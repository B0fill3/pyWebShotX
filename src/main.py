import typer
import asyncio
import os
import webbrowser
import signal
from typing import List
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

from src.core.screenshot import ScreenshotManager
from src.core.scanner import TechScanner
from src.report.generator import ReportGenerator

app = typer.Typer(add_completion=False)
console = Console()

async def process_url(url: str, screenshot_manager: ScreenshotManager, scanner: TechScanner, progress, task_id, run_detection: bool):
    """Processes an individual URL: screenshot and scan."""
    # Clean URL (remove whitespace, newlines)
    url = url.strip()
    if not url:
        progress.advance(task_id)
        return None

    # Execute screenshot first to get the final URL
    screenshot_result = await screenshot_manager.capture(url)
    
    techs = []
    if run_detection:
        # Determine which URL to scan for technologies
        scan_url = screenshot_result.get("final_url") or url
        # Run tech detection on the final URL
        techs = await scanner.detect(scan_url)

    # Combine results
    result = screenshot_result
    result["techs"] = techs
    
    # Update progress bar
    progress.advance(task_id)
    return result

async def main_async(input_file: str, output_dir: str, concurrency: int, open_results: bool, run_detection: bool, timeout: int):
    # Initial validations
    if not os.path.exists(input_file):
        console.print(f"[bold red]Error: The file {input_file} does not exist.[/bold red]")
        return

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read domains
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        console.print("[yellow]The input file is empty.[/yellow]")
        return

    console.print(f"[bold green]Starting scan of {len(urls)} targets with concurrency {concurrency}...[/bold green]")

    # Optimize thread pool for tech detection to match concurrency
    loop = asyncio.get_running_loop()
    loop.set_default_executor(ThreadPoolExecutor(max_workers=concurrency))

    # Initialize components
    screenshot_manager = ScreenshotManager(output_dir, concurrency, timeout)
    scanner = TechScanner()
    report_generator = ReportGenerator(output_dir)

    await screenshot_manager.start()

    results = []
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task_id = progress.add_task("[cyan]Processing...", total=len(urls))
            
            # Create a Queue and populate it
            queue = asyncio.Queue()
            for url in urls:
                queue.put_nowait(url)

            # Worker function
            async def worker():
                while True:
                    try:
                        # Get URL from queue non-blocking (since we pre-filled it)
                        current_url = queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
                    
                    try:
                        res = await process_url(current_url, screenshot_manager, scanner, progress, task_id, run_detection) # Pass timeout here if needed in process_url
                        if res:
                            results.append(res)
                    except Exception:
                        pass
                    finally:
                        queue.task_done()

            # Create workers based on concurrency
            workers = [asyncio.create_task(worker()) for _ in range(concurrency)]
            
            # Wait for all workers to finish
            await asyncio.gather(*workers)

    finally:
        await screenshot_manager.stop()

    # Generate report
    console.print("[bold cyan]Generating report...[/bold cyan]")
    report_generator.generate(results)
    
    report_path = os.path.join(output_dir, 'report.html')
    if open_results:
        console.print(f"[bold blue]Opening report in browser: {report_path}[/bold blue]")
        webbrowser.open(f"file://{os.path.abspath(report_path)}")

    console.print("[bold green]Process completed![/bold green]")

@app.command()
def scan(
    input_file: str = typer.Option(..., "--input", "-i", help="Path to the file with the list of subdomains."),
    output_dir: str = typer.Option("output", "--output", "-o", help="Directory where results will be saved."),
    concurrency: int = typer.Option(30, "--concurrency", "-c", help="Number of simultaneous tabs."),
    results: bool = typer.Option(False, "--results", "-r", help="Open the report in the default browser after scanning."),
    detection: bool = typer.Option(False, "--detection", "-d", help="Enable technology stack detection."),
    timeout: int = typer.Option(5, "--timeout", "-t", help="Timeout in seconds for each request.")
):
    """
    Scans subdomains, takes screenshots, and optionally detects technologies.
    """
    def force_exit(signum, frame):
        console.print("\n[bold red]Scan interrupted by user. Exiting...[/bold red]")
        os._exit(1)

    signal.signal(signal.SIGINT, force_exit)

    try:
        asyncio.run(main_async(input_file, output_dir, concurrency, results, detection, timeout))
    except Exception:
        pass

if __name__ == "__main__":
    app()