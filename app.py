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
            if content:
                text += content
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

# 4. Styling
st.markdown("""
<style>
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:25px; font-size: 20px; }
    div.stButton > button { background-color: #1a1a1a; color: #FFD700; border-radius: 10px; border: 1px solid #FFD700; height: 45px; font-weight: bold; }
    .guest-btn > div > button { background-color: #2b2b2b !important; color: #999 !important; border: 1px solid #444 !important; }
    .vault-card { background: #262626; border-left: 5px solid #FFD700; padding: 10px; border-radius: 5px; margin-bottom: 5px; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# 5. Security Portal
if not st.session_state.logged_in and not st.session_state.is_guest:
    st.markdown('<h1 style="text-align:center;">Alpha AI ⚡ Security Portal</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Register New"])
    
    with tab1:
        u_in = st.text_input("Username", key="login_user").lower().strip()
        p_in = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Access Alpha AI"):
            if u_in == "hasith123" and p_in == "hasith@alpha":
                st.session_state.logged_in = True
                st.session_state.current_user = "Hasith (Admin)"
                st.rerun()
            elif u_in in ["matheesha", "sadev"]:
                st.session_state.logged_in = True
                st.session_state.current_user = u_in
                st.rerun()
            elif u_in in st.session_state.user_db and check_hashes(p_in, st.session_state.user_db[u_in]["password"]):
                st.session_state.logged_in = True
                st.session_state.current_user = u_in
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

# 6. Sidebar
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
    if not st.session_state.is_guest:
        curr = st.session_state.current_user if st.session_state.current_user in st.session_state.user_db else "matheesha"
        vault = st.session_state.user_db.get(curr, {}).get("vault", [])
        if not vault: st.caption("No records.")
        for m in vault[-2:]:
            st.markdown(f'<div class="vault-card">📌 {m}</div>', unsafe_allow_html=True)
    else:
        st.info("Vault disabled for Guest.")

    persona = st.selectbox("🎭 Persona:", ["Standard Alpha", "Image Creator 🎨", "Hasith Mode ⚡"])
    ai_mode = st.radio("🚀 Intelligence:", ["Normal (Fast)", "Pro (Deep Analysis)"])
    
    st.subheader("💻 Alpha Sandbox")
    code_input = st.text_area("Python Editor:", "print('Alpha Active')")
    if st.button("Execute"):
        try:
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            exec(code_input)
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            st.code(output, language='python')
        except Exception as e:
            st.error(e)

    if st.button("Clear History"): st.session_state.messages = []; st.rerun()
    if st.button("Logout"): 
        st.session_state.logged_in = False
        st.session_state.is_guest = False
        st.rerun()

# 7. Main UI Header
st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith <span style="font-size:12px; opacity:0.8;">[{persona}]</span></div>', unsafe_allow_html=True)

# 8. Chat Interface
v_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='v1')
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
        curr = st.session_state.current_user if st.session_state.current_user in st.session_state.user_db else "matheesha"
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
                # Integrating PDF context into prompt
                pdf_context = f"\n\n[ATTACHED DOCUMENT DATA]: {st.session_state.pdf_text[:6000]}" if st.session_state.pdf_text else ""
                
                system_msg = (
                    f"You are Alpha AI by Hasith. Identity: Advanced Assistant. "
                    f"Mode: {ai_mode}. {pdf_context}. "
                    f"Creator: Hasith. Strictly avoid OpenAI/Meta mentions."
                )
                
                clean_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-10:]]
                
                try:
                    stream = client.chat.completions.create(
                        model="openai/gpt-oss-120b" if is_pro else "llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": system_msg}] + clean_history,
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
                    
                    # Optional Voice Output (First 200 chars)
                    audio_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={urllib.parse.quote(full_res[:200])}&tl=en&client=tw-ob"
                    st.audio(audio_url, format="audio/mp3")
                except Exception as e:
                    st.error(f"Neural Error: {e}")
