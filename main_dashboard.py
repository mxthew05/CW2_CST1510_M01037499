import streamlit as st
import pandas as pd
import plotly.express as px
from app.data.incidents import get_all_incidents, insert_incident, update_incident_status, delete_incident
from app.data.datasets import get_all_datasets
from app.data.tickets import get_all_tickets
from app.data.db import connect_database

def show_dashboard():
    st.title("📊 Multi-Domain Intelligence Dashboard")
    st.caption(f"Welcome, {st.session_state.username}! Logged in on {pd.Timestamp.now().date()}")

    st.sidebar.header("Navigation")
    domain = st.sidebar.radio("Select Domain", ["Cybersecurity", "Data Science", "IT Operations"])

    if domain == "Cybersecurity":
        show_cyber_dashboard()
    elif domain == "Data Science":
        show_data_science_dashboard()
    elif domain == "IT Operations":
        show_it_operations_dashboard()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

def show_cyber_dashboard():
    st.header("Cybersecurity Incidents")
    df = get_all_incidents()

    # Layout with columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Incidents by Type (Plotly Bar)")
        fig = px.bar(df.groupby("incident_type").size().reset_index(name="Count"),
                     x="incident_type", y="Count", color="incident_type")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Severity Distribution (Plotly Pie)")
        fig = px.pie(df, names="severity", title="Severity Levels")
        st.plotly_chart(fig, use_container_width=True)

    # CRUD Form
    with st.expander("Manage Incidents"):
        st.subheader("Create New Incident")
        with st.form("new_incident"):
            date = st.date_input("Date")
            inc_type = st.selectbox("Type", ["Phishing", "Malware", "DDoS"])
            severity = st.selectbox("Severity", ["Low", "Medium", "High"])
            status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
            desc = st.text_area("Description")
            submit = st.form_submit_button("Create")
            if submit:
                insert_incident(str(date), inc_type, severity, status, desc, st.session_state.username)
                st.success("Incident created!")
                st.rerun()

        # Update/Delete
        if not df.empty:
            selected_id = st.selectbox("Select Incident to Update/Delete", df["id"])
            new_status = st.selectbox("New Status", ["Open", "In Progress", "Resolved"])
            if st.button("Update Status"):
                update_incident_status(selected_id, new_status)
                st.success("Status updated!")
                st.rerun()
            if st.button("Delete Incident"):
                delete_incident(selected_id)
                st.success("Incident deleted!")
                st.rerun()

    # Data Table
    st.subheader("All Incidents")
    st.dataframe(df)

def show_data_science_dashboard():
    st.header("Data Science Datasets")
    df = get_all_datasets()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Datasets by Size (Plotly Scatter)")
        fig = px.scatter(df, x="created_date", y="size_mb", color="format", size="size_mb")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Formats Distribution (Built-in Bar)")
        st.bar_chart(df["format"].value_counts())

    st.subheader("All Datasets")
    st.dataframe(df)

def show_it_operations_dashboard():
    st.header("IT Operations Tickets")
    df = get_all_tickets()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Tickets by Priority (Plotly Bar)")
        fig = px.bar(df.groupby("priority").size().reset_index(name="Count"),
                     x="priority", y="Count", color="priority")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Status Distribution (Built-in Area)")
        st.area_chart(df["status"].value_counts())

    st.subheader("All Tickets")
    st.dataframe(df)