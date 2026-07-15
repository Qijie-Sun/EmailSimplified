from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Email:
    sender: str
    address: str
    subject: str
    date: Optional[datetime]
    content: str = ''
    html_content: str = ''

    @property
    def sender_and_address(self) -> str:
        if self.address and self.address != self.sender:
            return f"{self.sender} ({self.address})"
        return self.sender

    @property
    def formatted_date(self) -> str:
        return self.date.strftime('%m/%d/%Y') if self.date else '--/--/----'

    @property
    def formatted_time(self) -> str:
        return self.date.strftime('%H:%M') if self.date else '--:--'

    @classmethod
    def from_parsed(self, data: dict) -> 'Email':
        sender, address = self._extract_sender(data.get('From'))
        return Email(
            sender=sender or address or 'Unknown',
            address=address or '',
            subject=data.get('Subject') or '(No subject)',
            date=data.get('Date'),
            content=data.get('Content', ''),
            html_content=data.get("HTML", "")
        )

    @staticmethod
    def _extract_sender(from_field) -> tuple[str, str]:
        if isinstance(from_field, list) and from_field:
            sender, address = from_field[0]
            return sender or '', address or ''
        if isinstance(from_field, tuple) and from_field:
            sender, address = from_field
            return sender or '', address or ''
        return str(from_field) if from_field else '', ''