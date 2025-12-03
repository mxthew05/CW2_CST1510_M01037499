import streamlit as st
from app.dashboard.utils import perform_login

def show_login_page():
    st.title("🔐 Login to Multi-Domain Intelligence Platform")
    st.markdown("Secure login required to access the dashboard.")

    with st.form(key="login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        perform_login(username, password)