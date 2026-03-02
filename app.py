import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from PIL import Image

# --- 1. Database & Security Functions ---
conn = sqlite3.connect('alpha_master_v18.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT UNIQUE, password TEXT)')
conn.commit()

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(password, hashed_text): return make_hashes(password) == hashed_text
def add_userdata(username, password): 
    try:
        c.execute('INSERT INTO userstable(username, password) VALUES (?,?)', (username, password))
        conn.commit()
        return True
    except: return False

def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password =?', (username, password))
    return c.fetchall()

# --- 2. THE SUPREME METALLIC NEON UI ---
st.set_page_config(page_title="Alpha AI 2.5 Master", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Inter:wght@400;700&display=swap');
    
    .stApp { background-color: #000000; }

    /* Massive 115px Chrome Header */
    .chrome-header {
        font-family: 'Orbitron', sans-serif;
        font-size: 115px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(180deg, #ffffff 10%, #9ea7ad 45%, #4e5a61 55%, #050505 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 30px rgba(255, 255, 255, 0.3));
        margin-bottom: -10px;
    }
    
    .hasith-tag {
        text-align: center;
        color: #00d4ff;
        font-size: 26px;
        font-weight: bold;
        letter-spacing: 15px;
        text-transform: uppercase;
        text-shadow: 0 0 25px #00d4ff;
        margin-bottom: 50px;
    }

    /* NEON GLASS LOGIN & CHAT BUBBLES */
    div[data-testid="stExpander"], .stSelectbox, .stTextInput, [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 15px !important;
        backdrop-filter: blur(10px) !important;
        color: white !important;
    }

    /* PURE WHITE TEXT */
    p, li, span, label {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }

    /* AI RESPONSE GLOW */
    [data-testid="stChatMessage"]:nth-child(even) {
        border: 1px solid #00d4ff !important;
        box-shadow: 0 0 25px rgba(0, 212, 255, 0.3) !important;
    }

    /* CUSTOM LOGIN BUTTON */
    .stButton>button {
        background: linear-gradient(45deg, #00d4ff, #005f73) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        width: 100% !important;
        font-weight: bold !important;
        text-shadow: 0 0 5px black;
    }
    </style>
    """, unsafe_allow_html=True)

# Main Branding
st.markdown('<p class="chrome-header">ALPHA AI</p>', unsafe_allow_html=True)
st.markdown('<p class="hasith-tag">Developed by Hasith</p>', unsafe_allow_html=True)

# --- 3. LOGIN INTERFACE (GLOW STYLE) ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<p style="text-align:center; color:#ffffff; font-size:22px; font-weight:bold;">CREATED BY HASITH - ACCESS GATEWAY</p>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        # 
        choice = st.selectbox("Select Action", ["Login", "Register", "Creator Bypass"])
        
        if choice == "Login":
            u = st.text_input("Username")
            p = st.text_input("Password", type='password')
            if st.button("🔓 Unlock Alpha"):
                if login_user(u, make_hashes(p)):
                    st.session_state.logged_in, st.session_state.username = True, u
                    st.rerun()
                else: st.error("Access Denied: Invalid Credentials")

        elif choice == "Register":
            nu = st.text_input("Choose Username")
            np = st.text_input("Set Password", type='password')
            if st.button("🛡️ Create Identity"):
                if add_userdata(nu, make_hashes(np)):
                    st.success("Identity Created! Now Login.")
                else: st.error("Username already taken.")

        elif choice == "Creator Bypass":
            key = st.text_input("Enter Admin Master Key", type='password')
            if st.button("⚡ Emergency Bypass"):
                if key == "hasith12356":
                    st.session_state.logged_in, st.session_state.username = True, "Hasith (Admin)"
                    st.rerun()
                else: st.error("Invalid Master Key")

else:
    # --- 4. CHAT ENGINE (AFTER LOGIN) ---
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        mode = st.radio("Intelligence Level:", ["Normal", "Pro"])
        up_img = st.file_uploader("📸 Vision Scan", type=['jpg', 'jpeg', 'png'])
        if st.button("🚪 System Logout"):
            st.session_state.logged_in = False
            st.rerun()

    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Command Alpha 2.5..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        status_msg = "Alpha 2.5 thinking..." if mode == "Normal" else "Alpha's ultra thinking..."
        with st.chat_message("assistant"):
            with st.spinner(status_msg):
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel("gemini-2.5-flash")
                sys_p = "You are Alpha 2.5, created by Hasith. Responses: Professional, Friendly, White-Text optimized."
                payload = [f"{sys_p}\nQuery: {prompt}"]
                if up_img: payload.append(Image.open(up_img))
                
                response = model.generate_content(payload)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
