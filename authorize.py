import streamlit as st
import pandas as pd
import random

# Page config
st.set_page_config(
    page_title="Multi-Domain Intelligence Platform",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Company name / title
st.title("Multi-Domain Intelligence Platform")
st.markdown("---")

# Initialize session state
if "users" not in st.session_state:
    st.session_state.users = {
        "admin": "admin",  # default account
        "user": "123456"
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# If logged in → show dashboard
if st.session_state.logged_in:
    st.success(f"Logged in as **{st.session_state.username}**")

    # Sidebar logout
    with st.sidebar:
        st.image("https://via.placeholder.com/200x200.png?text=Logo", width=150)
        st.write(f"**User:** {st.session_state.username}")
        if st.button("Logout", type="primary"):
            st.session_state.logged_in = False
            st.rerun()

    # Initialize dummy data
    if "cyber_incidents" not in st.session_state:
        st.session_state.cyber_incidents = [
            {"title": "Phishing Campaign", "severity": "High", "status": "In Progress"},
            {"title": "DDoS Attack", "severity": "Critical", "status": "Resolved"},
        ]

    if "datasets" not in st.session_state:
        st.session_state.datasets = [
            {"name": "Customer Data 2025", "category": "Sensitive", "size_gb": 45.8},
        ]

    if "it_tickets" not in st.session_state:
        st.session_state.it_tickets = [
            {"title": "Server Down", "priority": "High", "status": "Open"},
        ]

    # Domain tabs
    tab_cyber, tab_data, tab_it = st.tabs(["Cybersecurity", "Data Science", "IT Operations"])

    # Cybersecurity tab
    with tab_cyber:
        st.subheader("Cybersecurity Overview")
        c1, c2, c3 = st.columns(3)
        c1.metric("Threats Detected", random.randint(200, 300), delta=random.randint(-10, 30))
        c2.metric("Active Incidents", len([i for i in st.session_state.cyber_incidents if i["status"] != "Resolved"]),
                  delta=-1)
        c3.metric("Vulnerabilities", random.randint(5, 15), delta=random.choice([-2, 2]))

        st.bar_chart(
            pd.DataFrame({
                "Threat Type": ["Malware", "Phishing", "DDoS", "Ransomware"],
                "Count": [89, 67, 45, 32]
            }).set_index("Threat Type")
        )

        st.subheader("Cyber Incidents")
        if st.session_state.cyber_incidents:
            st.dataframe(st.session_state.cyber_incidents, use_container_width=True)

        with st.expander("➕ Add New Incident"):
            with st.form("new_incident_form"):
                title = st.text_input("Incident Title", key="new_incident_title")
                severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"], key="new_incident_sev")
                status = st.selectbox("Status", ["Open", "In Progress", "Resolved"], key="new_incident_status")
                submitted = st.form_submit_button("Add Incident")
                if submitted and title:
                    st.session_state.cyber_incidents.append({
                        "title": title,
                        "severity": severity,
                        "status": status
                    })
                    st.success("Incident added")
                    st.rerun()

    # Data Science tab
    with tab_data:
        st.subheader("Data Science & ML")
        d1, d2, d3 = st.columns(3)
        d1.metric("Accuracy", "94.2%", "2.1%")
        d2.metric("Precision", "91.8%")
        d3.metric("Recall", "89.5%")

        st.line_chart(pd.DataFrame({
            "epoch": range(1, 11),
            "training_loss": [0.8, 0.6, 0.45, 0.32, 0.24, 0.20, 0.18, 0.16, 0.14, 0.12],
            "val_accuracy": [78, 82, 85, 88, 90, 91, 92, 93, 94, 94.5]
        }).set_index("val_accuracy"))

        st.subheader("Datasets")
        if st.session_state.datasets:
            st.dataframe(st.session_state.datasets, use_container_width=True)

    # IT Operations tab
    with tab_it:
        st.subheader("IT Operations")
        i1, i2, i3 = st.columns(3)
        i1.metric("CPU Usage", "67%", "+5%")
        i2.metric("Memory Usage", "8.2 GB", "+0.3 GB")
        i3.metric("Uptime", "99.8%", "0.1%")

        st.subheader("IT Tickets")
        if st.session_state.it_tickets:
            st.dataframe(st.session_state.it_tickets, use_container_width=True)

        with st.expander("➕ Create New Ticket"):
            with st.form("new_ticket"):
                title = st.text_input("Issue", key="new_ticket_title")
                priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], key="new_ticket_priority")
                submitted = st.form_submit_button("Create")
                if submitted and title:
                    st.session_state.it_tickets.append({"title": title, "priority": priority, "status": "Open"})
                    st.success("Ticket created")
                    st.rerun()

# Not logged in → show login/register tabs
else:
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")

        show_pass_login = st.checkbox("Show password", key="login_showpass")
        pass_type_login = "text" if show_pass_login else "password"
        password = st.text_input("Password", type=pass_type_login, key="login_password")

        if st.button("Log in", type="primary", use_container_width=True):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    with tab_register:
        st.subheader("Create Account")
        new_username = st.text_input("Choose username", key="register_username")

        show_pass_reg = st.checkbox("Show password", key="register_showpass")
        pass_type_reg = "text" if show_pass_reg else "password"

        new_password = st.text_input("Password", type=pass_type_reg, key="register_password")
        confirm_password = st.text_input("Confirm password", type=pass_type_reg, key="register_confirm")

        if st.button("Create account", type="primary", use_container_width=True):
            if not new_username or not new_password:
                st.warning("Please fill all fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif new_username in st.session_state.users:
                st.error("Username already exists")
            else:
                st.session_state.users[new_username] = new_password
                st.success("Account created successfully! Go to Login tab")
                st.balloons()