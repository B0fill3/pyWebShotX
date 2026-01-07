import typer
import asyncio
import os
import webbrowser
from typing import List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

from src.core.screenshot import ScreenshotManager
from src.core.scanner import TechScanner
from src.report.generator import ReportGenerator

app = typer.Typer(add_completion=False)
console = Console()

async def process_url(url: str, screenshot_manager: ScreenshotManager, scanner: TechScanner, progress, task_id):
    """Processes an individual URL: screenshot and scan."""
    # Clean URL (remove whitespace, newlines)
    url = url.strip()
    if not url:
        progress.advance(task_id)
        return None

    # Execute screenshot first to get the final URL
    screenshot_result = await screenshot_manager.capture(url)
    
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

async def main_async(input_file: str, output_dir: str, concurrency: int, open_results: bool):
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

    # Initialize components
    screenshot_manager = ScreenshotManager(output_dir, concurrency)
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
            
            # Create tasks
            tasks = [
                process_url(url, screenshot_manager, scanner, progress, task_id)
                for url in urls
            ]
            
            # Execute all
            results = await asyncio.gather(*tasks)
            
            # Filter null results (empty lines)
            results = [r for r in results if r is not None]

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
    concurrency: int = typer.Option(5, "--concurrency", "-c", help="Number of simultaneous tabs."),
    results: bool = typer.Option(False, "--results", "-r", help="Open the report in the default browser after scanning.")
):
    """
    Scans subdomains, takes screenshots, and detects technologies.
    """
    asyncio.run(main_async(input_file, output_dir, concurrency, results))

if __name__ == "__main__":
    app()