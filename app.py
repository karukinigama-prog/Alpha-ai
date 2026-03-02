import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from PIL import Image

# --- 1. Database Setup ---
conn = sqlite3.connect('alpha_final_elite.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT UNIQUE, password TEXT, word_count INTEGER DEFAULT 0)')
conn.commit()

# --- 2. THE ULTIMATE METALLIC GLASS UI ---
st.set_page_config(page_title="Alpha AI 2.5 Elite", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Inter:wght@400;700&display=swap');
    
    /* Full Page - Pure Black */
    .stApp {
        background-color: #000000;
    }

    /* 115px Massive Chrome Header */
    .chrome-header {
        font-family: 'Orbitron', sans-serif;
        font-size: 115px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(180deg, #ffffff 10%, #9ea7ad 45%, #4e5a61 55%, #1a1a1a 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 25px rgba(255, 255, 255, 0.2));
        margin-bottom: -15px;
    }
    
    .hasith-tag {
        text-align: center;
        color: #00d4ff;
        font-size: 26px;
        font-weight: bold;
        letter-spacing: 15px;
        text-transform: uppercase;
        text-shadow: 0 0 15px #00d4ff;
        margin-bottom: 50px;
    }

    /* GLASSMORPHISM CHAT BUBBLES - PURE WHITE TEXT */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 25px !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
        backdrop-filter: blur(10px) !important;
    }

    /* Ensure all text inside bubbles is Pure White */
    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] li, 
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] code {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
        font-size: 17.5px !important;
        line-height: 1.6 !important;
    }
    
    /* AI Response Glow & Cyan Border */
    [data-testid="stChatMessage"]:nth-child(even) {
        border: 1px solid rgba(0, 212, 255, 0.4) !important;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.15) !important;
        background: rgba(0, 212, 255, 0.03) !important;
    }

    /* Capability Cards - Metallic Theme */
    .cap-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid #333;
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        transition: 0.4s ease;
    }
    .cap-card:hover {
        border-color: #00d4ff;
        transform: translateY(-8px);
        box-shadow: 0 0 25px rgba(0, 212, 255, 0.2);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 1px solid #222 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Main Branding
st.markdown('<p class="chrome-header">ALPHA AI</p>', unsafe_allow_html=True)
st.markdown('<p class="hasith-tag">Developed by Hasith</p>', unsafe_allow_html=True)

# --- 3. Capability Board ---
st.markdown('<p style="text-align:center; color:#888; font-size:18px;">Powered by Gemini 2.5 Flash Engine</p>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown('<div class="cap-card"><h2 style="margin:0;">📄</h2><b style="color:white;">SUMMARIZE</b><p style="color:#777;font-size:13px;margin:0;">Instant Chat Analysis</p></div>', unsafe_allow_html=True)
with c2: st.markdown('<div class="cap-card"><h2 style="margin:0;">👁️</h2><b style="color:white;">VISION 2.5</b><p style="color:#777;font-size:13px;margin:0;">Image Data OCR</p></div>', unsafe_allow_html=True)
with c3: st.markdown('<div class="cap-card"><h2 style="margin:0;">🧠</h2><b style="color:white;">DUAL BRAIN</b><p style="color:#777;font-size:13px;margin:0;">Normal & Pro Modes</p></div>', unsafe_allow_html=True)
with c4: st.markdown('<div class="cap-card"><h2 style="margin:0;">🤝</h2><b style="color:white;">FRIENDLY</b><p style="color:#777;font-size:13px;margin:0;">Peer Personality</p></div>', unsafe_allow_html=True)

st.markdown("<br><hr style='border: 0.1px solid #222;'><br>", unsafe_allow_html=True)

# --- 4. Logic & Gemini Core ---
if "messages" not in st.session_state: st.session_state.messages = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # (Bypass or Login Logic)
    st.session_state.logged_in = True
    st.session_state.username = "hasith12356"
else:
    with st.sidebar:
        st.header(f"👤 {st.session_state.username}")
        mode = st.radio("Intelligence Level:", ["Normal", "Pro"])
        up_img = st.file_uploader("📸 Vision Input", type=['jpg', 'jpeg', 'png'])
        
        if st.button("📄 Summarize Full Chat"):
            st.session_state.messages.append({"role": "user", "content": "Please provide a clear summary of our chat history."})
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # Display History
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Handle Input & Statuses
    if prompt := st.chat_input("Command Alpha 2.5..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        # Custom Thinking Statuses
        thinking_txt = "Alpha 2.5 thinking..." if mode == "Normal" else "Alpha's ultra thinking..."
        
        with st.chat_message("assistant"):
            with st.spinner(thinking_txt):
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                sys_p = "You are Alpha 2.5, a sophisticated AI peer created by Hasith. Provide long, warm, and expert-level English responses."
                payload = [f"{sys_p}\nUser Query: {prompt}"]
                if up_img: payload.append(Image.open(up_img))
                
                response = model.generate_content(payload)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
