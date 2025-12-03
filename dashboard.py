import streamlit as st
from app.dashboard.login import show_login_page
from app.dashboard.main_dashboard import show_dashboard
from app.dashboard.utils import check_login

st.set_page_config(page_title="Intelligence Platform", layout="wide")

if not check_login():
    show_login_page()
else:
    show_dashboard()
