import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from PIL import Image # මෙය Pillow library එකයි
import sys
from io import StringIO

# --- 1. Database Setup ---
conn = sqlite3.connect('alpha_elite_v25.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT UNIQUE, password TEXT, word_count INTEGER DEFAULT 0)')
c.execute('CREATE TABLE IF NOT EXISTS feedback_table(username TEXT, feedback TEXT, date TEXT)')
conn.commit()

# --- 2. Helper Functions ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def add_userdata(username, password):
    try:
        c.execute('INSERT INTO userstable(username,password,word_count) VALUES (?,?,?)', (username, password, 0))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password =?', (username, password))
    return c.fetchone()

# --- 3. Page Styling & Config ---
st.set_page_config(page_title="Alpha AI 2.5 Elite", page_icon="☯", layout="wide")

# --- 4. Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. Portal Logic ---
if not st.session_state.logged_in:
    cols = st.columns([1, 1.5, 1])
    with cols[1]:
        st.title("☯ Alpha AI 2.5 Portal")
        auth_mode = st.tabs(["🔑 Login", "📝 Register", "🛡 Creator Access"])

        with auth_mode[0]:
            user = st.text_input("Username")
            passwd = st.text_input("Password", type='password')
            if st.button("Log In"):
                if login_user(user, make_hashes(passwd)):
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.rerun()
                else:
                    st.error("Invalid Username/Password")

        with auth_mode[1]:
            new_user = st.text_input("New Username")
            new_pass = st.text_input("New Password", type='password')
            if st.button("Sign Up"):
                if new_user == "hasith12356": st.error("Reserved name!")
                elif add_userdata(new_user, make_hashes(new_pass)): st.success("Success! Now Login.")
                else: st.error("Username taken.")

        with auth_mode[2]:
            st.info("Direct Entry for Hasith")
            admin_key = st.text_input("Admin Secret Key", type='password')
            if st.button("Unlock Alpha"):
                if admin_key == "hasith12356":
                    st.session_state.logged_in = True
                    st.session_state.username = "hasith12356"
                    st.rerun()
                else: st.error("Access Denied!")

# --- 6. Main App Post-Login ---
else:
    with st.sidebar:
        st.title(f"👤 {st.session_state.username}")
        if st.session_state.username == "hasith12356":
            st.success("👑 ADMIN MODE")
            if st.checkbox("📊 Master Stats"):
                c.execute('SELECT username, word_count FROM userstable')
                for u in c.fetchall(): st.write(f"• {u[0]}: {u[1]} words")
        
        st.markdown("---")
        # Python Code Runner
        st.subheader("🐍 Code Lab")
        py_code = st.text_area("Python Script", placeholder="print('Hello')", height=100)
        if st.button("▶ Run"):
            try:
                old_stdout = sys.stdout
                redirected_output = sys.stdout = StringIO()
                exec(py_code)
                sys.stdout = old_stdout
                st.code(redirected_output.getvalue())
            except Exception as e: st.error(e)

        st.markdown("---")
        img_file = st.file_uploader("🖼 Upload Image", type=['jpg','png','jpeg'])
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # Gemini 2.5 Setup
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.5-flash") # ඉල්ලා සිටි 2.5 මාදිලිය
    except:
        st.error("API Key Issue!")
        st.stop()

    st.title("💥 Alpha AI 2.5 Dashboard")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Ask anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        try:
            with st.chat_message("assistant"):
                with st.spinner("Alpha 2.5 is thinking..."):
                    payload = [prompt]
                    if img_file: payload.append(Image.open(img_file))
                    
                    response = model.generate_content(payload)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                    # Track analytics
                    words = len(prompt.split()) + len(response.text.split())
                    c.execute('UPDATE userstable SET word_count = word_count + ? WHERE username = ?', (words, st.session_state.username))
                    conn.commit()
        except Exception as e: st.error(e)
