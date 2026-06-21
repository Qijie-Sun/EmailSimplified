import streamlit as st
import imaplib

class Client:
    def __init__(self, email: str, password: str) -> None:
        self.email = email
        self.password = password
        self.imap: None

    def connect(self) -> 'Client':
        self.imap = imaplib.IMAP4_SSL('imap.gmail.com')
        try:
            self.imap.login(self.email, self.password)
            self.imap.select('inbox')
        except imaplib.IMAP4.error:
            st.error('Invalid email or password')
            return None
        return self