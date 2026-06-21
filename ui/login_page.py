import streamlit as st
from core.imap_handler import Client

def login_page() -> None:
    _, center, _ = st.columns([1, 1, 1])
    with center:
        st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)
        email = st.text_input("Enter Gmail address")
        password = st.text_input("Enter app password", type="password")
        st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

        if st.button("Login", use_container_width=True):
            client = Client(email, password).connect()
            if client:
                st.session_state.client = client
                st.rerun()