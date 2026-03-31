import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
from supabase import create_client, Client
import extra_streamlit_components as stx
import requests, base64, asyncio, io, json, datetime
import edge_tts
from PIL import Image
import urllib.parse
import random
from duckduckgo_search import DDGS 

# -----------------------
# 1. Page Config & Identity
# -----------------------
st.set_page_config(page_title="Alpha AI | Created by Hasith", layout="wide", page_icon="⚡")
st.markdown('<meta name="google-site-verification" content="W6jIGzCkkez2SpjygP6z0dJfinBNALmw2Hv-MkJvFB0" />', unsafe_allow_html=True)

# -----------------------
# 2. Session & Cookie Management
# -----------------------
cookie_manager = stx.CookieManager()
if "messages" not in st.session_state: st.session_state.messages = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False

saved_email = cookie_manager.get(cookie="alpha_persistent_login")

# -----------------------
# 3. API Setup
# -----------------------
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")

if not all([SUPABASE_URL, SUPABASE_KEY, GROQ_API_KEY, HF_TOKEN]):
    st.error("Missing API Keys in Streamlit Secrets!")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)
hf_client = InferenceClient(token=HF_TOKEN)

if saved_email and not st.session_state.logged_in:
    st.session_state.logged_in = True
    st.session_state.user_email = saved_email

# -----------------------
# 4. Auth Logic (GitHub Fix Included)
# -----------------------
def login_user(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user_email = res.user.email
        st.session_state.logged_in = True
        cookie_manager.set("alpha_persistent_login", res.user.email, expires_at=datetime.datetime.now() + datetime.timedelta(days=30))
        st.rerun()
    except: st.error("Invalid Credentials")

if not st.session_state.logged_in:
    st.markdown('<div style="text-align:center; padding:20px; background:orange; color:black; border-radius:10px; font-weight:bold;">ALPHA CORE ACCESS REQUIRED</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        l_email = st.text_input("Email")
        l_pass = st.text_input("Password", type="password")
        if st.button("Login"): login_user(l_email, l_pass)
        # GitHub login link for iframe fix
        auth_res = supabase.auth.sign_in_with_oauth({"provider": "github"})
        st.markdown(f'<a href="{auth_res.url}" target="_blank"><button style="width:100%; padding:10px; border-radius:10px; background:#333; color:white; border:none; cursor:pointer;">🚀 Login via GitHub (New Tab)</button></a>', unsafe_allow_html=True)
    st.stop()

# -----------------------
# 5. UI Styling
# -----------------------
st.markdown("""
<style>  
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:20px; font-size: 22px; }  
</style>  """, unsafe_allow_html=True)

# -----------------------
# 6. Sidebar Control
# -----------------------
with st.sidebar:
    st.title("Alpha Control")
    st.write(f"User: {st.session_state.user_email}")
    # Changed labels to reflect your Dashboard
    mode = st.radio("Intelligence Engine", ["Normal (Llama 3.3 70B)", "Pro (GPT OSS 120B)"])
    voice_on = st.checkbox("Voice Feedback", value=True)
    if st.button("Log Out"):
        cookie_manager.delete("alpha_persistent_login")
        st.session_state.logged_in = False
        st.rerun()

st.markdown('<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

# -----------------------
# 7. Chat Engine with Fallback Logic
# -----------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

user_input = st.chat_input("Command Alpha...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)
    
    with st.chat_message("assistant"):
        box = st.empty()
        full_res = ""
        
        # Decide model based on user selection
        target_model = "llama-3.3-70b-versatile" if "Normal" in mode else "openai/gpt-oss-120b"
        
        try:
            # First Attempt: Use Groq
            stream = groq_client.chat.completions.create(
                model=target_model,
                messages=[{"role": "system", "content": "You are Alpha AI by Hasith."}] + st.session_state.messages[-5:],
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    box.markdown(full_res + "▌")
        
        except Exception as e:
            # Fallback: If Groq is restricted, use Hugging Face
            st.warning("Primary engine restricted. Switching to Alpha Backup Engine...")
            try:
                hf_res = hf_client.chat_completion(
                    messages=[{"role": "user", "content": user_input}],
                    max_tokens=500,
                    model="HuggingFaceH4/zephyr-7b-beta"
                )
                full_res = hf_res.choices[0].message.content
            except:
                full_res = "Alpha System Error: All engines are currently restricted. Please check your API quotas."

        box.markdown(full_res)
        st.session_state.messages.append({"role": "assistant", "content": full_res})

st.caption("Alpha AI Project | Developed by Hasith Heshan Karunarathna")
