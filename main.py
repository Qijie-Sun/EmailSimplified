import imaplib
import getpass
import mailparser
from lxml import html

def login(email, password):
    imap = imaplib.IMAP4_SSL('imap.gmail.com')
    try:
        imap.login(email, password)
    except imaplib.IMAP4.error:
        print('Login failed. Please check your credentials.')
        exit()
    return imap

def select():
    options = {
        '1': '',
        '2': 'primary',
        '3': 'promotions',
        '4': 'social',
        '5': 'updates',
        '6': 'exit'
    }

    print('Select Gmail category:')
    for k, v in options.items():
        option = k + ': '
        if v:
            option += v.capitalize()
        else:
            option += 'All'
        print(option)

    while True:
        choice = input('Enter choice (1-6): ').strip()
        if choice in options:
            return options[choice]
        print('Invalid choice.')

def fetch_emails(imap, category, limit):
    imap.select('inbox')
    status, messages = imap.search(None, 'X-GM-RAW', 'category:' + category)
    if status != 'OK':
        print('Failed to retrieve emails.')
        exit()

    email_ids = messages[0].split()
    return email_ids[-limit:]

def extract_visible_text(html_content):
    tree = html.fromstring(html_content)
    html.etree.strip_elements(tree, 'script', 'style', 'head', 'title', 'meta', with_tail=False)
    text = tree.text_content()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return '\n'.join(chunk for chunk in chunks if chunk)

def parse(imap, id):
    status, msg_data = imap.fetch(id, '(RFC822)')
    raw_email = msg_data[0][1]
    parsed = mailparser.parse_from_bytes(raw_email)

    print('=' * 50)
    print(f'From: {parsed.from_}')
    print(f'Subject: {parsed.subject}')
    print(f'Date: {parsed.date}')

    if parsed.text_plain:
        clean_text = '\n'.join(parsed.text_plain)
    elif parsed.text_html:
        html_content = '\n'.join(parsed.text_html)
        clean_text = extract_visible_text(html_content)
    else:
        clean_text = '[No readable content found]'

    print(clean_text)


email = input('Enter email: ')
password = getpass.getpass('Enter app password: ')

imap = login(email, password)

category = select()
if category == 'exit':
    print('Exiting...')
    imap.logout()
    exit()
    
email_ids = fetch_emails(imap, category, 3)
for id in reversed(email_ids):
    parse(imap, id)

imap.logout()