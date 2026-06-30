import streamlit as st
import html
from datetime import datetime
from core.email import Email
from core.parser import parse

category_options = {
    'All': '',
    'Primary': 'primary',
    'Promotions': 'promotions',
    'Social': 'social',
    'Updates': 'updates'
}

def horizontal_separator() -> None:
    st.markdown('<div style="border-top:1px solid grey; width:100%;"></div>', unsafe_allow_html=True)

def vertical_separator() -> None:
    st.markdown('<div style="border-left:1px solid grey; height:100vh;"></div>', unsafe_allow_html=True)

def render_email_card(email: Email) -> None:
    sender = html.escape(email.sender)
    subject = html.escape(email.subject)
    st.markdown(f"""
        <div class="email-card">
            <div class="email-row">
                <span class="email-sender">{sender}</span>
                <span class="email-date">{email.formatted_date}</span>
            </div>
            <div class="email-row">
                <span class="email-subject">{subject}</span>
                <span class="email-time">{email.formatted_time}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def get_emails(category: str, limit: int) -> list[Email]:
    cache_key = (category, limit)
    if st.session_state.get('_emails_cache_key') != cache_key:
        client = st.session_state.client
        email_ids = client.fetch_email_ids(category, limit)
        emails = []
        for email_id in email_ids:
            data = parse(client.imap, email_id)
            if data:
                emails.append(Email.from_parsed(data))
        emails.sort(key=lambda e: e.date or datetime.min, reverse=True)
        st.session_state._emails_cache_key = cache_key
        st.session_state._emails_cache = emails
    return st.session_state._emails_cache

def main_page() -> None:
    category_col, number_col, search_col, logout_col = st.columns([2, 1, 6, 1])
    with category_col:
        category = st.selectbox('Category', list(category_options.keys()))
    with number_col:
        num_emails = st.number_input('Number', min_value=1, max_value=1000, value=10)
    with search_col:
        query = st.text_input('Search')
    with logout_col:
        st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
        if st.button('Logout', use_container_width=True):
            st.session_state.client = None
            st.rerun()
    horizontal_separator()

    left_col, separator_col, right_col = st.columns([3, 0.05, 7])
    with left_col:
        st.markdown("#### Themes")
        horizontal_separator()

        st.markdown("#### Emails")
        emails = get_emails(category_options[category], num_emails)
        for i, email in enumerate(emails):
            with st.container(key=f"email_card_{i}"):
                render_email_card(email)
                if st.button("", key=f"email_select_{i}", use_container_width=True):
                    st.session_state.selected_email = email
                    st.rerun()
    with separator_col:
        vertical_separator()
    with right_col:
        st.markdown("#### Selected Emails")
        selected = st.session_state.get("selected_email")
        if selected:
            st.write(selected.sender)
            st.write(selected.subject)
            st.write(selected.content)
