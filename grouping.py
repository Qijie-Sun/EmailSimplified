from collections import defaultdict
import re

THEMES = [
    "Shopping",
    "Finance",
    "Social"
]

THEME_KEYWORDS = {
    "Shopping": [
        "order", "receipt", "shipping", "delivery", "purchase", "invoice"
    ],
    "Finance": [
        "bank", "statement", "payment", "credit", "debit", "balance"
    ],
    "Social": [
        "friend", "follower", "liked", "commented", "mentioned"
    ]
}


def classify_email(email):
    text = f"{email.get('Subject', '')} {email.get('Content', '')}".lower()

    for theme, keywords in THEME_KEYWORDS.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", text):
                return theme

    return "Other"

def group_emails_by_theme(emails):
    grouped = defaultdict(list)

    for email in emails:
        theme = classify_email(email)
        grouped[theme].append(email)

    return grouped