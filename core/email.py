from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Email:
    sender: str
    subject: str
    date: Optional[datetime]
    content: str = ""

    @property
    def formatted_date(self) -> str:
        return self.date.strftime('%m/%d/%Y') if self.date else '--/--/----'

    @property
    def formatted_time(self) -> str:
        return self.date.strftime('%H:%M') if self.date else '--:--'

    @classmethod
    def from_parsed(self, data: dict) -> 'Email':
        return Email(
            sender=Email._extract_sender(data.get('From')),
            subject=data.get('Subject') or '(No subject)',
            date=data.get('Date'),
            content=data.get('Content', '')
        )

    @staticmethod
    def _extract_sender(from_field) -> str:
        if isinstance(from_field, list) and from_field:
            name, address = from_field[0]
            return name or address or 'Unknown sender'
        if isinstance(from_field, tuple) and from_field:
            name, address = from_field
            return name or address or 'Unknown sender'
        return str(from_field) if from_field else 'Unknown sender'