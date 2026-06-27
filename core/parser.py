import mailparser
from lxml import html

# Strip styles and return plain text
def extract_visible_text(html_content):
    tree = html.fromstring(html_content)
    html.etree.strip_elements(tree, 'script', 'style', 'head', 'title', 'meta', with_tail=False)
    text = tree.text_content()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split('  '))
    return '\n'.join(chunk for chunk in chunks if chunk)

# Extract details of emails
def parse(imap, ids):
    id_bytes = ids
    status, msg_data = imap.fetch(id_bytes, '(RFC822)')
    raw_emails = []
    for i in range(0, len(msg_data), 2):
        if isinstance(msg_data[i], tuple):
            raw_emails.append(msg_data[i][1])

    def parse_single(raw_email):
        parsed = mailparser.parse_from_bytes(raw_email)

        if parsed.text_plain:
            clean_text = '\n'.join(parsed.text_plain)
        elif parsed.text_html:
            html_content = '\n'.join(parsed.text_html)
            clean_text = extract_visible_text(html_content)
        else:
            clean_text = '[No readable content found]'

        return {
            'From': parsed.from_,
            'Subject': parsed.subject,
            'Date': parsed.date,
            'Content': clean_text
        }

    return parse_single(raw_emails[0])