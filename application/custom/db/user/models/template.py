from flask import render_template

from dataclasses import dataclass, field, asdict
from datetime import date


@dataclass
class Template:
    uuid: str
    title: str
    description: str
    category: str
    path: str
    creation_date: date = field(default_factory=date.today)

    def __post_init__(self) -> None:
        # Convert creation_date to a date object if is string
        if isinstance(self.creation_date, str):
            self.creation_date = date.fromisoformat(self.creation_date)

    dict = asdict

    def values(self) -> tuple[str]:
        return (self.uuid, self.title, self.description, self.category, self.path, self.date_str())

    def render_html(self) -> str:
        """Create html template object

        Returns:
            str: The html object
        """

        html = render_template(
            'elements/template.html', 
            uuid=self.uuid, 
            title=self.title, 
            description=self.description,   
            date=self.date_str(),
            category=self.category)
        return html
    
    def date_str(self):
        return self.creation_date.isoformat()