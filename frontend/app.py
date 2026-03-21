"""Streamlit Frontend: UI for the Enterprise RAG Chatbot."""

import os
import time
import streamlit as st
import requests
from typing import Optional, List, Dict
from loguru import logger
from streamlit_cookies_controller import CookieController

# --- Page Config ---
st.set_page_config(
    page_title="Enterprise AI Assistant",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- Backend Config ---
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# --- Initialize Session State & Cookies ---
controller = CookieController()
time.sleep(0.1) # small delay for cookie load
cookie_token = controller.get("auth_token")
cookie_email = controller.get("auth_email")
last_active = controller.get("last_active")

current_time = time.time()

if cookie_token:
    if last_active and (current_time - float(last_active) > 600):
        controller.remove("auth_token")
        controller.remove("last_active")
        st.session_state.token = None
        st.session_state.email = None
        # Use an empty container to show error without messing up the UI flow
        placeholder = st.empty()
        placeholder.error("🔒 Security Timeout: You have been logged out due to 10 minutes of inactivity.")
        time.sleep(3)
        st.rerun()
    elif last_active and (current_time - float(last_active) > 540):
        st.warning("⚠️ **Heads up!** You will be logged out in less than a minute due to inactivity.")
        
    if not st.session_state.get("token"):
        st.session_state.token = cookie_token
        st.session_state.email = cookie_email
        st.session_state.view = "dashboard"
        
    # Renew last_active cookie every 30 seconds to prevent constant reruns
    if not last_active or (current_time - float(last_active) > 30):
        controller.set("last_active", str(current_time))

if "token" not in st.session_state:
    st.session_state.token = None
if "email" not in st.session_state:
    st.session_state.email = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "view" not in st.session_state:
    st.session_state.view = "login"

# --- Premium Styling (ChatGPT Minimalist Theme) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, sans-serif !important;
    }
    .stApp { 
        background-color: #212121; 
        color: #ececec;
    }
    .main .block-container {
        padding-top: 1rem !important;
        max-width: 800px;
    }
    div[data-testid="stSidebar"] {
        background-color: #171717 !important;
        border-right: none !important;
    }
    h1, h2, h3, h4, .stMarkdown { color: #f9f9f9 !important; }
    p { color: #d1d5db !important; }
    
    /* Flat Buttons */
    .stButton>button { 
        width: 100%; border-radius: 8px; height: 3em; font-weight: 500; 
        background-color: #ffffff;
        color: #000000; border: none; box-shadow: none;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #e5e5e5;
        color: #000000;
        transform: none;
    }
    
    /* Standard Input */
    .stTextInput>div>div>input {
        background-color: #212121;
        border: 1px solid #4a4a4a;
        color: white; border-radius: 8px;
    }
    
    /* Tabs */
    div[data-baseweb="tab-list"] { background: transparent; }
    div[data-baseweb="tab"] { color: #a3a3a3; font-weight: 500; }
    div[aria-selected="true"] { color: #ffffff !important; background: transparent; border-bottom: 2px solid #ffffff; }

    /* --- Chat UI Overhaul (ChatGPT Style) --- */
    div[data-testid="stBottomBlockContainer"] {
        background: #212121 !important;
        padding-bottom: 20px !important;
    }
    div[data-testid="stChatInput"] {
        background-color: #2f2f2f !important;
        border: none !important;
        border-radius: 24px !important;
        box-shadow: none !important;
        padding: 4px 10px !important;
    }
    
    /* AI Chat Frame (Transparent) */
    div[data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0.5rem 0 !important;
    }
    
    /* User Chat Bubble */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        background-color: #2f2f2f !important;
        border-radius: 20px !important;
        padding: 1rem 1.5rem !important;
        margin: 1rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)


# --- ── Helper: API Calls ───────────────────────────────────────────────────

def api_login(email: str) -> bool:
    try:
        resp = requests.post(f"{BACKEND_URL}/auth/login", json={"email": email})
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Login request failed: {e}")
        return False

def api_verify_otp(email: str, otp: str) -> Optional[str]:
    try:
        resp = requests.post(f"{BACKEND_URL}/auth/verify-otp", json={"email": email, "otp": otp})
        if resp.status_code == 200:
            return resp.json().get("access_token")
    except Exception as e:
        logger.error(f"OTP verification failed: {e}")
    return None

def api_upload_file(file_obj, token: str) -> bool:
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": (file_obj.name, file_obj.getvalue(), file_obj.type)}
    try:
        resp = requests.post(f"{BACKEND_URL}/documents/upload", headers=headers, files=files)
        return resp.status_code == 201
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        return False

def api_chat_stream(query: str, history: List[Dict], token: str):
    """Generator for streaming chat responses."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"query": query, "history": history}
    try:
        # We use stream=True and iter_lines or iter_content
        with requests.post(f"{BACKEND_URL}/chat/query/stream", headers=headers, json=payload, stream=True) as resp:
            if resp.status_code == 200:
                for chunk in resp.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        yield chunk
            else:
                yield f"❌ Error: Backend returned status {resp.status_code}"
    except Exception as e:
        logger.error(f"Streaming request failed: {e}")
        yield f"❌ Error: {str(e)}"

# --- ── View: Login ─────────────────────────────────────────────────────────

def show_login():
    st.subheader("🏢 Enterprise RAG Chatbot")
    st.title("User Login")
    st.info("Enter your corporate email to receive a secure 6-digit access code (OTP).")
    
    email = st.text_input("Corporate Email", placeholder="user@company.com")
    
    if "otp_sent" not in st.session_state:
        st.session_state.otp_sent = False

    if not st.session_state.otp_sent:
        if st.button("Send Login Code"):
            if email:
                if api_login(email):
                    st.session_state.otp_sent = True
                    st.session_state.email = email
                    st.success(f"Code sent to {email}")
                    st.rerun()
                else:
                    st.error("Failed to send code. Is the server online?")
            else:
                st.warning("Please enter an email address.")
    else:
        otp = st.text_input("6-digit Code", placeholder="Type 123456...", max_chars=6)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Verify & Enter"):
                token = api_verify_otp(st.session_state.email, otp)
                if token:
                    st.session_state.token = token
                    st.session_state.view = "dashboard"
                    controller.set("auth_token", token)
                    controller.set("auth_email", st.session_state.email)
                    controller.set("last_active", str(time.time()))
                    st.success("Login Successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid or expired code.")
        with col2:
            if st.button("Resend OTP"):
                if api_login(st.session_state.email):
                    st.success("A new code has been sent!")
                else:
                    st.error("Failed to resend.")
        with col3:
            if st.button("Cancel"):
                st.session_state.otp_sent = False
                st.rerun()

# --- ── View: Dashboard (Sidebar & Tabs) ────────────────────────────────────

def show_dashboard():
    # Sidebar: User Info & Logout
    with st.sidebar:
        st.image("https://img.icons8.com/clouds/200/ffffff/bot.png")
        st.title("AI Assistant")
        st.markdown(f"Logged in as:<br>`{st.session_state.email}`", unsafe_allow_html=True)
        st.write("")
        if st.button("🔓 Sign Out"):
            st.session_state.clear()
            controller.remove("auth_token")
            controller.remove("last_active")
            st.rerun()
            
        st.divider()
        st.markdown("**📂 Document Intake**")
        uploaded_file = st.file_uploader("Upload memory context...", type=["pdf", "txt", "csv"])
        if uploaded_file:
            if st.button("🚀 Index Document"):
                with st.spinner("Embedding..."):
                    if api_upload_file(uploaded_file, st.session_state.token):
                        st.success("Indexed successfully.")
                    else:
                        st.error("Failed to index.")
        st.divider()
        st.caption("Powered by NVIDIA NIM")

    # --- Main Chat Area ---
    if len(st.session_state.chat_history) == 0:
        st.markdown("<h2 style='text-align: center; opacity: 0.5; margin-top: 20vh;'>How can I help you today?</h2>", unsafe_allow_html=True)
    else:
        st.write("") # Spacing

    # Display History
    for msg in st.session_state.chat_history:
        role = msg["role"]
        content = msg["content"]
        with st.chat_message(role):
            st.markdown(content)

    # Input
    if prompt := st.chat_input("Message the AI..."):
        # Display user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # API Call (Streaming)
        with st.chat_message("assistant"):
            response_container = st.container()
            metadata_container = st.container()
            
            full_response = ""
            meta_data = {"emotion": "neutral", "sources": []}

            def stream_parser():
                nonlocal full_response, meta_data
                import json
                for chunk in api_chat_stream(prompt, st.session_state.chat_history[:-1], st.session_state.token):
                    if chunk.startswith("__METADATA__:"):
                        try:
                            meta_str = chunk.split("\n")[0].replace("__METADATA__:", "")
                            meta_data = json.loads(meta_str)
                            if "\n" in chunk:
                                remaining = chunk.split("\n", 1)[1]
                                if remaining:
                                    full_response += remaining
                                    yield remaining
                        except:
                            pass
                    else:
                        full_response += chunk
                        yield chunk

            st.write_stream(stream_parser())

            with metadata_container:
                if meta_data["sources"]:
                    st.caption(f"Sources used: {', '.join(meta_data['sources'])}")

            st.session_state.chat_history.append({"role": "assistant", "content": full_response})

# --- Main Logic ---
if st.session_state.token is None:
    show_login()
else:
    show_dashboard()
