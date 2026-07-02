import streamlit as st
from ui.main_page import main_page
from ui.login_page import login_page

# Load CSS file
def load_css(path='styles\\styles.css') -> None:
    with open(path) as css_file:
        st.markdown(f'<style>{css_file.read()}</style>', unsafe_allow_html=True)

# Main
def main() -> None:
    st.set_page_config(layout='wide')
    load_css()
    st.session_state.setdefault('client', None)

    if st.session_state.client:
        main_page()
    else:
        login_page()

if __name__ == '__main__':
    main()