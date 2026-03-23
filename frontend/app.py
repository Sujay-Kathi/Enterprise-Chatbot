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
    page_title="Velo AI | Enterprise Chatbot",
    page_icon="⚡",
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
    /* --- UI & Typography Polish --- */
    h1, h2, h3, h4 { 
        color: #F3F4F6 !important; 
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    .stMarkdown, p { 
        color: #E5E7EB !important; 
        line-height: 1.6;
    }
    
    /* Clean, Modern Buttons (Remove Cliché Defaults) */
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3rem; 
        font-weight: 500; 
        background-color: #3B82F6; /* Velo Blue */
        color: #FFFFFF !important; 
        border: none; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton>button:hover {
        background-color: #2563EB;
        transform: translateY(-1px);
        box-shadow: 0 6px 8px -1px rgba(0, 0, 0, 0.2);
    }
    
    /* Inputs: Solid & Professional */
    .stTextInput>div>div>input {
        background-color: #27272A;
        border: 1px solid #3F3F46;
        color: #F8FAFC; 
        border-radius: 8px;
        padding: 0.75rem 1rem;
        transition: border-color 0.2s;
    }
    .stTextInput>div>div>input:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 1px #3B82F6;
    }
    
    /* Tabs: Simplified */
    div[data-baseweb="tab-list"] { background: transparent; gap: 1rem; }
    div[data-baseweb="tab"] { color: #A1A1AA; font-weight: 500; font-size: 0.95rem; }
    div[aria-selected="true"] { color: #FFFFFF !important; background: transparent; border-bottom: 2px solid #3B82F6 !important; }

    /* --- Chat UI Overhaul (Minimalist, Distinct) --- */
    div[data-testid="stBottomBlockContainer"] {
        background: #212121 !important;
        padding-bottom: 24px !important;
    }
    /* Elegant Chat Input */
    div[data-testid="stChatInput"] {
        background-color: #27272A !important;
        border: 1px solid #3F3F46 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
        padding: 4px 12px !important;
    }
    
    /* AI Chat Frame (Transparent, Clean) */
    div[data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 1rem 0 !important;
        gap: 1rem !important;
    }
    
    /* User Chat Bubble (Distinct Visual Hierarchy) */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        background-color: #27272A !important;
        border: 1px solid #3F3F46 !important;
        border-radius: 12px !important;
        padding: 1.25rem !important;
        margin: 1rem 0 2rem 0 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    }

    /* Custom Avatar styling to override ugly default boxes */
    [data-testid="chatAvatarIcon-user"] {
        background-color: #3B82F6 !important;
        border-radius: 8px !important;
        color: white !important;
    }
    [data-testid="chatAvatarIcon-assistant"] {
        background-color: #10B981 !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    /* Small labels above chat */
    .chat-name-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #9CA3AF;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
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

def api_list_documents(token: str) -> List[Dict]:
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(f"{BACKEND_URL}/documents/", headers=headers)
        if resp.status_code == 200:
            return resp.json().get("documents", [])
    except Exception as e:
        logger.error(f"List documents failed: {e}")
    return []

def api_pin_document(filename: str, pin: bool, token: str) -> bool:
    headers = {"Authorization": f"Bearer {token}"}
    params = {"filename": filename, "pin": pin}
    try:
        resp = requests.post(f"{BACKEND_URL}/documents/pin", headers=headers, params=params)
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Pin document failed: {e}")
        return False

# --- ── View: Login ─────────────────────────────────────────────────────────

def show_login():
    st.subheader("🏢 Velo Enterprise")
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
        st.title("VELO")
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
                        st.rerun()
                    else:
                        st.error("Failed to index.")
        
        st.divider()
        st.markdown("**🧠 Knowledge Manager (CAG)**")
        docs = api_list_documents(st.session_state.token)
        if docs:
            # Stats
            total_docs = len(docs)
            pinned_docs = sum(1 for d in docs if d["pinned"])
            st.caption(f"Files Index: {total_docs} | 🔥 Pinned: {pinned_docs}")
            
            # Use small columns or container for clean list
            for doc in docs:
                fname = doc["filename"]
                is_pinned = doc["pinned"]
                count = doc.get("usage_count", 0)
                
                # Dynamic labeling
                icon = "🔥" if is_pinned else "📄"
                label = f"{icon} {fname} ({count} hits)"
                
                # Checkbox for manual override / status view
                if st.checkbox(label, value=is_pinned, key=f"pin_{fname}"):
                    if not is_pinned:
                        if api_pin_document(fname, True, st.session_state.token):
                            st.rerun()
                else:
                    if is_pinned:
                        if api_pin_document(fname, False, st.session_state.token):
                            st.rerun()
        else:
            st.caption("No documents in library yet.")
            
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
        avatar = "👤" if role == "user" else "⚡"
        
        with st.chat_message(role, avatar=avatar):
            name = "User" if role == "user" else "Velo"
            st.markdown(f"<div class='chat-name-label'>{name}</div>", unsafe_allow_html=True)
            st.markdown(content)
            
            # Clean inline metadata tags
            if role == "assistant":
                if msg.get("cached"):
                    st.markdown("<div style='font-size: 0.7rem; color: #FCD34D; background: rgba(252, 211, 77, 0.1); border: 1px solid rgba(252, 211, 77, 0.2); padding: 3px 8px; border-radius: 6px; display: inline-block; margin-top: 8px; margin-right: 6px;'>⚡ Instant Memory</div>", unsafe_allow_html=True)
                if msg.get("sources") and len(msg["sources"]) > 0:
                    sources_str = ", ".join(msg["sources"])
                    st.markdown(f"<div style='font-size: 0.7rem; color: #9CA3AF; background: rgba(156, 163, 175, 0.1); border: 1px solid rgba(156, 163, 175, 0.2); padding: 3px 8px; border-radius: 6px; display: inline-block; margin-top: 8px;'>📚  {sources_str}</div>", unsafe_allow_html=True)

    if prompt := st.chat_input("Message the AI..."):
        # Display user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown("<div class='chat-name-label'>User</div>", unsafe_allow_html=True)
            st.markdown(prompt)

        # API Call (Streaming)
        with st.chat_message("assistant", avatar="⚡"):
            st.markdown("<div class='chat-name-label'>Velo</div>", unsafe_allow_html=True)
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
                # Same inline metadata tags for the live stream
                if meta_data.get("cached"):
                    st.markdown("<div style='font-size: 0.7rem; color: #FCD34D; background: rgba(252, 211, 77, 0.1); border: 1px solid rgba(252, 211, 77, 0.2); padding: 3px 8px; border-radius: 6px; display: inline-block; margin-top: 8px; margin-right: 6px;'>⚡ Instant Memory</div>", unsafe_allow_html=True)
                
                if meta_data.get("sources") and len(meta_data["sources"]) > 0:
                    sources_str = ", ".join(meta_data['sources'])
                    st.markdown(f"<div style='font-size: 0.7rem; color: #9CA3AF; background: rgba(156, 163, 175, 0.1); border: 1px solid rgba(156, 163, 175, 0.2); padding: 3px 8px; border-radius: 6px; display: inline-block; margin-top: 8px;'>📚  {sources_str}</div>", unsafe_allow_html=True)

            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": full_response,
                "cached": meta_data.get("cached", False),
                "sources": meta_data.get("sources", [])
            })

# --- Main Logic ---
if st.session_state.token is None:
    show_login()
else:
    show_dashboard()
