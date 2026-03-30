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
# 2. Custom UI Styling (No Branding, Sidebar Visible)
# -----------------------
st.markdown("""
<style>
    footer {visibility: hidden;}
    .stAppDeployButton, [data-testid="stStatusWidget"] { display: none !important; }
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:20px; font-size: 22px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }
    .stChatMessage { border-radius: 15px; }
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; height: 45px; font-weight: bold; border: 1px solid #FFD700; transition: 0.3s; }
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
# 4. API & Database Setup (Supabase Integration)
# -----------------------
# ඔයා එවපු Keys ටික මෙතනින් Secrets හරහා ලබාගන්නවා
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")

# Supabase Client එක Initialize කිරීම
if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    st.error("Database connection failed. Please check Streamlit Secrets.")
    st.stop()

groq_client = Groq(api_key=GROQ_API_KEY)
hf_client = InferenceClient(token=HF_TOKEN)

# -----------------------
# 5. Auth Logic (Permanent Login)
# -----------------------
def login_alpha(email, password):
    try:
        # Supabase හරහා login වීම
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = response.user
        st.session_state.logged_in = True
        st.success("Access Granted, Master!")
        st.rerun()
    except Exception as e:
        st.error("Authentication Error: Invalid Master Credentials.")

def signup_alpha(email, password, name):
    try:
        # අලුත් User කෙනෙක් register කිරීම
        response = supabase.auth.sign_up({"email": email, "password": password, "options": {"data": {"full_name": name}}})
        st.info("Registration successful! Please check your email to verify.")
    except Exception as e:
        st.error(f"Error during registration: {e}")

# -----------------------
# 6. Login Screen UI
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="premium-banner">ALPHA CORE SYSTEM ACCESS</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#FFD700; font-weight:bold;">Created by Hasith Karunarathna</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_signup = st.tabs(["🔐 Login", "📝 New Operator"])
        
        with tab_login:
            login_email = st.text_input("Email")
            login_pass = st.text_input("Password", type="password")
            if st.button("Initialize Alpha"):
                login_alpha(login_email, login_pass)
            st.divider()
            st.caption("Forgot your Master Key? Contact Admin Hasith.")

        with tab_signup:
            new_name = st.text_input("Full Name")
            new_email = st.text_input("Official Email")
            new_pass = st.text_input("Create Password", type="password")
            if st.button("Register Identity"):
                signup_alpha(new_email, new_pass, new_name)

    st.stop()

# -----------------------
# 7. Helper Functions (Voice & AI)
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
# 8. Main Application UI (Sidebar & Tabs)
# -----------------------
with st.sidebar:
    st.title("Alpha Control")
    st.write(f"Operator: **{st.session_state.user.email}**")
    st.divider()
    mode = st.radio("Intelligence Level", ["Normal (Llama 3.3)", "Pro (DeepSeek-R1-Zero 671B)"])
    voice_on = st.checkbox("Voice Output", value=True)
    if st.button("Log Out"):
        supabase.auth.sign_out()
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()
    st.write("---")
    st.caption("Created by Hasith | Bandarawela Central College")

st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

# Multimodal Tabs
tab_chat, tab_lab = st.tabs(["💬 Hybrid Conversation", "🖼 AI Creation Lab"])

with tab_chat:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    user_input = st.chat_input("State your command, Master...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"): st.markdown(user_input)
        
        with st.chat_message("assistant"):
            res_placeholder = st.empty()
            full_res = ""
            
            if "Normal" in mode:
                try:
                    stream = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": f"You are Alpha AI created by Hasith. Warmly greet user {st.session_state.user.email}."}] + st.session_state.messages[-10:],
                        stream=True
                    )
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            full_res += chunk.choices[0].delta.content
                            res_placeholder.markdown(full_res + "▌")
                except: st.error("Groq Restriction Error. Please update Secrets.")
            
            else:
                # Pro Mode: DeepSeek-R1-Zero 671B (Full Model)
                try:
                    for message in hf_client.chat_completion(
                        model="deepseek-ai/DeepSeek-R1-Zero",
                        messages=[{"role": "system", "content": "You are Alpha AI, a deep reasoning engine created by Hasith Karunarathna."}] + st.session_state.messages[-10:],
                        max_tokens=2048, stream=True
                    ):
                        content = message.choices[0].delta.content
                        if content:
                            full_res += content
                            res_placeholder.markdown(full_res + "▌")
                except: st.error("DeepSeek (HF) is busy or overloaded. Try again.")

            res_placeholder.markdown(full_res)
            if voice_on: asyncio.run(speak_alpha(full_res))
            st.session_state.messages.append({"role": "assistant", "content": full_res})

with tab_lab:
    st.subheader("Image Generation Lab")
    img_p = st.text_input("Describe your vision:")
    if st.button("Generate Visualization"):
        with st.spinner("Alpha is thinking..."):
            url = f"https://gen.pollinations.ai/image/{urllib.parse.quote(img_p)}?nologo=true&seed={random.randint(1,9999)}"
            st.image(url, caption="Generated by Alpha AI")
