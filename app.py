import streamlit as st
from groq import Groq
import sys
import time
from io import StringIO
from streamlit_mic_recorder import speech_to_text
import hashlib
import random
import urllib.parse
import os
import PyPDF2
from gtts import gTTS
import base64

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Created by Hasith", page_icon="⚡", layout="wide")

# 2. Alpha Loading Screen (7 Seconds)
if "loaded" not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
            <style>
                .loader-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh; }
                .alpha-text { font-size: 50px; font-weight: bold; color: #FFD700; text-shadow: 0 0 20px #FF8C00; margin-bottom: 20px; font-family: 'Arial Black', sans-serif; }
                .loading-bar { width: 300px; height: 4px; background: #333; border-radius: 2px; overflow: hidden; position: relative; }
                .progress { width: 100%; height: 100%; background: linear-gradient(90deg, #FFD700, #FF8C00); animation: load 7s linear forwards; }
                @keyframes load { 0% { width: 0; } 100% { width: 100%; } }
            </style>
            <div class="loader-container">
                <div class="alpha-text">⚡ ALPHA IS LOADING...</div>
                <div class="loading-bar"><div class="progress"></div></div>
                <p style="color: #888; margin-top: 15px;">Advanced Neural Integration by Hasith</p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(7)
    st.session_state.loaded = True
    placeholder.empty()
    st.rerun()

# 3. Session & Database Setup
if "user_db" not in st.session_state:
    st.session_state.user_db = {
        "matheesha": {"password": "123", "vault": []},
        "sadev": {"password": "123", "vault": []}
    }
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_user" not in st.session_state: st.session_state.current_user = None
if "is_guest" not in st.session_state: st.session_state.is_guest = False
if "messages" not in st.session_state: st.session_state.messages = []
if "pdf_text" not in st.session_state: st.session_state.pdf_text = ""

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(password, hashed_text): return make_hashes(password) == hashed_text

def extract_pdf_content(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content: text += content
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

# 4. Global UI Styling
st.markdown("""
<style>
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:25px; font-size: 20px; }
    div.stButton > button { background-color: #1a1a1a; color: #FFD700; border-radius: 10px; border: 1px solid #FFD700; height: 45px; font-weight: bold; }
    .guest-btn > div > button { background-color: #2b2b2b !important; color: #999 !important; border: 1px solid #444 !important; }
    .vault-card { background: #262626; border-left: 5px solid #FFD700; padding: 10px; border-radius: 5px; margin-bottom: 5px; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# 5. Security Portal (Login/Guest)
if not st.session_state.logged_in and not st.session_state.is_guest:
    st.markdown('<h1 style="text-align:center;">Alpha AI ⚡ Security Portal</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Register New"])
    
    with tab1:
        u_in = st.text_input("Username", key="login_user").lower().strip()
        p_in = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Access Alpha AI"):
            if u_in == "hasith123" and p_in == "hasith@alpha":
                st.session_state.logged_in = True
                st.session_state.current_user = "hasith123"
                if "vault" not in st.session_state.user_db.get(u_in, {}):
                    st.session_state.user_db[u_in] = {"vault": []}
                st.rerun()
            elif u_in in ["matheesha", "sadev"] or (u_in in st.session_state.user_db and check_hashes(p_in, st.session_state.user_db[u_in].get("password", ""))):
                st.session_state.logged_in = True
                st.session_state.current_user = u_in
                if u_in not in st.session_state.user_db: st.session_state.user_db[u_in] = {"vault": []}
                st.rerun()
            else:
                st.error("Invalid Credentials.")
        
        st.write("---")
        st.markdown('<div class="guest-btn">', unsafe_allow_html=True)
        if st.button("🔓 Free Guest Login"):
            st.session_state.is_guest = True
            st.session_state.current_user = "Guest"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        nu = st.text_input("New Username", key="reg_user")
        np = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Create Account"):
            if nu and nu.lower() not in ["hasith123", "matheesha", "sadev"]:
                st.session_state.user_db[nu.lower()] = {"password": make_hashes(np), "vault": []}
                st.success("Account created successfully!")
    st.stop()

# 6. Sidebar Menu
with st.sidebar:
    st.title("⚙️ Alpha Controls")
    st.write(f"Active User: **{st.session_state.current_user}**")
    
    st.subheader("📄 PDF Intelligence")
    uploaded_pdf = st.file_uploader("Upload PDF for Analysis", type=["pdf"])
    if uploaded_pdf:
        with st.spinner("Extracting PDF Data..."):
            st.session_state.pdf_text = extract_pdf_content(uploaded_pdf)
            st.success("PDF Data Synchronized!")
    
    st.subheader("🧠 Neural Vault")
    curr = st.session_state.current_user
    if not st.session_state.is_guest and curr in st.session_state.user_db:
        vault = st.session_state.user_db[curr].get("vault", [])
        if not vault: st.caption("No records found.")
        for m in vault[-2:]:
            st.markdown(f'<div class="vault-card">📌 {m}</div>', unsafe_allow_html=True)
    else:
        st.info("Vault disabled for Guest mode.")

    persona = st.selectbox("🎭 Persona:", ["Standard Alpha", "Image Creator 🎨", "Hasith Mode ⚡"])
    ai_mode = st.radio("🚀 Intelligence Level:", ["Normal (Fast)", "Pro (Deep Analysis)"])
    
    if st.button("Clear History"): st.session_state.messages = []; st.rerun()
    if st.button("Logout"): 
        st.session_state.logged_in = False
        st.session_state.is_guest = False
        st.rerun()

# 7. Main Header
st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

# 8. Chat History Display
v_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='v_rec')
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "img" in msg: st.image(msg["img"])

# 9. AI Logic Core
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
u_input = st.chat_input("Ask Alpha anything...")
final_q = v_text if v_text else u_input

if final_q:
    st.session_state.messages.append({"role": "user", "content": final_q})
    with st.chat_message("user"): st.markdown(final_q)

    # Memory Management
    if not st.session_state.is_guest and any(w in final_q.lower() for w in ["remember", "my name is", "i love"]):
        curr = st.session_state.current_user
        if "vault" not in st.session_state.user_db[curr]: st.session_state.user_db[curr]["vault"] = []
        st.session_state.user_db[curr]["vault"].append(final_q)

    with st.chat_message("assistant"):
        if persona == "Image Creator 🎨":
            img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(final_q)}?width=1024&height=1024&nologo=true"
            st.image(img_url)
            st.session_state.messages.append({"role": "assistant", "content": "Visual generated.", "img": img_url})
        else:
            is_pro = "Pro" in ai_mode
            thinking_text = "Alpha's ultra thinking..." if is_pro else "Alpha is thinking..."
            
            with st.spinner(thinking_text):
                # Clean history (fix for 400 error)
                clean_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-10:]]
                
                pdf_context = f"Document Content: {st.session_state.pdf_text[:5000]}" if st.session_state.pdf_text else ""
                sys_prompt = f"You are Alpha AI by Hasith. Mode: {ai_mode}. {pdf_context}. Be precise."
                
                try:
                    stream = client.chat.completions.create(
                        model="openai/gpt-oss-120b" if is_pro else "llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": sys_prompt}] + clean_history,
                        stream=True
                    )
                    full_res = ""
                    res_area = st.empty()
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            full_res += chunk.choices[0].delta.content
                            res_area.markdown(full_res + "▌")
                    res_area.markdown(full_res)
                    st.session_state.messages.append({"role": "assistant", "content": full_res})
                    
                    # --- VOICE OUTPUT SYSTEM ---
                    tts = gTTS(text=full_res[:250], lang='en')
                    tts.save("response.mp3")
                    with open("response.mp3", "rb") as f:
                        audio_bytes = f.read()
                        st.audio(audio_bytes, format="audio/mp3")
                        # Auto-play attempt
                        b64 = base64.b64encode(audio_bytes).decode()
                        st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
                    os.remove("response.mp3")
                    
                except Exception as e:
                    st.error(f"Neural Sync Error: {e}")
