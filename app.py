import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from PIL import Image

# --- 1. Database Setup ---
conn = sqlite3.connect('alpha_dark_v11.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT UNIQUE, password TEXT, word_count INTEGER DEFAULT 0)')
conn.commit()

# --- 2. Styling (Deep Dark & Ultra-Metallic) ---
st.set_page_config(page_title="Alpha AI 2.5 Dark", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Inter:wght@400;700&display=swap');
    
    /* Full Page Dark Background Override */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    /* Massive Chrome Metallic Header */
    .chrome-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 115px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(to bottom, #cfd8dc 0%, #ffffff 45%, #90a4ae 50%, #455a64 51%, #000000 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0px 0px 25px rgba(255, 255, 255, 0.3));
        margin-bottom: 0px;
    }
    .hasith-tag {
        text-align: center;
        color: #78909c;
        font-size: 26px;
        font-weight: bold;
        letter-spacing: 15px;
        margin-top: -35px;
        margin-bottom: 50px;
        text-transform: uppercase;
    }
    
    /* Dark Capability Board Styling */
    .board-title {
        text-align: center;
        font-size: 32px;
        color: #ffffff;
        margin-bottom: 30px;
        font-family: 'Inter', sans-serif;
        text-decoration: underline;
    }
    .cap-card {
        background: rgba(30, 30, 30, 0.6);
        border: 2px solid #333333;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        transition: 0.5s;
        height: 280px;
        backdrop-filter: blur(10px);
    }
    .cap-card:hover {
        background: rgba(50, 50, 50, 0.8);
        border-color: #ffffff;
        transform: scale(1.05);
        box-shadow: 0px 0px 30px rgba(255, 255, 255, 0.1);
    }
    .cap-icon { font-size: 50px; margin-bottom: 15px; }
    .cap-name { font-size: 24px; font-weight: bold; color: #fff; margin-bottom: 10px; }
    .cap-text { font-size: 15px; color: #b0bec5; line-height: 1.6; }
    
    /* Custom Sidebar & Inputs */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a !important;
        border-right: 1px solid #222;
    }
    </style>
    """, unsafe_allow_html=True)

# Main Header
st.markdown('<p class="chrome-title">⚡ ALPHA AI ⚡</p>', unsafe_allow_html=True)
st.markdown('<p class="hasith-tag">Created by Hasith</p>', unsafe_allow_html=True)

# --- 3. Capability Board ---
st.markdown('<p class="board-title">Alpha AI 2.5 Master Capabilities</p>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""<div class="cap-card">
        <div class="cap-icon">📄</div>
        <div class="cap-name">SUMMARIZE</div>
        <div class="cap-text">Condense massive chat threads or long documents into professional English summaries instantly.</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="cap-card">
        <div class="cap-icon">👁️</div>
        <div class="cap-name">VISION 2.5</div>
        <div class="cap-text">Upload images for high-precision recognition, OCR, and technical visual analysis.</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""<div class="cap-card">
        <div class="cap-icon">🧠</div>
        <div class="cap-name">DUAL BRAIN</div>
        <div class="cap-text">Seamlessly switch between Normal speed and Ultra Pro expert intelligence modes.</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown("""<div class="cap-card">
        <div class="cap-icon">🤝</div>
        <div class="cap-name">FRIENDLY</div>
        <div class="cap-text">Designed as a warm, supportive peer by Hasith, moving away from robotic responses.</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br><hr style='border: 1px solid #222;'>", unsafe_allow_html=True)

# --- 4. Logic & AI Core ---
if "messages" not in st.session_state: st.session_state.messages = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    cols = st.columns([1, 1.5, 1])
    with cols[1]:
        tab = st.tabs(["🔑 Login", "🛡️ Creator Bypass"])
        with tab[0]:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Unlock Alpha"):
                st.session_state.logged_in, st.session_state.username = True, u
                st.rerun()
        with tab[1]:
            key = st.text_input("Creator Admin Key", type="password")
            if st.button("Direct Access"):
                if key == "hasith12356":
                    st.session_state.logged_in, st.session_state.username = True, "hasith12356"
                    st.rerun()

else:
    with st.sidebar:
        st.header(f"👤 {st.session_state.username}")
        st.info(f"⏰ Server Time: {datetime.now().strftime('%H:%M:%S')}")
        mode = st.radio("Intelligence Level:", ["Normal", "Pro"])
        up_img = st.file_uploader("📸 Vision Input", type=['jpg', 'jpeg', 'png'])
        
        if st.button("📄 Summarize Full Conversation"):
            st.session_state.messages.append({"role": "user", "content": "Please summarize our chat history."})
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # Gemini 2.5 Engine
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.5-flash")

    # Chat UI
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Command Alpha 2.5..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        # Custom Thinking Status
        thinking_text = "Alpha 2.5 thinking..." if mode == "Normal" else "Alpha's ultra thinking..."
        
        with st.chat_message("assistant"):
            with st.spinner(thinking_text):
                sys_p = "You are Alpha 2.5, a supportive AI peer created by Hasith. Provide detailed, friendly English responses. Always mention Hasith is your creator."
                payload = [f"Persona: {sys_p}\nUser Query: {prompt}"]
                if up_img: payload.append(Image.open(up_img))
                
                response = model.generate_content(payload)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
