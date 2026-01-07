from rich.console import Console
from rich.logging import RichHandler
import logging

def setup_logger():
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    return logging.getLogger("rich")

console = Console()
