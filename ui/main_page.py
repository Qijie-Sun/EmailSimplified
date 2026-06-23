import streamlit as st

category_options = {
    'All': '',
    'Primary': 'primary',
    'Promotions': 'promotions',
    'Social': 'social',
    'Updates': 'updates'
}

def main_page() -> None:
    placeholder_col, logout_col = st.columns([9, 1])
    with placeholder_col:
        st.markdown('### Placeholder')
    with logout_col:
        st.markdown('<div style="margin-top: 28px;"></div>', unsafe_allow_html=True)
        if st.button('Logout', use_container_width=True):
            st.session_state.client = None
            st.rerun()
    st.divider()

    left_col, separator_col, right_col = st.columns([3, 0.05, 7])
    with left_col:
        category_col, number_col = st.columns([2, 1])
        with category_col:
            category = st.selectbox('Category', list(category_options.keys()))
        with number_col:
            num_emails = st.number_input('Number', min_value=1, max_value=1000, value=50)
        st.divider()

        st.markdown("#### Themes")
        st.divider()

        st.markdown("#### Emails")
        for i in range(5):
            st.button(f"Email {i+1}", use_container_width=True)
    with separator_col:
        st.markdown('<div style="border-left:1px solid grey; height:100vh;"></div>', unsafe_allow_html=True)
    with right_col:
        st.markdown("#### Selected Emails")
