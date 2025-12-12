import streamlit as st
import pandas as pd
import bcrypt
import sqlite3
from datetime import datetime
from openai import OpenAI
import os

# ====================== PAGE & LOGO ======================
st.set_page_config(page_title="Intelligence Platform", layout="wide", page_icon="Chart")

with st.sidebar:
    st.image("https://tse3.mm.bing.net/th/id/OIP.-xWpfRxoTxJmI9RySlX6SgHaHa?w=183&h=183&c=7&r=0&o=5&dpr=1.3&pid=1.7", width=180)
    st.markdown("---")
    
    page = st.radio("Navigation", [
        "Cybersecurity",
        "Data Science", 
        "IT Operations",
        "AI Assistant"
    ], index=0)

DATA_FOLDER = "DATA"

# ====================== DATABASE ======================
def init_db():
    with sqlite3.connect('intelligence_platform.db', timeout=30) as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)')
        c.execute('''
            CREATE TABLE IF NOT EXISTS cyber_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT, timestamp TEXT, severity TEXT,
                category TEXT, status TEXT, description TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id INTEGER, name TEXT, rows INTEGER,
                columns INTEGER, uploaded_by TEXT, upload_date TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS it_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER, priority TEXT, description TEXT,
                status TEXT, assigned_to TEXT, created_at TEXT,
                resolution_time_hours INTEGER
            )
        ''')

init_db()

# ====================== PASSWORD & OPENAI ======================
def hash_pw(pw): return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
def check_pw(pw, h): return bcrypt.checkpw(pw.encode(), h.encode())

try:
    client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY"))
    AI_READY = True
except:
    AI_READY = False

