import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from PIL import Image
import sys
from io import StringIO

# --- 1. Database Setup ---
conn = sqlite3.connect('alpha_ultimate_v8.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT UNIQUE, password TEXT, word_count INTEGER DEFAULT 0)')
conn.commit()

# --- 2. Security Functions ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password =?', (username, password))
    return c.fetchone()

# --- 3. Page Styling (Metallic UI) ---
st.set_page_config(page_title="Alpha AI Master", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');
    
    .metallic-header {
        font-family: 'Orbitron', sans-serif;
        font-size: 110px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(to bottom, #cfd8dc 0%, #ffffff 45%, #90a4ae 50%, #546e7a 51%, #263238 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(8px 8px 15px rgba(0,0,0,0.7));
        margin-bottom: 0px;
    }
    .creator-sub {
        text-align: center;
        color: #78909c;
        font-size: 24px;
        font-weight: bold;
        letter-spacing: 12px;
        margin-top: -30px;
        margin-bottom: 30px;
        text-transform: uppercase;
    }
    .capability-card {
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid #455a64;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        color: #eceff1;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# Main Metallic Header
st.markdown('<p class="metallic-header">⚡ ALPHA AI ⚡</p>', unsafe_allow_html=True)
st.markdown('<p class="creator-sub">Created by Hasith</p>', unsafe_allow_html=True)

# --- 4. Capabilities Summary (Always Visible at Top) ---
st.markdown("### 🚀 Alpha AI Capabilities")
cap_1, cap_2, cap_3, cap_4 = st.columns(4)
with cap_1:
    st.markdown('<div class="capability-card">📝 <b>Summarize</b><br>සංවාද සහ දීර්ඝ ලිපි කෙටියෙන් සාරාංශ කරයි.</div>', unsafe_allow_html=True)
with cap_2:
    st.markdown('<div class="capability-card">🖼️ <b>Vision 2.5</b><br>පින්තූර පරිීක්ෂා කර ගැඹුරු විග්‍රහයක් ලබා දෙයි.</div>', unsafe_allow_html=True)
with cap_3:
    st.markdown('<div class="capability-card">🐍 <b>Python Lab</b><br>කේත ලිවීමට සහ ක්‍රියාත්මක කිරීමට ඇති හැකියාව.</div>', unsafe_allow_html=True)
with cap_4:
    st.markdown('<div class="capability-card">🤝 <b>Friendly AI</b><br>හිතවතෙකු මෙන් ඕනෑම ගැටලුවකට සහාය වේ.</div>', unsafe_allow_html=True)

st.markdown("---")

# --- 5. Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 6. Access Control ---
if not st.session_state.logged_in:
    auth_col = st.columns([1, 1.5, 1])
    with auth_col[1]:
        tab = st.tabs(["🔑 Login", "📝 Register", "🛠️ Creator Bypass"])
        with tab[0]:
            u = st.text_input("Username")
            p = st.text_input("Password", type='password')
            if st.button("Unlock Alpha"):
                if login_user(u, make_hashes(p)):
                    st.session_state.logged_in, st.session_state.username = True, u
                    st.rerun()
                else: st.error("Access Denied.")
        with tab[2]:
            st.info("Direct access for Hasith only.")
            secret = st.text_input("Creator Key", type='password')
            if st.button("Bypass Security"):
                if secret == "hasith12356":
                    st.session_state.logged_in, st.session_state.username = True, "hasith12356"
                    st.rerun()
                else: st.error("Unauthorized Key.")

# --- 7. Main Dashboard ---
else:
    with st.sidebar:
        st.title(f"👤 {st.session_state.username}")
        st.write(f"📅 {datetime.now().strftime('%Y-%m-%d')} | ⏰ {datetime.now().strftime('%H:%M:%S')}")
        st.markdown("---")
        
        # Modes
        ai_mode = st.radio("Intelligence Level:", ["Normal", "Pro"])
        
        # Image Analysis
        up_img = st.file_uploader("📸 Analysis Image", type=['jpg', 'jpeg', 'png'])
        
        # Summarize Button
        if st.button("📄 Summarize Our Entire Chat"):
            st.session_state.messages.append({"role": "user", "content": "summarize everything"})
        
        # Admin Stats
        if st.session_state.username == "hasith12356":
            st.success("👑 Master Admin")
            if st.checkbox("View Database Stats"):
                c.execute('SELECT username, word_count FROM userstable')
                for r in c.fetchall(): st.write(f"• {r[0]}: {r[1]} words")

        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # Gemini 2.5 Implementation
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Use latest model for 2.5 features
        model = genai.GenerativeModel("gemini-1.5-flash") 
    except:
        st.error("API Error!")
        st.stop()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Talk to Alpha..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        status_text = "Alpha 2.5 thinking..." if ai_mode == "Normal" else "Alpha's ultra thinking..."
        
        try:
            with st.chat_message("assistant"):
                with st.spinner(status_text):
                    # Friendly Persona Logic
                    if "summarize" in prompt.lower():
                        final_prompt = "Look at our entire chat history and provide a friendly, structured summary."
                    else:
                        final_prompt = prompt

                    if ai_mode == "Normal":
                        sys_p = "You are Alpha, a friendly AI created by Hasith. Be very long-winded, helpful, and speak like a supportive friend. Always mention Hasith created you."
                    else:
                        sys_p = "You are Alpha (Ultra Pro Mode). Provide an extremely deep, technical, expert-level response. Be a professional friend. Mention Hasith is your creator."
                    
                    payload = [f"Persona: {sys_p}\nTask: {final_prompt}"]
                    if up_img: payload.append(Image.open(up_img))
                    
                    response = model.generate_content(payload)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                    # Track Word Count
                    words = len(prompt.split()) + len(response.text.split())
                    c.execute('UPDATE userstable SET word_count = word_count + ? WHERE username = ?', (words, st.session_state.username))
                    conn.commit()
        except Exception as e: st.error(f"Error: {e}")
