from flask import render_template

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Template():
    uuid: str
    title: str
    description: str
    category: str
    date: datetime
    path: str

    def render_html(self) -> str:
        html = render_template(
            'elements/doc_template.html', 
            uuid=self.uuid, 
            title=self.title, 
            description=self.description, 
            date=self.date,
            category=self.category)
        return html
    
    def date_str(self, format='%d/%m/%Y'):
        return self.date.strftime(format)