import asyncio
from playwright.async_api import async_playwright, Page, BrowserContext
from typing import Dict, Any, Optional
import os
from src.utils.logger import console

class ScreenshotManager:
    def __init__(self, output_dir: str, concurrency: int = 5, timeout: int = 5):
        self.output_dir = output_dir
        self.concurrency = concurrency
        self.timeout = timeout * 1000 # Convert to ms for Playwright
        self.semaphore = asyncio.Semaphore(concurrency)
        self.browser = None
        self.context = None
        self.playwright = None

    async def start(self):
        """Starts the browser."""
        self.playwright = await async_playwright().start()
        # We use chromium, but it can be changed. Headless=True is default.
        self.browser = await self.playwright.chromium.launch()
        # Create a context with a reasonable viewport
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 800},
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

    async def stop(self):
        """Closes the browser."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception:
            pass

    async def capture(self, url: str) -> Dict[str, Any]:
        """Takes a screenshot of the given URL and extracts metadata."""
        async with self.semaphore:
            page = None
            result = {
                "url": url,
                "screenshot_path": None,
                "title": "",
                "status": 0,
                "error": None,
                "final_url": None
            }
            
            # Ensure protocol
            if not url.startswith("http"):
                target_url = f"http://{url}" # Try http first, or whatever logic you prefer
            else:
                target_url = url

            filename = target_url.replace("://", "_").replace("/", "_").replace(":", "_") + ".png"
            filepath = os.path.join(self.output_dir, filename)

            try:
                page = await self.context.new_page()
                
                # Navigate
                # We use wait_until="networkidle" to ensure redirects are followed
                response = await page.goto(target_url, timeout=self.timeout, wait_until="networkidle")
                
                if response:
                    # Logic to get the FIRST status code (e.g., 301/302) instead of the final 200
                    # We traverse back the redirect chain
                    first_response = response
                    request_chain = response.request
                    while request_chain.redirected_from:
                        request_chain = request_chain.redirected_from
                        chain_response = await request_chain.response()
                        if chain_response:
                            first_response = chain_response
                    
                    result["status"] = first_response.status
                    result["title"] = await page.title()
                    result["final_url"] = response.url
                
                # Capture
                await page.screenshot(path=filepath, full_page=False)
                result["screenshot_path"] = filename # Save relative path for the report
                
            except Exception as e:
                result["error"] = str(e)
                # console.print(f"[red]Error capturing {url}: {e}[/red]")
            finally:
                if page:
                    await page.close()
            
            return result