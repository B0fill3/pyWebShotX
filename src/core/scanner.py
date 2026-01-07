import asyncio
import webtech
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor
from src.utils.logger import console

class TechScanner:
    def __init__(self):
        # Initialize webtech. We can configure options here if needed.
        try:
            self.wt = webtech.WebTech(options={'json': True, 'random_user_agent': True})
        except Exception as e:
            console.print(f"[yellow]Warning initializing WebTech: {e}[/yellow]")
            self.wt = None

    def _scan_sync(self, url: str) -> Dict[str, Any]:
        """Executes the scan synchronously."""
        if not self.wt:
            return {}
        
        # Ensure protocol
        if not url.startswith("http"):
            target_url = f"http://{url}"
        else:
            target_url = url

        try:
            # start_from_url returns a dictionary with detected technologies
            report = self.wt.start_from_url(target_url, timeout=10)
            return report
        except Exception as e:
            # console.print(f"[red]Error scanning {url}: {e}[/red]")
            return {"error": str(e)}

    async def detect(self, url: str) -> List[str]:
        """Executes the scan asynchronously using a ThreadPool."""
        loop = asyncio.get_running_loop()
        try:
            # Run the synchronous function in an executor
            result = await loop.run_in_executor(None, self._scan_sync, url)
            
            techs = []
            if "tech" in result:
                for tech in result["tech"]:
                    techs.append(tech["name"]) # Extract only the name
            return techs
        except Exception:
            return []