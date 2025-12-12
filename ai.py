# ═══════════════════════════════════════════════════════════
# CST1510 Week 10 – FULL GEMINI AI INTEGRATION (BETTER & FREE)
# Multi-Domain Intelligent Assistant: Cybersecurity | Data Science | IT Operations
# ═══════════════════════════════════════════════════════════

import streamlit as st
import google.generativeai as genai

# ------------------- CONFIGURATION -------------------
# Securely load your Gemini API key
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("Gemini API Key not found! Add it to .streamlit/secrets.toml")
    st.stop()

# Available models (all free for development!)
GEMINI_MODEL = "gemini-1.5-flash"  # Fast, smart, and free up to 1000 requests/day

# Domain-specific system prompts (this is the magic!)
DOMAIN_PROMPTS = {
    "General Assistant": "You are a helpful and friendly assistant.",
    "Cybersecurity Expert": """
You are a senior cybersecurity analyst with 15 years of experience.
Provide technical, accurate, and actionable advice.
Use MITRE ATT&CK references when relevant.
Always suggest immediate actions and long-term prevention.
Be professional and clear.
    """,
    "Data Science Expert": """
You are a data science and machine learning expert.
Help with data analysis, visualization recommendations, statistical tests, and Python/R code.
Explain concepts clearly and suggest best practices.
    """,
    "IT Operations Expert": """
You are an experienced IT operations and DevOps engineer.
Help troubleshoot systems, prioritize tickets, optimize infrastructure, and explain technical issues.
Focus on practical, real-world solutions.
    """
}

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="Multi-Domain AI Platform", page_icon="Brain", layout="wide")
st.title("Multi-Domain Intelligence Platform")
st.markdown("### Powered by Google Gemini AI (Free & No Credit Card Needed)")

# ------------------- SIDEBAR -------------------
with st.sidebar:
    st.header("AI Assistant Settings")

    # Domain selector
    selected_domain = st.selectbox(
        "Choose AI Expert:",
        options=list(DOMAIN_PROMPTS.keys()),
        index=1  # Default: Cybersecurity
    )

    st.divider()
    st.caption(f"**Current Expert:** {selected_domain}")

    # Message counter
    if "chat" in st.session_state:
        msg_count = len([m for m in st.session_state.chat.history if m.role != "model"])
        st.metric("Messages in Chat", msg_count)
    else:
        st.metric("Messages in Chat", 0)

    # Clear chat button
    if st.button("Clear Chat History", use_container_width=True, type="primary"):
        st.session_state.chat = st.session_state.model.start_chat(history=[])
        st.success("Chat cleared!")
        st.rerun()

# ------------------- INITIALIZE MODEL & CHAT -------------------
# Re-create model only when domain changes
if ("last_domain" not in st.session_state or
        st.session_state.last_domain != selected_domain):
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=DOMAIN_PROMPTS[selected_domain]
    )

    # Start fresh chat with new expert
    st.session_state.model = model
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.last_domain = selected_domain

# ------------------- DISPLAY CHAT HISTORY -------------------
for message in st.session_state.chat.history:
    role = "user" if message.role == "user" else "assistant"
    with st.chat_message(role):
        # Gemini stores text in parts[0].text
        try:
            st.markdown(message.parts[0].text)
        except:
            st.markdown("...")

# ------------------- USER INPUT -------------------
if prompt := st.chat_input(f"Ask the {selected_domain} anything..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send to Gemini with streaming
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            response = st.session_state.chat.send_message(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Gemini API Error: {e}")
            st.info("Check your internet or API key.")

# ------------------- FOOTER -------------------
st.markdown("---")
st.caption("CST1510 Coursework 2 • Google Gemini 1.5 Flash • Free Tier • No OpenAI Credits Needed")