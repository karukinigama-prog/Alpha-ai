import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from PIL import Image
import sys
from io import StringIO

# --- 1. Database Setup ---
conn = sqlite3.connect('alpha_ultimate_v3.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT UNIQUE, password TEXT, word_count INTEGER DEFAULT 0)')
c.execute('CREATE TABLE IF NOT EXISTS feedback_table(username TEXT, feedback TEXT, date TEXT)')
conn.commit()

# --- 2. Helper Functions ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

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

def update_word_count(username, count):
    # Track word usage for all users including admin
    c.execute('UPDATE userstable SET word_count = word_count + ? WHERE username = ?', (count, username))
    conn.commit()

# --- 3. Page Config & Professional Styling ---
st.set_page_config(page_title="Alpha AI Elite", page_icon="☯", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; transition: 0.3s; }
    .stButton>button:hover { background-color: #4CAF50; color: white; }
    .admin-box { background-color: #1a1c23; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Session State Control ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. Integrated Login/Registration Portal ---
if not st.session_state.logged_in:
    cols = st.columns([1, 1.8, 1])
    with cols[1]:
        st.title("☯ Alpha AI Elite Portal")
        auth_mode = st.tabs(["🔑 Login", "📝 Register", "🛡 Creator Access"])

        with auth_mode[0]:
            user = st.text_input("Username", key="l_user")
            passwd = st.text_input("Password", type='password', key="l_pass")
            if st.button("Log In"):
                result = login_user(user, make_hashes(passwd))
                if result:
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.rerun()
                else:
                    st.error("Invalid Login Credentials")

        with auth_mode[1]:
            new_user = st.text_input("Choose Username", key="r_user")
            new_pass = st.text_input("Choose Password", type='password', key="r_pass")
            if st.button("Register Account"):
                if new_user.lower() == "hasith12356":
                    st.error("Username reserved for Creator.")
                elif add_userdata(new_user, make_hashes(new_pass)):
                    st.success("Registration Successful! Please Login.")
                else:
                    st.error("Username already taken.")

        with auth_mode[2]:
            st.info("Direct access for Creator Hasith.")
            admin_id = st.text_input("Enter Admin Secret Key", type='password')
            if st.button("Unlock Alpha"):
                if admin_id == "hasith12356":
                    st.session_state.logged_in = True
                    st.session_state.username = "hasith12356"
                    st.success("Welcome back, Hasith!")
                    # Ensure admin exists in word count table
                    c.execute('INSERT OR IGNORE INTO userstable(username,password,word_count) VALUES (?,?,?)', ("hasith12356", "admin_bypass", 0))
                    conn.commit()
                    st.rerun()
                else:
                    st.error("Unauthorized Admin Key.")

# --- 6. The Elite AI Experience ---
else:
    with st.sidebar:
        st.title(f"👤 {st.session_state.username}")
        if st.session_state.username == "hasith12356":
            st.success("👑 SYSTEM CREATOR")
            if st.checkbox("📊 Master Analytics"):
                st.subheader("User Statistics")
                c.execute('SELECT username, word_count FROM userstable')
                for u in c.fetchall():
                    st.markdown(f"<div class='admin-box'>👤 {u[0]}<br>📝 {u[1]} Words</div>", unsafe_allow_html=True)
                
                st.subheader("Feedbacks")
                c.execute('SELECT * FROM feedback_table')
                for fb in c.fetchall():
                    st.info(f"From {fb[0]}: {fb[1]} ({fb[2]})")

        st.markdown("---")
        ai_mode = st.radio("AI Intelligence Level", ["Normal (Fast)", "Pro (Detailed)"])
        uploaded_img = st.file_uploader("🖼 Upload Image for Analysis", type=['jpg','png','jpeg'])
        
        st.subheader("🐍 Code Lab")
        py_code = st.text_area("Live Python Interpreter", placeholder="print('Alpha Online')", height=100)
        if st.button("▶ Execute"):
            try:
                old_stdout = sys.stdout
                redirected_output = sys.stdout = StringIO()
                exec(py_code)
                sys.stdout = old_stdout
                st.code(redirected_output.getvalue())
            except Exception as e:
                st.error(f"Logic Error: {e}")

        st.markdown("---")
        if st.button("🚪 Logout / Switch User"):
            st.session_state.logged_in = False
            st.rerun()

    # --- Gemini 2.0 Flash Implementation ---
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.0-flash")
    except:
        st.error("API Key connection failed.")
        st.stop()

    st.title("💥 Alpha AI Dashboard")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask Alpha anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        update_word_count(st.session_state.username, len(prompt.split()))

        try:
            with st.chat_message("assistant"):
                with st.spinner("Alpha is processing..."):
                    payload = [prompt]
                    if uploaded_img:
                        payload.append(Image.open(uploaded_img))
                    
                    # System Persona Logic
                    sys_prompt = "Briefly." if ai_mode == "Normal (Fast)" else "Provide a detailed expert response."
                    full_prompt = f"{sys_prompt} {prompt}"
                    
                    response = model.generate_content(payload)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    update_word_count(st.session_state.username, len(response.text.split()))
        except Exception as e:
            st.error(f"Processing Error: {e}")

    # Footer Feedback
    st.markdown("---")
    with st.expander("📝 Submit Feedback to Hasith"):
        fb_msg = st.text_input("Your Message:")
        if st.button("Submit"):
            c.execute('INSERT INTO feedback_table VALUES (?,?,?)', (st.session_state.username, fb_msg, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            st.success("Thank you! Feedback saved.")
