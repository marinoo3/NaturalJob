from flask import render_template

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Template:
    uuid: str
    title: str
    description: str
    category: str
    path: str
    date: datetime = field(default_factory=datetime.today)

    def values(self) -> tuple[str]:
        return (self.uuid, self.title, self.description, self.category, self.path, self.date_str())

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