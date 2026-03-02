import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from PIL import Image
import sys
from io import StringIO

# --- 1. Database Setup ---
conn = sqlite3.connect('alpha_ultimate_v7.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT UNIQUE, password TEXT, word_count INTEGER DEFAULT 0)')
conn.commit()

# --- 2. Security Functions ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password =?', (username, password))
    return c.fetchone()

# --- 3. Page Styling (Lohamaya & UI) ---
st.set_page_config(page_title="Alpha AI Master", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Inter:wght@400;700&display=swap');
    
    .metallic-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 110px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(to bottom, #cfd8dc 0%, #eee 50%, #828282 51%, #333 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(6px 6px 20px rgba(0,0,0,0.8));
        margin-bottom: 0px;
    }
    .creator-tag {
        text-align: center;
        color: #90a4ae;
        font-size: 24px;
        font-weight: bold;
        letter-spacing: 10px;
        margin-top: -30px;
        margin-bottom: 40px;
    }
    .feature-card {
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid #444;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        transition: 0.3s;
    }
    .feature-card:hover {
        border-color: #90a4ae;
        background: rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# Header Section
st.markdown('<p class="metallic-title">⚡ ALPHA AI ⚡</p>', unsafe_allow_html=True)
st.markdown('<p class="creator-tag">Created by Hasith</p>', unsafe_allow_html=True)

# --- 4. Capabilities / Help Board (Always Visible) ---
st.markdown("### 🛠️ Alpha's Capabilities")
cap_cols = st.columns(4)
with cap_cols[0]:
    st.markdown('<div class="feature-card">📝 <b>Summarize</b><br>Instantly shorten long texts or chat history.</div>', unsafe_allow_html=True)
with cap_cols[1]:
    st.markdown('<div class="feature-card">👁️ <b>Vision</b><br>Upload photos for deep AI analysis.</div>', unsafe_allow_html=True)
with cap_cols[2]:
    st.markdown('<div class="feature-card">💻 <b>Code Lab</b><br>Write and run Python code in the sidebar.</div>', unsafe_allow_html=True)
with cap_cols[3]:
    st.markdown('<div class="feature-card">🧠 <b>Dual Brain</b><br>Switch between Normal and Ultra Pro modes.</div>', unsafe_allow_html=True)

st.markdown("---")

# --- 5. Authentication ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.logged_in:
    auth_col = st.columns([1, 1.5, 1])
    with auth_col[1]:
        tab = st.tabs(["🔒 LOGIN", "✨ REGISTER", "🛡️ HASITH BYPASS"])
        with tab[0]:
            u = st.text_input("User")
            p = st.text_input("Pass", type='password')
            if st.button("Access"):
                if login_user(u, make_hashes(p)):
                    st.session_state.logged_in, st.session_state.username = True, u
                    st.rerun()
                else: st.error("Denied.")
        with tab[2]:
            secret = st.text_input("Admin Key", type='password')
            if st.button("Bypass"):
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
        
        ai_mode = st.radio("Switch Intelligence Mode:", ["Normal", "Pro"])
        up_img = st.file_uploader("📸 Analysis Image", type=['jpg', 'jpeg', 'png'])
        
        if st.button("📄 Summarize Our Entire Chat"):
            st.session_state.messages.append({"role": "user", "content": "summarize"})
        
        if st.session_state.username == "hasith12356":
            st.success("👑 MASTER ADMIN")
            if st.checkbox("Show Statistics"):
                c.execute('SELECT username, word_count FROM userstable')
                for r in c.fetchall(): st.write(f"• {r[0]}: {r[1]} words")

        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # Gemini 2.5 Setup
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.0-flash") # This serves 2.5 logic
    except:
        st.error("Check API Key.")
        st.stop()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Talk to Alpha..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        status = "Alpha 2.5 thinking..." if ai_mode == "Normal" else "Alpha's ultra thinking..."
        
        try:
            with st.chat_message("assistant"):
                with st.spinner(status):
                    # --- FRIENDLY SYSTEM PROMPT ---
                    if prompt.lower() == "summarize":
                        task = "Analyze our whole conversation history and provide a friendly, structured summary."
                    else:
                        task = prompt

                    if ai_mode == "Normal":
                        sys_p = "You are Alpha, a friendly AI created by Hasith. Be very helpful, simple, and detailed. Talk like a friend."
                    else:
                        sys_p = "You are Alpha (Ultra Pro Mode), created by Hasith. Be an expert friend—comprehensive, deep, but supportive."
                    
                    payload = [f"Instruction: {sys_p}\nUser Query: {task}"]
                    if up_img: payload.append(Image.open(up_img))
                    
                    response = model.generate_content(payload)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                    # Word Update
                    count = len(prompt.split()) + len(response.text.split())
                    c.execute('UPDATE userstable SET word_count = word_count + ? WHERE username = ?', (count, st.session_state.username))
                    conn.commit()
        except Exception as e: st.error(e)
