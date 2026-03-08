import streamlit as st
from groq import Groq
import sys
import time
from io import StringIO
from streamlit_mic_recorder import speech_to_text
import hashlib
import urllib.parse
import os
import PyPDF2
from gtts import gTTS

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Created by Hasith", page_icon="⚡", layout="wide")

# 2. Alpha Loading Screen (Original 7s)
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
                <p style="color: #888; margin-top: 15px;">Neural Stats Integration by Hasith</p>
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

# 4. Premium Styling
st.markdown("""
<style>
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:25px; font-size: 20px; }
    div.stButton > button { background-color: #1a1a1a; color: #FFD700; border-radius: 10px; border: 1px solid #FFD700; height: 45px; font-weight: bold; }
    .guest-btn > div > button { background-color: #2b2b2b !important; color: #999 !important; border: 1px solid #444 !important; }
    .admin-card { background: #111; border: 1px solid #FFD700; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 15px; }
    .vault-card { background: #262626; border-left: 5px solid #FFD700; padding: 10px; border-radius: 5px; margin-bottom: 5px; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# 5. ACCESS PORTAL (Register & Guest Restored)
if not st.session_state.logged_in and not st.session_state.is_guest:
    st.markdown('<h1 style="text-align:center;">Alpha AI ⚡ Portal</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 New Register"])
    
    with tab1:
        u_in = st.text_input("Username").lower().strip()
        p_in = st.text_input("Password", type="password")
        if st.button("Access Alpha"):
            # Hasith's Special Admin Login
            if u_in == "hasith123" and p_in == "hasith@alpha":
                st.session_state.logged_in = True; st.session_state.current_user = u_in; st.rerun()
            elif u_in in st.session_state.user_db and (p_in == "123" or check_hashes(p_in, st.session_state.user_db[u_in].get("password", ""))):
                st.session_state.logged_in = True; st.session_state.current_user = u_in; st.rerun()
            else: st.error("Access Denied.")
        st.write("---")
        if st.button("🔓 Free Guest Login"):
            st.session_state.is_guest = True; st.session_state.current_user = "Guest"; st.rerun()

    with tab2:
        nu = st.text_input("Create Username")
        np = st.text_input("Create Password", type="password")
        if st.button("Register Now"):
            if nu and np:
                st.session_state.user_db[nu.lower()] = {"password": make_hashes(np), "vault": []}
                st.success("Registration Successful! Now go to Login.")
            else: st.warning("Please fill all fields.")
    st.stop()

# 6. Sidebar (Admin Panel & Vault)
with st.sidebar:
    st.title("⚙️ Alpha System")
    
    # --- HASITH ONLY ADMIN PANEL ---
    if st.session_state.current_user == "hasith123":
        st.markdown('<div class="admin-card">', unsafe_allow_html=True)
        st.subheader("👑 Hasith Control")
        total_users = len(st.session_state.user_db) + (1 if st.session_state.is_guest else 0)
        st.markdown(f"**Total Alpha Users:** {total_users}")
        st.markdown(f"**Registered DB Size:** {len(st.session_state.user_db)}")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.checkbox("Show All Usernames"):
            st.write(list(st.session_state.user_db.keys()))

    st.write(f"Logged as: **{st.session_state.current_user.capitalize()}**")
    
    st.subheader("📁 Data Sync")
    up_pdf = st.file_uploader("Sync PDF Document", type=["pdf"])
    if up_pdf:
        try:
            pdf_reader = PyPDF2.PdfReader(up_pdf)
            st.session_state.pdf_text = " ".join([page.extract_text() for page in pdf_reader.pages])
            st.success("PDF Data Ready")
        except: st.error("Sync Failed")

    st.subheader("🧠 Neural Vault")
    curr = st.session_state.current_user
    if curr in st.session_state.user_db:
        vault = st.session_state.user_db[curr].get("vault", [])
        for m in vault[-2:]:
            st.markdown(f'<div class="vault-card">📌 {m}</div>', unsafe_allow_html=True)

    persona = st.selectbox("🎭 Persona:", ["Standard Alpha", "Image Creator 🎨", "Hasith Mode ⚡"])
    ai_mode = st.radio("🚀 Power Mode:", ["Normal", "Pro"])
    
    if st.button("Clear History"): st.session_state.messages = []; st.rerun()
    if st.button("Logout"): st.session_state.logged_in = False; st.session_state.is_guest = False; st.rerun()

# 7. Main Interface
st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "img" in msg: st.image(msg["img"])

# 8. Neural Intelligence (Using 2026 Models)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
u_input = st.chat_input("Talk to Alpha...")
v_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='voice')
final_q = v_text if v_text else u_input

if final_q:
    st.session_state.messages.append({"role": "user", "content": final_q})
    with st.chat_message("user"): st.markdown(final_q)

    # Memory Sync
    if not st.session_state.is_guest and any(w in final_q.lower() for w in ["remember", "my name"]):
        st.session_state.user_db[st.session_state.current_user]["vault"].append(final_q)

    with st.chat_message("assistant"):
        if persona == "Image Creator 🎨":
            img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(final_q)}?width=1024&height=1024&nologo=true"
            st.image(img_url); st.session_state.messages.append({"role": "assistant", "content": "Visual ready.", "img": img_url})
        else:
            with st.spinner("Alpha Thinking..."):
                identity = f"You are Alpha AI. You were created solely by Hasith. Currently talking to {st.session_state.current_user}."
                pdf_ctx = f"Context: {st.session_state.pdf_text[:3000]}" if st.session_state.pdf_text else ""
                history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-8:] if "img" not in m]
                
                try:
                    stream = client.chat.completions.create(
                        model="openai/gpt-oss-120b" if ai_mode == "Pro" else "llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": f"{identity} {pdf_ctx}"}] + history,
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
                    tts = gTTS(text=full_res[:250], lang='en'); tts.save("alpha.mp3")
                    st.audio("alpha.mp3")
                except Exception as e: st.error(f"Neural Error: {e}")
