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
# 2. Custom UI Styling (No Branding)
# -----------------------
st.markdown("""
<style>
    footer {visibility: hidden;}
    .stAppDeployButton, [data-testid="stStatusWidget"] { display: none !important; }
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:20px; font-size: 22px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; height: 45px; font-weight: bold; border: 1px solid #FFD700; }
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
    st.error("Database connection failed. Check Secrets.")
    st.stop()

groq_client = Groq(api_key=GROQ_API_KEY)
hf_client = InferenceClient(token=HF_TOKEN)

# -----------------------
# 5. Auth Logic
# -----------------------
def login_alpha(email, password):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = response.user
        st.session_state.logged_in = True
        st.rerun()
    except: st.error("Invalid Login Credentials.")

def signup_alpha(email, password, name):
    try:
        # Email verification එක Dashboard එකෙන් off කළාම මේක කෙලින්ම වැඩ කරනවා
        supabase.auth.sign_up({"email": email, "password": password, "options": {"data": {"full_name": name}}})
        st.success("Registration successful! Now you can Login.")
    except Exception as e: st.error(f"Signup Error: {e}")

def github_login():
    try:
        # GitHub OAuth logic
        res = supabase.auth.sign_in_with_oauth({"provider": "github"})
        st.markdown(f'<meta http-equiv="refresh" content="0; url={res.url}">', unsafe_allow_html=True)
    except: st.error("GitHub Login Failed.")

# -----------------------
# 6. Login UI
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="premium-banner">ALPHA CORE SYSTEM ACCESS</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_l, tab_s = st.tabs(["🔐 Login", "📝 Sign Up"])
        with tab_l:
            l_email = st.text_input("Email")
            l_pass = st.text_input("Password", type="password")
            if st.button("Access Alpha"): login_alpha(l_email, l_pass)
            st.divider()
            if st.button("Continue with GitHub"): github_login()
        with tab_s:
            s_name = st.text_input("Full Name")
            s_email = st.text_input("Official Email")
            s_pass = st.text_input("Create Password", type="password")
            if st.button("Create Identity"): signup_alpha(s_email, s_pass, s_name)
    st.stop()

# -----------------------
# 7. Core System (Voice Fixed)
# -----------------------
async def speak_alpha(text):
    try:
        comm = edge_tts.Communicate(text, "en-US-SteffanNeural")
        audio = b""
        async for chunk in comm.stream():
            if chunk["type"] == "audio": audio += chunk["data"]
        if audio:
            b64 = base64.b64encode(audio).decode()
            st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

# -----------------------
# 8. Main App Interface
# -----------------------
with st.sidebar:
    st.title("Alpha Control")
    st.write(f"Logged as: **{st.session_state.user.email}**")
    mode = st.radio("Intelligence Level", ["Normal", "Pro (DeepSeek-R1)"])
    voice_on = st.checkbox("Voice Output", value=True)
    if st.button("Log Out"):
        supabase.auth.sign_out()
        st.session_state.logged_in = False
        st.rerun()

st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

# Chat System
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

user_input = st.chat_input("State your command, Master...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)
    
    with st.chat_message("assistant"):
        res_placeholder = st.empty()
        full_res = ""
        
        if mode == "Normal":
            try:
                # මෙතනදී GROQ API Key එක අලුත් එකක් විය යුතුයි
                stream = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are Alpha AI created by Hasith."}] + st.session_state.messages[-10:],
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        res_placeholder.markdown(full_res + "▌")
            except: st.error("Groq Restriction Error. Please update API Key.")
        else:
            try:
                for message in hf_client.chat_completion(
                    model="deepseek-ai/DeepSeek-R1-Zero",
                    messages=[{"role": "system", "content": "You are Alpha AI reasoning model."}] + st.session_state.messages[-10:],
                    max_tokens=2048, stream=True
                ):
                    if message.choices[0].delta.content:
                        full_res += message.choices[0].delta.content
                        res_placeholder.markdown(full_res + "▌")
            except: st.error("DeepSeek (HF) is busy.")

        res_placeholder.markdown(full_res)
        # Voice Error Fix
        if voice_on: asyncio.run(speak_alpha(full_res))
        st.session_state.messages.append({"role": "assistant", "content": full_res})
