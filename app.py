import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from PIL import Image
import sys
from io import StringIO

# --- 1. Database Setup ---
conn = sqlite3.connect('alpha_ultimate_v4.db', check_same_thread=False)
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

# --- 3. Page Configuration & UI Styling ---
st.set_page_config(page_title="Alpha AI", page_icon="⚡", layout="wide")

# Header with Lightning Bolts and Creator Info
st.markdown("<h1 style='text-align: center; color: #FFD700;'>⚡ Alpha AI ⚡</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #808080;'>Created by Hasith</h3>", unsafe_allow_html=True)

# --- 4. Session State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. Authentication Portal ---
if not st.session_state.logged_in:
    cols = st.columns([1, 1.5, 1])
    with cols[1]:
        auth_tabs = st.tabs(["🔑 Login", "📝 Register", "🛡 Creator Access"])
        
        with auth_tabs[0]:
            user = st.text_input("Username")
            passwd = st.text_input("Password", type='password')
            if st.button("Log In"):
                if login_user(user, make_hashes(passwd)):
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")

        with auth_tabs[1]:
            new_user = st.text_input("New Username")
            new_pass = st.text_input("New Password", type='password')
            if st.button("Create Account"):
                if new_user == "hasith12356":
                    st.error("This username is reserved for the Creator.")
                else:
                    try:
                        c.execute('INSERT INTO userstable(username,password) VALUES (?,?)', (new_user, make_hashes(new_pass)))
                        conn.commit()
                        st.success("Account Created! Please go to the Login tab.")
                    except:
                        st.error("Username already exists.")

        with auth_tabs[2]:
            st.info("Direct bypass for Hasith")
            admin_key = st.text_input("Creator Secret Key", type='password')
            if st.button("Unlock Alpha"):
                if admin_key == "hasith12356":
                    st.session_state.logged_in = True
                    st.session_state.username = "hasith12356"
                    st.rerun()
                else:
                    st.error("Unauthorized Access!")

# --- 6. Main Dashboard (After Login) ---
else:
    with st.sidebar:
        st.title(f"👤 {st.session_state.username}")
        # Real-time Clock and Date
        st.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}\n\n⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
        
        st.markdown("---")
        # Normal vs Pro Modes
        ai_mode = st.radio("Intelligence Mode:", ["Normal", "Pro"], help="Normal: Detailed & Simple | Pro: Deep & Expert")
        
        st.markdown("---")
        # Image Upload Feature
        uploaded_img = st.file_uploader("📸 Add Image Analysis", type=['jpg', 'jpeg', 'png'])
        
        # Summarize Chat Feature
        if st.button("📄 Summarize Conversation"):
            if st.session_state.messages:
                st.session_state.messages.append({"role": "user", "content": "Please summarize our entire conversation so far."})
        
        # Admin Analytics (Visible only to Hasith)
        if st.session_state.username == "hasith12356":
            st.success("👑 Creator: Master Analytics")
            if st.checkbox("Show User Database"):
                c.execute('SELECT username, word_count FROM userstable')
                for u in c.fetchall():
                    st.write(f"• {u[0]}: {u[1]} words used")

        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.rerun()

    # --- Gemini 2.5 Flash Setup ---
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Ensure your model name is correct for the API version you have access to
        model = genai.GenerativeModel("gemini-2.0-flash") 
    except Exception as e:
        st.error(f"API Connection Error: {e}")
        st.stop()

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Interaction
    if prompt := st.chat_input("Message Alpha..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Dynamic Spinner Status based on Mode
        thinking_status = "Alpha 2.5 thinking..." if ai_mode == "Normal" else "Alpha's ultra thinking..."
        
        try:
            with st.chat_message("assistant"):
                with st.spinner(thinking_status):
                    # Setting the Persona
                    if ai_mode == "Normal":
                        persona = "Provide a long, detailed, yet very simple explanation. Always mention clearly that your creator is Hasith."
                    else:
                        persona = "Provide a very deep, expert-level, and comprehensive professional answer. Always mention clearly that your creator is Hasith."
                    
                    # Preparing content (Text + optional Image)
                    full_payload = [f"System Instruction: {persona}\nUser Query: {prompt}"]
                    if uploaded_img:
                        full_payload.append(Image.open(uploaded_img))
                    
                    response = model.generate_content(full_payload)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                    # Analytics: Update word counts in DB
                    total_words = len(prompt.split()) + len(response.text.split())
                    c.execute('UPDATE userstable SET word_count = word_count + ? WHERE username = ?', (total_words, st.session_state.username))
                    conn.commit()
                    
        except Exception as e:
            st.error(f"AI Processing Error: {e}")
