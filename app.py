import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
from supabase import create_client, Client
import extra_streamlit_components as stx
import requests, base64, asyncio, datetime
import edge_tts

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
    .stAppDeployButton { display: none !important; }
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
# 3. Initialization & Cookie Management
# -----------------------
if "messages" not in st.session_state: st.session_state.messages = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_email" not in st.session_state: st.session_state.user_email = None

cookie_manager = stx.CookieManager()
saved_email = cookie_manager.get(cookie="alpha_session_email")

# Auto-login if cookie exists
if saved_email and not st.session_state.logged_in:
    st.session_state.logged_in = True
    st.session_state.user_email = saved_email

# -----------------------
# 4. API & Database Setup
# -----------------------
# Using credentials from your Secrets
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    st.error("Missing Supabase Secrets. Please check your Streamlit settings.")
    st.stop()

groq_client = Groq(api_key=GROQ_API_KEY)
hf_client = InferenceClient(token=HF_TOKEN)

# -----------------------
# 5. Authentication Logic
# -----------------------
def login_user(email, password):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user_email = response.user.email
        st.session_state.logged_in = True
        # Set cookie to expire in 30 days
        cookie_manager.set("alpha_session_email", response.user.email, expires_at=datetime.datetime.now() + datetime.timedelta(days=30))
        st.rerun()
    except: st.error("Access Denied: Invalid Email or Password.")

def signup_user(email, password, name):
    try:
        # NOTE: Ensure "Confirm Email" is OFF in Supabase Auth Settings
        supabase.auth.sign_up({"email": email, "password": password, "options": {"data": {"full_name": name}}})
        st.success("Identity Created! Use the Login tab to enter.")
    except Exception as e: st.error(f"Error: {e}")

def github_login_btn():
    try:
        res = supabase.auth.sign_in_with_oauth({"provider": "github"})
        # Fix for "Refused to Connect" Iframe error
        st.markdown(f'<a href="{res.url}" target="_self"><button style="background-color: #24292e; color: white; padding: 12px; border-radius: 10px; width: 100%; cursor: pointer; border: none; font-weight: bold;">🚀 Login with GitHub</button></a>', unsafe_allow_html=True)
    except: st.error("GitHub Connection Failed.")

# -----------------------
# 6. Auth UI
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="premium-banner">ALPHA CORE SYSTEM ACCESS</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        t_login, t_reg = st.tabs(["🔐 Login", "📝 Register"])
        with t_login:
            e_in = st.text_input("Email")
            p_in = st.text_input("Password", type="password")
            if st.button("Initialize"): login_user(e_in, p_in)
            st.divider()
            github_login_btn()
        with t_reg:
            n_reg = st.text_input("Full Name")
            e_reg = st.text_input("Email")
            p_reg = st.text_input("Password", type="password")
            if st.button("Register Identity"): signup_user(e_reg, p_reg, n_reg)
    st.stop()

# -----------------------
# 7. Core Systems
# -----------------------
async def speak(text):
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
# 8. Main Dashboard
# -----------------------
with st.sidebar:
    st.title("Alpha Control")
    st.write(f"Active User: **{st.session_state.user_email}**")
    engine = st.radio("Intelligence Engine", ["Standard (Llama 3.3)", "Reasoning (DeepSeek-R1)"])
    v_toggle = st.checkbox("Voice Feedback", value=True)
    if st.button("Emergency Logout"):
        supabase.auth.sign_out()
        cookie_manager.delete("alpha_session_email")
        st.session_state.logged_in = False
        st.rerun()

st.markdown('<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

user_cmd = st.chat_input("State your command...")

if user_cmd:
    st.session_state.messages.append({"role": "user", "content": user_cmd})
    with st.chat_message("user"): st.markdown(user_cmd)
    
    with st.chat_message("assistant"):
        box = st.empty()
        full_txt = ""
        
        if "Standard" in engine:
            try:
                # Fix for "Restricted" Groq error
                s = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are Alpha AI by Hasith."}] + st.session_state.messages[-10:],
                    stream=True
                )
                for c in s:
                    if c.choices[0].delta.content:
                        full_txt += c.choices[0].delta.content
                        box.markdown(full_txt + "▌")
            except: st.error("Update your Groq API Key in Secrets.")
        else:
            try:
                for m in hf_client.chat_completion(
                    model="deepseek-ai/DeepSeek-R1-Zero",
                    messages=[{"role": "system", "content": "You are Alpha AI reasoning engine."}] + st.session_state.messages[-10:],
                    max_tokens=2048, stream=True
                ):
                    if m.choices[0].delta.content:
                        full_txt += m.choices[0].delta.content
                        box.markdown(full_txt + "▌")
            except: st.error("DeepSeek Engine Busy.")

        box.markdown(full_txt)
        if v_toggle: asyncio.run(speak(full_txt))
        st.session_state.messages.append({"role": "assistant", "content": full_txt})
