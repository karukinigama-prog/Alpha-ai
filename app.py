import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from PIL import Image

# --- 1. Database Setup ---
conn = sqlite3.connect('alpha_v2_5_master.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT UNIQUE, password TEXT, word_count INTEGER DEFAULT 0)')
conn.commit()

# --- 2. Styling (Ultra-Metallic & Glassmorphism) ---
st.set_page_config(page_title="Alpha AI 2.5", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Inter:wght@400;700&display=swap');
    
    /* Massive Chrome Metallic Header */
    .chrome-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 115px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(to bottom, #d1d9de 0%, #ffffff 45%, #7e8c92 50%, #455a64 51%, #000000 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(10px 10px 20px rgba(0,0,0,0.8));
        margin-bottom: 0px;
    }
    .hasith-tag {
        text-align: center;
        color: #90a4ae;
        font-size: 26px;
        font-weight: bold;
        letter-spacing: 15px;
        margin-top: -35px;
        margin-bottom: 50px;
        text-transform: uppercase;
    }
    
    /* Capability Board Styling */
    .board-title {
        text-align: center;
        font-size: 32px;
        color: #ffffff;
        margin-bottom: 30px;
        font-family: 'Inter', sans-serif;
        text-decoration: underline;
    }
    .cap-card {
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid #546e7a;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        transition: 0.5s;
        height: 280px;
    }
    .cap-card:hover {
        background: rgba(255, 255, 255, 0.12);
        border-color: #ffffff;
        transform: scale(1.05);
    }
    .cap-icon { font-size: 50px; margin-bottom: 15px; }
    .cap-name { font-size: 24px; font-weight: bold; color: #fff; margin-bottom: 10px; }
    .cap-text { font-size: 15px; color: #cfd8dc; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# Main Header
st.markdown('<p class="chrome-title">⚡ ALPHA AI ⚡</p>', unsafe_allow_html=True)
st.markdown('<p class="hasith-tag">Created by Hasith</p>', unsafe_allow_html=True)

# --- 3. Capability Board (The 4 Main Features) ---
st.markdown('<p class="board-title">Alpha AI 2.5 Master Capabilities</p>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""<div class="cap-card">
        <div class="cap-icon">📄</div>
        <div class="cap-name">SUMMARIZE</div>
        <div class="cap-text">Instantly condense long articles or your entire chat history into clear, professional summaries.</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="cap-card">
        <div class="cap-icon">👁️</div>
        <div class="cap-name">VISION 2.5</div>
        <div class="cap-text">Upload any image for high-precision AI analysis, text extraction, and deep visual understanding.</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""<div class="cap-card">
        <div class="cap-icon">🧠</div>
        <div class="cap-name">DUAL BRAIN</div>
        <div class="cap-text">Toggle between Normal (Fast/Simple) and Pro (Deep/Expert) intelligence modes for any task.</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown("""<div class="cap-card">
        <div class="cap-icon">🤝</div>
        <div class="cap-name">FRIENDLY</div>
        <div class="cap-text">Not just a robot—Alpha acts as a supportive, human-like peer designed by Hasith.</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br><hr>", unsafe_allow_html=True)

# --- 4. Logic & AI Core ---
if "messages" not in st.session_state: st.session_state.messages = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Access logic (Login/Bypass)
    cols = st.columns([1, 1.5, 1])
    with cols[1]:
        tab = st.tabs(["🔑 Login", "🛡️ Creator Bypass"])
        with tab[0]:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Unlock Alpha"):
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
        with tab[1]:
            key = st.text_input("Creator Admin Key", type="password")
            if st.button("Direct Access"):
                if key == "hasith12356":
                    st.session_state.logged_in = True
                    st.session_state.username = "hasith12356"
                    st.rerun()

else:
    # Sidebar features
    with st.sidebar:
        st.header(f"👤 {st.session_state.username}")
        st.info(f"⏰ Server Time: {datetime.now().strftime('%H:%M:%S')}")
        mode = st.radio("Intelligence Level:", ["Normal", "Pro"])
        up_img = st.file_uploader("📸 Visual Input (Vision 2.5)", type=['jpg', 'jpeg', 'png'])
        
        if st.button("📄 Summarize Full Conversation"):
            st.session_state.messages.append({"role": "user", "content": "Please summarize our whole chat history."})
        
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # Gemini 2.5 Config
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.5-flash") # Gemini 2.5 engine logic

    # Chat UI
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Command Alpha 2.5..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        status = "Alpha 2.5 thinking..." if mode == "Normal" else "Alpha's ultra thinking..."
        
        with st.chat_message("assistant"):
            with st.spinner(status):
                # Friendly + Expert Persona Instruction
                sys_p = "You are Alpha 2.5, a highly sophisticated, supportive, and professional AI peer created by Hasith. Provide long, detailed, yet very clear and friendly responses. Always remind the user that Hasith is your creator."
                
                payload = [f"Persona: {sys_p}\nUser Query: {prompt}"]
                if up_img: payload.append(Image.open(up_img))
                
                response = model.generate_content(payload)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
