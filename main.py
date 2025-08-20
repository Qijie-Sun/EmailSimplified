import imaplib
import getpass
import mailparser
from lxml import html
import streamlit as st

# Hide "Press Enter to apply" text on inputs
st.markdown(
    """
    <style>
    div[data-testid="InputInstructions"] > span:nth-child(1) {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def login(email, password):
    imap = imaplib.IMAP4_SSL('imap.gmail.com')
    try:
        imap.login(email, password)
    except imaplib.IMAP4.error:
        st.error('Login failed. Please check your credentials.')
        exit()
    return imap

def fetch_emails(imap, category, limit):
    imap.select('inbox')
    status, messages = imap.search(None, 'X-GM-RAW', 'category:' + category)
    if status != 'OK':
        st.error('Failed to retrieve emails.')
        return []
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

# streamlit run main.py
def main():
    st.title("Gmail Reader")

    if "imap" not in st.session_state:
        st.session_state.imap = None
        st.session_state.email = ""
        st.session_state.password = ""

    if not st.session_state.imap:
        st.session_state.email = st.text_input("Enter Gmail address", value=st.session_state.email)
        st.session_state.password = st.text_input("Enter app password", type="password")
        if st.button("Login"):
            st.session_state.imap = login(st.session_state.email, st.session_state.password)
    else:
        category_options = {
            "All": "",
            "Primary": "primary",
            "Promotions": "promotions",
            "Social": "social",
            "Updates": "updates"
        }

        category = st.selectbox("Select Gmail category", list(category_options.keys()))
        num_emails = st.slider("Number of emails to fetch", min_value=1, max_value=10, value=3)

        if st.button("Fetch Emails"):
            email_ids = fetch_emails(st.session_state.imap, category_options[category], num_emails)
            if email_ids:
                st.success(f"Fetched {len(email_ids)} emails.")
                for id in reversed(email_ids):
                    parsed_email = parse(st.session_state.imap, id)
                    st.markdown("---")
                    st.write(f"**From:** {parsed_email['From']}")
                    st.write(f"**Subject:** {parsed_email['Subject']}")
                    st.write(f"**Date:** {parsed_email['Date']}")
                    st.markdown(parsed_email['Content'])
            else:
                st.info("No emails found.")

if __name__ == "__main__":
    main()