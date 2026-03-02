import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from PIL import Image

# --- 1. Database & Security Functions ---
conn = sqlite3.connect('alpha_final_master_v16.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT UNIQUE, password TEXT)')
conn.commit()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def add_userdata(username, password):
    c.execute('INSERT INTO userstable(username, password) VALUES (?,?)', (username, password))
    conn.commit()

def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password =?', (username, password))
    data = c.fetchall()
    return data

# --- 2. THE ULTIMATE METALLIC GLASS UI ---
st.set_page_config(page_title="Alpha AI 2.5 Master", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Inter:wght@400;700&display=swap');
    
    .stApp { background-color: #000000; }

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

    /* Force all text to Pure White */
    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li, [data-testid="stChatMessage"] span {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
        font-size: 17.5px !important;
        line-height: 1.6 !important;
    }
    
    /* AI Response Glow & Border */
    [data-testid="stChatMessage"]:nth-child(even) {
        border: 1px solid rgba(0, 212, 255, 0.4) !important;
        box-shadow: 0 0 25px rgba(0, 212, 255, 0.15) !important;
        background: rgba(0, 212, 255, 0.03) !important;
    }

    /* Metallic Capability Cards */
    .cap-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid #333;
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        transition: 0.4s;
    }
    .cap-card:hover { border-color: #ffffff; transform: translateY(-5px); }

    /* Custom Sidebar styling */
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
st.markdown('<p style="text-align:center; color:#ffffff; font-size:20px; font-weight:bold; letter-spacing: 2px;">CREATED BY HASITH</p>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown('<div class="cap-card"><h2 style="margin:0;">📄</h2><b style="color:white;">SUMMARIZE</b></div>', unsafe_allow_html=True)
with c2: st.markdown('<div class="cap-card"><h2 style="margin:0;">👁️</h2><b style="color:white;">VISION 2.5</b></div>', unsafe_allow_html=True)
with c3: st.markdown('<div class="cap-card"><h2 style="margin:0;">🧠</h2><b style="color:white;">DUAL BRAIN</b></div>', unsafe_allow_html=True)
with c4: st.markdown('<div class="cap-card"><h2 style="margin:0;">🤝</h2><b style="color:white;">FRIENDLY</b></div>', unsafe_allow_html=True)

st.markdown("<br><hr style='border: 0.1px solid #222;'><br>", unsafe_allow_html=True)

# --- 4. AUTHENTICATION (LOGIN / REGISTER / BYPASS) ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    cols = st.columns([1, 1.5, 1])
    with cols[1]:
        choice = st.selectbox("Account Gateway", ["Login", "Register", "Creator Bypass"])
        
        if choice == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type='password')
            if st.button("Unlock Alpha"):
                hashed_pswd = make_hashes(password)
                result = login_user(username, check_hashes(password, hashed_pswd))
                if result:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else: st.error("Invalid Username or Password")

        elif choice == "Register":
            new_user = st.text_input("New Username")
            new_password = st.text_input("New Password", type='password')
            if st.button("Create Account"):
                try:
                    add_userdata(new_user, make_hashes(new_password))
                    st.success("Registration Successful! Now please login.")
                except: st.error("User already exists!")

        elif choice == "Creator Bypass":
            admin_key = st.text_input("Secret Admin Key", type='password')
            if st.button("Master Access"):
                if admin_key == "hasith12356":
                    st.session_state.logged_in = True
                    st.session_state.username = "Hasith (Admin)"
                    st.rerun()
                else: st.error("Access Denied")
else:
    # --- 5. MAIN CHAT APPLICATION ---
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        mode = st.radio("Engine Mode:", ["Normal", "Pro"])
        up_img = st.file_uploader("📸 Vision 2.5 Scan", type=['jpg', 'jpeg', 'png'])
        
        if st.button("📄 Summarize History"):
            st.session_state.messages.append({"role": "user", "content": "Please summarize our entire conversation so far."})
        
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()

    if "messages" not in st.session_state: st.session_state.messages = []
    
    # Render messages
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # Chat input and processing
    if prompt := st.chat_input("Command Alpha 2.5..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        # Status Logic
        status_msg = "Alpha 2.5 thinking..." if mode == "Normal" else "Alpha's ultra thinking..."
        
        with st.chat_message("assistant"):
            with st.spinner(status_msg):
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel("gemini-2.5-flash") # Gemini 2.5 Engine logic
                
                # Peer Personality Instruction
                sys_p = "You are Alpha 2.5, a sophisticated AI peer created by Hasith. Provide long, warm, expert-level English responses. Always acknowledge Hasith as your creator."
                
                payload = [f"{sys_p}\nUser Query: {prompt}"]
                if up_img: payload.append(Image.open(up_img))
                
                try:
                    response = model.generate_content(payload)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")
