import imaplib
import mailparser
from lxml import html
import streamlit as st
from concurrent.futures import ThreadPoolExecutor

import grouping

def load_css(file_path="styles.css"):
    with open(file_path) as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def login(email, password):
    imap = imaplib.IMAP4_SSL('imap.gmail.com')
    try:
        imap.login(email, password)
        imap.select('inbox')
    except imaplib.IMAP4.error:
        st.error('Login failed. Please check your credentials.')
        exit()
    return imap

def fetch_emails(imap, category, limit):
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

def parse(imap, ids):
    if isinstance(ids, (list, tuple)):
        id_bytes = b','.join(ids)
        batch = True
    else:
        id_bytes = ids
        batch = False
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

    if batch:
        with ThreadPoolExecutor(max_workers=8) as executor:
            return list(executor.map(parse_single, raw_emails))

    return parse_single(raw_emails[0])

# streamlit run main.py
def main():
    st.set_page_config(layout="wide")
    load_css()
    st.title("Email Simplified")

    if "imap" not in st.session_state:
        st.session_state.imap = None
        st.session_state.email = ""
        st.session_state.password = ""

    if not st.session_state.imap:
        st.session_state.email = st.text_input("Enter Gmail address", value=st.session_state.email)
        st.session_state.password = st.text_input("Enter app password", type="password")
        if st.button("Login"):
            if not st.session_state.email or not st.session_state.password:
                st.error("Please enter both email and password")
            else:
                st.session_state.imap = login(st.session_state.email, st.session_state.password)
                st.rerun()
        return
    
    category_options = {
        "All": "",
        "Primary": "primary",
        "Promotions": "promotions",
        "Social": "social",
        "Updates": "updates"
    }

    # TODO: clean up column formattings
    col1, col2, col3, col4 = st.columns([2, 1, 4, 1])
    with col1:
        category = st.selectbox("Category", list(category_options.keys()))
    with col2:
        num_emails = st.selectbox("Number",options=[10, 20, 50, 100], index=1)
    with col4:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button('Logout', use_container_width=True):
            st.session_state.imap = None
            st.rerun()

    email_ids = fetch_emails(st.session_state.imap, category_options[category], num_emails)
    if email_ids:
        parsed_emails = parse(st.session_state.imap, email_ids)
        grouped_emails = grouping.group_emails_by_theme(parsed_emails)
    else:
        st.info("No emails found.")

    themes_col, main_col = st.columns([1, 4])
    with themes_col:
        st.markdown("### Themes")
        theme_options = ["All"] + list(grouped_emails.keys())

        selected_theme = st.radio(
            "Email Groups",
            theme_options,
            label_visibility="collapsed",
        )
    with main_col:
        if selected_theme != "All":
            parsed_emails = grouped_emails.get(selected_theme, [])
        for parsed_email in reversed(parsed_emails):
            sender = parsed_email['From']
            if isinstance(sender, list) and sender:
                sender = sender[0][0] or sender[0][1]
            sender_limit = 20
            if len(sender) > sender_limit:
                sender = sender[:sender_limit - 3] + "..."

            subject = parsed_email['Subject'] or "(No Subject)"
            subject_limit = 80
            if len(subject) > subject_limit:
                subject = subject[:subject_limit - 3] + "..."

            date = str(parsed_email['Date']).split()[0]
            y, m, d = date.split("-")
            date = f"{m}/{d}/{y}"

            col_5, col_6 = st.columns([9, 1])
            with col_5:
                st.markdown(f"**{sender}** — {subject}")
            with col_6:
                st.markdown(f"{date}")

            with st.expander("Contents"):
                st.write(f"**From:** {parsed_email['From']}")
                st.write(f"**Subject:** {parsed_email['Subject']}")
                st.write(f"**Date:** {parsed_email['Date']}")
                st.markdown(parsed_email['Content'])

if __name__ == "__main__":
    main()