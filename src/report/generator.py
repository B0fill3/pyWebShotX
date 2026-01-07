import os
from jinja2 import Environment, FileSystemLoader
from typing import List, Dict, Any
from src.utils.logger import console

class ReportGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def generate(self, results: List[Dict[str, Any]]):
        """Generates the HTML report from the results."""
        template = self.env.get_template('report.html')
        
        html_content = template.render(results=results)
        
        output_path = os.path.join(self.output_dir, 'report.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        console.print(f"[bold green]Report successfully generated at: {output_path}[/bold green]")