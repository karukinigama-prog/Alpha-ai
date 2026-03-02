import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from PIL import Image
import sys
from io import StringIO

# --- 1. Database Setup ---
conn = sqlite3.connect('alpha_metallic_v5.db', check_same_thread=False)
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

# --- 3. Page Configuration & Metallic Styling ---
st.set_page_config(page_title="Alpha AI Elite", page_icon="⚡", layout="wide")

# Custom CSS for Metallic Look
st.markdown("""
    <style>
    .metallic-text {
        font-size: 60px;
        font-weight: bold;
        background: linear-gradient(to bottom, #cfd8dc 0%, #90a4ae 50%, #546e7a 51%, #263238 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(2px 2px #000);
        text-align: center;
        font-family: 'Orbitron', sans-serif;
    }
    .creator-text {
        text-align: center;
        color: #78909c;
        font-size: 20px;
        letter-spacing: 2px;
    }
    .stChatFloatingInputContainer { background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# Header Section
st.markdown('<p class="metallic-text">⚡ ALPHA AI ⚡</p>', unsafe_allow_html=True)
st.markdown('<p class="creator-text">CREATED BY HASITH</p>', unsafe_allow_html=True)

# --- 4. Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. Authentication ---
if not st.session_state.logged_in:
    cols = st.columns([1, 1.5, 1])
    with cols[1]:
        auth_tabs = st.tabs(["🔑 Login", "📝 Register Account", "🛡 Creator Access"])
        
        with auth_tabs[0]:
            user = st.text_input("Username")
            passwd = st.text_input("Password", type='password')
            if st.button("Access System"):
                if login_user(user, make_hashes(passwd)):
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.rerun()
                else: st.error("Access Denied.")

        with auth_tabs[1]:
            new_user = st.text_input("Choose Username")
            new_pass = st.text_input("Choose Password", type='password')
            if st.button("Register"):
                if new_user == "hasith12356": st.error("Unauthorized ID.")
                else:
                    try:
                        c.execute('INSERT INTO userstable(username,password) VALUES (?,?)', (new_user, make_hashes(new_pass)))
                        conn.commit()
                        st.success("Registered. Please login.")
                    except: st.error("User exists.")

        with auth_tabs[2]:
            st.info("Creator Bypass")
            admin_key = st.text_input("Creator ID", type='password')
            if st.button("Unlock Alpha"):
                if admin_key == "hasith12356":
                    st.session_state.logged_in = True
                    st.session_state.username = "hasith12356"
                    st.rerun()
                else: st.error("Invalid Creator ID.")

# --- 6. Main Interface ---
else:
    with st.sidebar:
        st.markdown(f"### 👤 User: {st.session_state.username}")
        st.write(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
        st.write(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
        
        st.markdown("---")
        ai_mode = st.radio("Intelligence Level:", ["Normal", "Pro"], help="Normal: 2.5 Logic | Pro: Ultra Depth")
        
        uploaded_img = st.file_uploader("🖼 Analyze Visuals", type=['jpg', 'jpeg', 'png'])
        
        if st.button("📄 Summarize Conversation"):
            st.session_state.messages.append({"role": "user", "content": "Summarize everything we discussed in detail."})
        
        if st.session_state.username == "hasith12356":
            st.success("👑 Master Panel")
            if st.checkbox("Show Statistics"):
                c.execute('SELECT username, word_count FROM userstable')
                for u in c.fetchall(): st.write(f"• {u[0]}: {u[1]} words")

        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # Gemini 2.5 Flash Setup
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.5-flash") # Targeted Version
    except Exception as e:
        st.error("API Error.")
        st.stop()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Input command to Alpha..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Dynamic Loading Text
        status_msg = "Alpha 2.5 thinking..." if ai_mode == "Normal" else "Alpha's ultra thinking..."
        
        try:
            with st.chat_message("assistant"):
                with st.spinner(status_status_msg):
                    # Setting Deep Persona
                    if ai_mode == "Normal":
                        persona = "Provide a long, clear, and very simple explanation. Mention you are created by Hasith."
                    else:
                        persona = "Provide an extremely deep, technical, professional, and comprehensive long-form answer. Be an expert. Mention you are created by Hasith."
                    
                    payload = [f"Persona: {persona}\nQuery: {prompt}"]
                    if uploaded_img:
                        payload.append(Image.open(uploaded_img))
                    
                    response = model.generate_content(payload)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                    # Update Analytics
                    total_words = len(prompt.split()) + len(response.text.split())
                    c.execute('UPDATE userstable SET word_count = word_count + ? WHERE username = ?', (total_words, st.session_state.username))
                    conn.commit()
                    
        except Exception as e:
            st.error(f"Engine Error: {e}")
