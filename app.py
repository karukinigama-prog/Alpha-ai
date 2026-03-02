import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from PIL import Image
import sys
from io import StringIO

# --- 1. Database Setup ---
conn = sqlite3.connect('alpha_master_v6.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT UNIQUE, password TEXT, word_count INTEGER DEFAULT 0)')
c.execute('CREATE TABLE IF NOT EXISTS feedback_table(username TEXT, feedback TEXT, date TEXT)')
conn.commit()

# --- 2. Helper Functions ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password =?', (username, password))
    return c.fetchone()

# --- 3. Page Configuration & Ultra-Metallic UI ---
st.set_page_config(page_title="Alpha AI Master", page_icon="⚡", layout="wide")

# Advanced CSS for 3D Metallic Chrome Effect
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');
    
    .master-metallic {
        font-family: 'Orbitron', sans-serif;
        font-size: 100px; /* Larger Header */
        font-weight: 900;
        text-align: center;
        background: linear-gradient(to bottom, #bcc6cc 0%, #eee 50%, #828282 51%, #333 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(5px 5px 15px rgba(0,0,0,0.9));
        margin-bottom: 0px;
        letter-spacing: 10px;
    }
    .creator-tag {
        text-align: center;
        color: #7f8c8d;
        font-size: 22px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 8px;
        margin-top: -20px;
        margin-bottom: 30px;
    }
    .cap-card {
        background: linear-gradient(145deg, #1e1e1e, #252525);
        border: 1px solid #444;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# Main Header
st.markdown('<p class="master-metallic">⚡ ALPHA AI ⚡</p>', unsafe_allow_html=True)
st.markdown('<p class="creator-tag">Created by Hasith</p>', unsafe_allow_html=True)

# --- 4. Capabilities Dashboard ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="cap-card">📑 <b>SUMMARIZE</b><br>Instant key insights</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="cap-card">👁️ <b>VISION</b><br>AI Image Recognition</div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="cap-card">💻 <b>CODE</b><br>Python Interpreter</div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="cap-card">🌍 <b>GLOBAL</b><br>Multi-Language Support</div>', unsafe_allow_html=True)

st.markdown("---")

# --- 5. Authentication System ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.logged_in:
    login_cols = st.columns([1, 1.5, 1])
    with login_cols[1]:
        mode = st.tabs(["🔑 LOGIN", "📝 REGISTER", "👑 CREATOR BYPASS"])
        
        with mode[0]:
            u = st.text_input("Username")
            p = st.text_input("Password", type='password')
            if st.button("Unlock Alpha"):
                if login_user(u, make_hashes(p)):
                    st.session_state.logged_in, st.session_state.username = True, u
                    st.rerun()
                else: st.error("Access Denied.")

        with mode[1]:
            new_u = st.text_input("New User")
            new_p = st.text_input("New Pass", type='password')
            if st.button("Create Account"):
                if new_u == "hasith12356": st.error("Name Reserved.")
                elif add_userdata(new_u, make_hashes(new_p)): st.success("Created!")
                else: st.error("Exists.")

        with mode[2]:
            st.info("Direct Access for Hasith")
            secret = st.text_input("Admin Key", type='password')
            if st.button("Bypass Security"):
                if secret == "hasith12356":
                    st.session_state.logged_in, st.session_state.username = True, "hasith12356"
                    st.rerun()
                else: st.error("Unauthorized.")

# --- 6. The AI Dashboard ---
else:
    with st.sidebar:
        st.title(f"👤 {st.session_state.username}")
        st.write(f"📅 {datetime.now().strftime('%Y-%m-%d')} | ⏰ {datetime.now().strftime('%H:%M:%S')}")
        st.markdown("---")
        
        ai_mode = st.radio("Intelligence Mode:", ["Normal", "Pro"])
        
        up_img = st.file_uploader("📸 Image Input", type=['jpg', 'jpeg', 'png'])
        
        if st.button("📄 Summarize Conversation"):
            st.session_state.messages.append({"role": "user", "content": "Summarize this entire conversation."})
            st.rerun()
        
        if st.session_state.username == "hasith12356":
            st.success("👑 MASTER ADMIN")
            if st.checkbox("Show Usage Stats"):
                c.execute('SELECT username, word_count FROM userstable')
                for r in c.fetchall(): st.write(f"• {r[0]}: {r[1]} words")

        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # Gemini 2.5 Setup
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.5-flash")
    except:
        st.error("API Key missing.")
        st.stop()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Command Alpha..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        # Mode-based Status
        status = "Alpha 2.5 thinking..." if ai_mode == "Normal" else "Alpha's ultra thinking..."
        
        try:
            with st.chat_message("assistant"):
                with st.spinner(status):
                    # Deep Persona
                    if ai_mode == "Normal":
                        sys_p = "Detailed, simple, and long explanation. Created by Hasith."
                    else:
                        sys_p = "Extremely deep, professional, technical, and comprehensive. Created by Hasith."
                    
                    payload = [f"Mode: {ai_mode}\nTask: {sys_p}\nInput: {prompt}"]
                    if up_img: payload.append(Image.open(up_img))
                    
                    response = model.generate_content(payload)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                    # Update Analytics
                    count = len(prompt.split()) + len(response.text.split())
                    c.execute('UPDATE userstable SET word_count = word_count + ? WHERE username = ?', (count, st.session_state.username))
                    conn.commit()
        except Exception as e: st.error(e)
