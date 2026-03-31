import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
from supabase import create_client, Client
import requests, base64, asyncio, io
import edge_tts
import urllib.parse
import random

# -----------------------
# 1. Page Config & Identity
# -----------------------
st.set_page_config(page_title="Alpha AI | Created by Hasith", layout="wide", page_icon="⚡")

# -----------------------
# 2. Custom UI Styling
# -----------------------
st.markdown("""
<style>
    footer {visibility: hidden;}
    .stAppDeployButton, [data-testid="stStatusWidget"] { display: none !important; }
    .premium-banner { 
        width:100%; padding:15px; 
        background: linear-gradient(90deg, #FFD700, #FF8C00); 
        color:#000; border-radius:15px; 
        text-align:center; font-weight:bold; 
        margin-bottom:20px; font-size: 24px; 
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3); 
    }
    div.stButton > button { 
        background-color: #1e1e1e; color: #FFD700; 
        border-radius: 12px; width: 100%; 
        height: 45px; font-weight: bold; 
        border: 1px solid #FFD700; 
    }
    div.stButton > button:hover { background-color: #FFD700; color: #000; }
</style>
""", unsafe_allow_html=True)

# -----------------------
# 3. Session State Init
# -----------------------
if "messages" not in st.session_state: st.session_state.messages = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user" not in st.session_state: st.session_state.user = None

# -----------------------
# 4. API & Database Setup
# -----------------------
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    st.error("Supabase Credentials Missing in Secrets.")
    st.stop()

groq_client = Groq(api_key=GROQ_API_KEY)
hf_client = InferenceClient(token=HF_TOKEN)

# -----------------------
# 5. Authentication Logic
# -----------------------
def login_user(email, password):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = response.user
        st.session_state.logged_in = True
        st.rerun()
    except: st.error("Access Denied: Invalid Credentials.")

def signup_user(email, password, name):
    try:
        # Note: Ensure "Confirm Email" is OFF in Supabase Auth Settings
        supabase.auth.sign_up({
            "email": email, 
            "password": password, 
            "options": {"data": {"full_name": name}}
        })
        st.success("Identity Created! You can now Login.")
    except Exception as e: st.error(f"Error: {e}")

def github_login():
    try:
        res = supabase.auth.sign_in_with_oauth({"provider": "github"})
        # Using a button link to prevent "Refused to Connect" error
        st.markdown(f"""
            <a href="{res.url}" target="_self">
                <button style="background-color: #24292e; color: white; padding: 12px; border-radius: 10px; width: 100%; cursor: pointer; border: none; font-weight: bold;">
                    🚀 Authorize via GitHub
                </button>
            </a>
        """, unsafe_allow_html=True)
    except: st.error("GitHub Connection Failed.")

# -----------------------
# 6. Login Screen
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="premium-banner">ALPHA CORE SYSTEM ACCESS</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Register"])
        with tab_login:
            email = st.text_input("Email")
            pw = st.text_input("Password", type="password")
            if st.button("Initialize Alpha"): login_user(email, pw)
            st.divider()
            github_login()
        with tab_signup:
            reg_name = st.text_input("Full Name")
            reg_email = st.text_input("Official Email")
            reg_pw = st.text_input("Create Password", type="password")
            if st.button("Create Account"): signup_user(reg_email, reg_pw, reg_name)
    st.stop()

# -----------------------
# 7. Core Functions (Voice Fix)
# -----------------------
async def speak_text(text):
    try:
        communicate = edge_tts.Communicate(text, "en-US-SteffanNeural")
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio": audio_data += chunk["data"]
        if audio_data:
            b64 = base64.b64encode(audio_data).decode()
            st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

# -----------------------
# 8. Main Dashboard
# -----------------------
with st.sidebar:
    st.title("Alpha Settings")
    st.write(f"User: **{st.session_state.user.email}**")
    model_choice = st.radio("AI Engine", ["Normal (Llama 3.3)", "Pro (DeepSeek-R1)"])
    voice_enabled = st.checkbox("Enable Voice", value=True)
    if st.button("System Logout"):
        supabase.auth.sign_out()
        st.session_state.logged_in = False
        st.rerun()
    st.divider()
    st.caption("Created by Hasith Karunarathna")

st.markdown('<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

# Chat Layout
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

prompt = st.chat_input("Enter command...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        response_text = ""
        
        if "Normal" in model_choice:
            try:
                # IMPORTANT: Replace restricted Groq Key in Secrets
                stream = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are Alpha AI created by Hasith Karunarathna."}] + st.session_state.messages[-10:],
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        response_text += chunk.choices[0].delta.content
                        placeholder.markdown(response_text + "▌")
            except: st.error("Groq Key Restricted. Please update in Secrets.")
        else:
            try:
                # Pro Mode: DeepSeek-R1
                for message in hf_client.chat_completion(
                    model="deepseek-ai/DeepSeek-R1-Zero",
                    messages=[{"role": "system", "content": "You are Alpha AI, a reasoning engine by Hasith."}] + st.session_state.messages[-10:],
                    max_tokens=2048, stream=True
                ):
                    if message.choices[0].delta.content:
                        response_text += message.choices[0].delta.content
                        placeholder.markdown(response_text + "▌")
            except: st.error("DeepSeek Engine is currently overloaded.")

        placeholder.markdown(response_text)
        
        # Audio Fix
        if voice_enabled: asyncio.run(speak_text(response_text))
        st.session_state.messages.append({"role": "assistant", "content": response_text})
