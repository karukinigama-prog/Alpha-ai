import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from PIL import Image
import sys
from io import StringIO

# --- 1. Database Setup ---
conn = sqlite3.connect('alpha_master_final.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT UNIQUE, password TEXT, word_count INTEGER DEFAULT 0)')
conn.commit()

# --- 2. Security ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password =?', (username, password))
    return c.fetchone()

# --- 3. UI Styling (Lohamaya Metallic) ---
st.set_page_config(page_title="Alpha AI Master", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');
    
    .lohamaya-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 115px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(to bottom, #d1d9de 0%, #ffffff 45%, #7e8c92 50%, #455a64 51%, #000000 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(10px 10px 20px rgba(0,0,0,0.9));
        margin-bottom: 0px;
    }
    .hasith-tag {
        text-align: center;
        color: #90a4ae;
        font-size: 26px;
        font-weight: bold;
        letter-spacing: 15px;
        margin-top: -35px;
        margin-bottom: 40px;
        text-transform: uppercase;
    }
    .capability-card {
        background: rgba(255, 255, 255, 0.03);
        border: 2px solid #546e7a;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        color: #fff;
        transition: 0.4s;
    }
    .capability-card:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# Main Header
st.markdown('<p class="lohamaya-title">⚡ ALPHA AI ⚡</p>', unsafe_allow_html=True)
st.markdown('<p class="hasith-tag">Created by Hasith</p>', unsafe_allow_html=True)

# Capabilities Summary Board
st.markdown("### 🛠️ Alpha AI Intelligence Hub")
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown('<div class="capability-card">📊 <b>Smart Summary</b><br>සම්පූර්ණ සංවාදයම තත්පරයකින් සාරාංශ කරයි.</div>', unsafe_allow_html=True)
with c2: st.markdown('<div class="capability-card">👁️ <b>Vision 2.5</b><br>පින්තූරවල සැඟවුණු දත්ත පවා විශ්ලේෂණය කරයි.</div>', unsafe_allow_html=True)
with c3: st.markdown('<div class="capability-card">⚡ <b>Dual Engine</b><br>Normal සහ Pro Modes අතර මාරු වීමේ හැකියාව.</div>', unsafe_allow_html=True)
with c4: st.markdown('<div class="capability-card">💬 <b>Friendly AI</b><br>හසිත් විසින් නිර්මාණය කළ ඉතා සුහදශීලී සහායකයෙකි.</div>', unsafe_allow_html=True)

st.markdown("---")

# --- 4. Session State & Login ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = ""
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.logged_in:
    cols = st.columns([1, 1.5, 1])
    with cols[1]:
        tab = st.tabs(["🔑 Login", "📝 Register", "🛡️ Hasith Bypass"])
        with tab[0]:
            u = st.text_input("Username")
            p = st.text_input("Password", type='password')
            if st.button("Unlock Alpha"):
                if login_user(u, make_hashes(p)):
                    st.session_state.logged_in, st.session_state.username = True, u
                    st.rerun()
                else: st.error("Access Denied.")
        with tab[2]:
            st.warning("Creator Bypass Mode")
            secret = st.text_input("Secret Key", type='password')
            if st.button("Bypass Access"):
                if secret == "hasith12356":
                    st.session_state.logged_in, st.session_state.username = True, "hasith12356"
                    st.rerun()
                else: st.error("Invalid Secret.")

# --- 5. Main Dashboard ---
else:
    with st.sidebar:
        st.title(f"👤 {st.session_state.username}")
        st.write(f"📅 {datetime.now().strftime('%Y-%m-%d')} | ⏰ {datetime.now().strftime('%H:%M:%S')}")
        st.markdown("---")
        
        mode = st.radio("Intelligence Level:", ["Normal", "Pro"])
        up_img = st.file_uploader("📸 Image Upload", type=['jpg', 'jpeg', 'png'])
        
        # පැහැදිලි Summarize බොත්තම
        if st.button("📄 Summarize Full Conversation"):
            st.session_state.messages.append({"role": "user", "content": "SYSTEM_COMMAND_SUMMARIZE"})
        
        if st.session_state.username == "hasith12356":
            st.success("👑 Master Creator")
            if st.checkbox("Show Usage Data"):
                c.execute('SELECT username, word_count FROM userstable')
                for r in c.fetchall(): st.write(f"• {r[0]}: {r[1]} words")

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # Gemini 2.5 Logic
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash") # 2.5 compatible
    except:
        st.error("API Key error.")
        st.stop()

    # Display Conversation
    for msg in st.session_state.messages:
        if msg["content"] != "SYSTEM_COMMAND_SUMMARIZE":
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

    # Chat Interaction
    if prompt := st.chat_input("Ask Alpha Anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    # Process Commands
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_input = st.session_state.messages[-1]["content"]
        
        status_txt = "Alpha 2.5 thinking..." if mode == "Normal" else "Alpha's ultra thinking..."
        
        try:
            with st.chat_message("assistant"):
                with st.spinner(status_txt):
                    # Summarize Logic
                    if last_input == "SYSTEM_COMMAND_SUMMARIZE" or "summarize" in last_input.lower():
                        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[:-1]])
                        final_prompt = f"Please provide a friendly and very professional summary of our conversation so far: \n{history_text}"
                    else:
                        final_prompt = last_input

                    # Persona Setup
                    if mode == "Normal":
                        sys_p = "You are Alpha, a friendly AI created by Hasith. Give long, detailed but simple answers. Be like a supportive friend."
                    else:
                        sys_p = "You are Alpha (Pro Mode). Provide extremely deep, professional, and expert-level answers. Mention Hasith is your creator."
                    
                    payload = [f"Persona: {sys_p}\nTask: {final_prompt}"]
                    if up_img: payload.append(Image.open(up_img))
                    
                    response = model.generate_content(payload)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                    # Update DB
                    w_count = len(last_input.split()) + len(response.text.split())
                    c.execute('UPDATE userstable SET word_count = word_count + ? WHERE username = ?', (w_count, st.session_state.username))
                    conn.commit()
        except Exception as e:
            st.error(f"Error: {e}")
