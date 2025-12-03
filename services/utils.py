import streamlit as st
from app.services.user_service import login_user

def check_login():
    """Check if user is logged in via session state."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    return st.session_state.logged_in

def perform_login(username, password):
    """Perform login and set session state."""
    success, msg = login_user(username, password)
    if success:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.success(msg)
        st.rerun()  # Refresh to show dashboard
    else:
        st.error(msg)