# ====================== DATABASE CLASS ======================
class DB:
    @staticmethod
    def add_user(u, p):
        try:
            with sqlite3.connect('intelligence_platform.db') as conn:
                c = conn.cursor()
                c.execute("INSERT INTO users (username,password_hash) VALUES (?,?)", (u, hash_pw(p)))
            return True
        except: return False

    @staticmethod
    def login(u, p):
        with sqlite3.connect('intelligence_platform.db') as conn:
            c = conn.cursor()
            c.execute("SELECT password_hash FROM users WHERE username=?", (u,)) 
            r = c.fetchone()
        return r and check_pw(p, r[0])

    @staticmethod
    def save_incident(data):
        with sqlite3.connect('intelligence_platform.db') as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO cyber_incidents 
                      (incident_id, timestamp, severity, category, status, description)
 VALUES (?,?,?,?,?,?)""",
                      (data['id'], data['time'], data['severity'], data['category'], "Open", data['desc']))

    @staticmethod
    def save_dataset(data):
        with sqlite3.connect('intelligence_platform.db') as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO datasets 
 (dataset_id, name, rows, columns, uploaded_by, upload_date)
 VALUES (?,?,?,?,?,?)""",
                      (data['id'], data['name'], data['rows'], data['cols'], data['by'], data['date']))

    @staticmethod
    def save_ticket(data):
        with sqlite3.connect('intelligence_platform.db') as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO it_tickets 
 (ticket_id, priority, description, status, assigned_to, created_at)
 VALUES (?,?,?,?,?,?)""",
                      (data['id'], data['priority'], data['desc'], "Open", data['to'], data['time']))

    @staticmethod
    def load_data():
        with sqlite3.connect('intelligence_platform.db', timeout=30) as conn:
            c = conn.cursor()
            for t in ["cyber_incidents", "datasets", "it_tickets"]:
                c.execute(f"DELETE FROM {t}")

            # FIXED: Now unpacks correctly (2 items: query and cols)
            files = {
                "cyber_incidents.csv": (
                    "INSERT INTO cyber_incidents VALUES (NULL,?,?,?,?,?,?)",
                    ['incident_id','timestamp','severity','category','status','description']
                ),
                "datasets_metadata.csv": (
                    "INSERT INTO datasets VALUES (NULL,?,?,?,?,?,?)",
                    ['dataset_id','name','rows','columns','uploaded_by','upload_date']
                ),
                "it_tickets.csv": (
                    "INSERT INTO it_tickets VALUES (NULL,?,?,?,?,?,?,?)",
                    ['ticket_id','priority','description','status','assigned_to','created_at','resolution_time_hours']
                )
            }

            for filename, data in files.items():
                query, cols = data  # Now correctly unpacks 2 values
                path = os.path.join(DATA_FOLDER, filename)
                try:
                    df = pd.read_csv(path, sep=',', on_bad_lines='skip', dtype=str)
                    df.columns = df.columns.str.strip()
                    for _, r in df.iterrows():
                        values = [r.get(col, "") for col in cols]
                        c.execute(query, values)
                    st.sidebar.success(f"Loaded {len(df)} ← {filename}")
                except Exception as e:
                    st.sidebar.error(f"{filename}: {e}")

    @staticmethod
    def get(table):
        with sqlite3.connect('intelligence_platform.db') as conn:
            return pd.read_sql_query(f"SELECT * FROM {table}", conn)

# Load data
if "data_loaded" not in st.session_state:
    with st.spinner("Loading data..."):
        DB.load_data()
        st.session_state.data_loaded = True

# ====================== LOGIN ======================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Multi-Domain Intelligence Platform")
    c1, c2 = st.columns(2)
    with c1:
        st.header("Login")
        u = st.text_input("Username", key="login_username")
        p = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", type="primary"):
            if DB.login(u, p):
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Wrong username/password")
    with c2:
        st.header("Register")
        nu = st.text_input("New Username", key="reg_username")
        np = st.text_input("New Password", type="password", key="reg_password")
        if st.button("Register"):
            if DB.add_user(nu, np):
                st.success("Account created!")
            else:
                st.error("Username taken")
else:
    st.sidebar.success(f"Logged in as: {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    # ====================== MAIN PAGES ======================
    if page == "Cybersecurity":
        st.header("Cybersecurity Threat Dashboard")
        with st.expander("Report New Incident", expanded=True):
            with st.form("incident_form"):
                col1, col2 = st.columns(2)
                with col1:
                    incident_id = st.text_input("Incident ID", value=f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
                    category = st.selectbox("Category", ["Malware", "Phishing", "DDoS", "Unauthorized Access", "Data Leak"])
                    severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
                with col2:
                    description = st.text_area("Description")
                    source_ip = st.text_input("Source IP", value="192.168.1.1")
                    assigned_to = st.text_input("Assign To", value=st.session_state.user)
                
                if st.form_submit_button("Submit Incident", type="primary"):
                    DB.save_incident({
                        'id': incident_id,
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'severity': severity,
                        'category': category,
                        'desc': description
                    })
                    st.success("Incident saved!")
                    st.rerun()

        df = DB.get("cyber_incidents")
        st.metric("Total Incidents", len(df))
        st.bar_chart(df["severity"].value_counts())
        st.dataframe(df)

    elif page == "Data Science":
        st.header("Data Science & ML Datasets Repository")
        with st.expander("Upload New Dataset", expanded=True):
            with st.form("dataset_form"):
                col1, col2 = st.columns(2)
                with col1:
                    ds_id = st.text_input("Dataset ID", value=str(int(datetime.now().timestamp())))
                    name = st.text_input("Dataset Name")
                with col2:
                    rows = st.number_input("Number of Rows", min_value=1, value=1000)
                    columns = st.number_input("Number of Columns", min_value=1, value=10)
                    upload_date = st.date_input("Upload Date", value=datetime.now().date())
                
                if st.form_submit_button("Upload Dataset", type="primary"):
                    DB.save_dataset({
                        'id': ds_id,
                        'name': name,
                        'rows': rows,
                        'cols': columns,
                        'by': st.session_state.user,
                        'date': str(upload_date)
                    })
                    st.success("Dataset saved!")
                    st.rerun()

        df = DB.get("datasets")
        st.metric("Total Rows", f"{pd.to_numeric(df['rows'], errors='coerce').sum():,}")
        st.dataframe(df)

    elif page == "IT Operations":
        st.header("IT Service Desk & Operations")
        with st.expander("Create New Ticket", expanded=True):
            with st.form("ticket_form"):
                col1, col2 = st.columns(2)
                with col1:
                    ticket_id = st.text_input("Ticket ID", value=f"TICKET-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
                    title = st.text_input("Title")
                    priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
                with col2:
                    assigned_to = st.text_input("Assign To", value=st.session_state.user)
                    description = st.text_area("Description")
                
                if st.form_submit_button("Create Ticket", type="primary"):
                    DB.save_ticket({
                        'id': ticket_id,
                        'priority': priority,
                        'desc': description,
                        'to': assigned_to,
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    st.success("Ticket created and saved!")
                    st.rerun()

        df = DB.get("it_tickets")
        open_count = len(df[df['status'].str.contains('Open|Progress|Waiting', case=False, na=False)])
        st.metric("Open Tickets", open_count)
        st.bar_chart(df["priority"].value_counts())
        st.dataframe(df)

    elif page == "AI Assistant":
        st.header("AI Assistant")
        
        domain = st.selectbox("Select Domain", ["Cybersecurity", "Data Science", "IT Operations", "General"], key="ai_domain")
        
        if AI_READY:
            st.success("Connected to OpenAI gpt-4o")
            
            if "messages" not in st.session_state:
                st.session_state.messages = [{"role": "system", "content": f"You are an expert in {domain}."}]
            
            for msg in st.session_state.messages[1:]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            
            col1, col2 = st.columns([6,1])
            with col1:
                prompt = st.text_input("Ask the AI anything:", key="ai_input", label_visibility="collapsed")
            with col2:
                if st.button("Ask AI", type="primary", use_container_width=True):
                    if prompt:
                        st.session_state.messages.append({"role": "user", "content": prompt})
                        with st.chat_message("user"):
                            st.markdown(prompt)
                        with st.chat_message("assistant"):
                            with st.spinner("Thinking..."):
                                resp = client.chat.completions.create(model="gpt-4o", messages=st.session_state.messages)
                                reply = resp.choices[0].message.content
                                st.markdown(reply)
                                st.session_state.messages.append({"role": "assistant", "content": reply})
        else:
            st.warning("OpenAI key not found")

# CLEAN — NO BANNERS