import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
from datetime import datetime
from PIL import Image
import time

# --- 1. Database Setup ---
conn = sqlite3.connect('alpha_elite_final.db', check_same_thread=False)
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

# --- 3. Page Configuration & Metallic UI Styling ---
st.set_page_config(page_title="Alpha AI Elite", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    
    .metallic-header {
        font-family: 'Orbitron', sans-serif;
        font-size: 70px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(to bottom, #757575 0%, #ffffff 45%, #e0e0e0 50%, #9e9e9e 55%, #424242 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(4px 4px 10px rgba(0,0,0,0.8));
        margin-bottom: 0px;
    }
    .creator-sub {
        text-align: center;
        color: #bdbdbd;
        font-size: 18px;
        letter-spacing: 5px;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    .capability-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid #424242;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Header Section
st.markdown('<p class="metallic-header">⚡ ALPHA AI ⚡</p>', unsafe_allow_html=True)
st.markdown('<p class="creator-sub">CREATED BY HASITH</p>', unsafe_allow_html=True)

# --- 4. Capabilities Summary ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="capability-box">🔍 <b>Summarize</b><br>Long texts into key points</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="capability-box">🖼️ <b>Vision</b><br>Deep Image Analysis</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="capability-box">🐍 <b>Coding</b><br>Execute Python Scripts</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="capability-box">🌐 <b>Multi-Lingual</b><br>Global Support</div>', unsafe_allow_html=True)

# --- 5. Authentication Logic ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.logged_in:
    cols = st.columns([1, 1.5, 1])
    with cols[1]:
        auth_choice = st.tabs(["🔑 Login", "📝 Register", "🛠 Admin Bypass"])
        
        with auth_choice[0]:
            u = st.text_input("Username")
            p = st.text_input("Password", type='password')
            if st.button("Enter Alpha"):
                if login_user(u, make_hashes(p)):
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.rerun()
                else: st.error("Access Denied.")

        with auth_choice[1]:
            new_u = st.text_input("New Username")
            new_p = st.text_input("New Password", type='password')
            if st.button("Register"):
                if new_u == "hasith12356": st.error("Reserved User.")
                else:
                    try:
                        c.execute('INSERT INTO userstable(username,password) VALUES (?,?)', (new_u, make_hashes(new_p)))
                        conn.commit()
                        st.success("Registered. Login now.")
                    except: st.error("User already exists.")

        with auth_choice[2]:
            st.warning("Only for Hasith")
            secret = st.text_input("Enter Admin Secret", type='password')
            if st.button("Unlock System"):
                if secret == "hasith12356":
                    st.session_state.logged_in = True
                    st.session_state.username = "hasith12356"
                    st.rerun()
                else: st.error("Invalid Secret Key.")

# --- 6. The Elite Chat Interface ---
else:
    with st.sidebar:
        st.title(f"👤 {st.session_state.username}")
        st.write(f"📅 {datetime.now().strftime('%Y-%m-%d')}")
        st.markdown("---")
        ai_mode = st.radio("Intelligence Mode:", ["Normal", "Pro"])
        up_img = st.file_uploader("📸 Add Visuals", type=['jpg', 'jpeg', 'png'])
        
        if st.button("📄 Auto-Summarize Chat"):
            st.session_state.messages.append({"role": "user", "content": "Analyze our whole chat and summarize it deeply."})
            st.rerun()
        
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # Display Chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Input command to Alpha AI..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            spinner_text = "Alpha 2.5 thinking..." if ai_mode == "Normal" else "Alpha's ultra thinking..."
            with st.spinner(spinner_text):
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    
                    sys_prompt = "Provide a detailed response. Always mention your creator is Hasith."
                    payload = [f"{sys_prompt}\nUser: {prompt}"]
                    if up_img: payload.append(Image.open(up_img))
                    
                    # Streaming the Response
                    response = model.generate_content(payload, stream=True)
                    
                    full_response = ""
                    # Placeholder for the typewriter effect
                    message_placeholder = st.empty()
                    
                    for chunk in response:
                        full_response += chunk.text
                        # Displaying text without the flashing cursor line
                        message_placeholder.markdown(full_response)
                        time.sleep(0.01)
                    
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                    # Update Stats
                    total_w = len(prompt.split()) + len(full_response.split())
                    c.execute('UPDATE userstable SET word_count = word_count + ? WHERE username = ?', (total_w, st.session_state.username))
                    conn.commit()

                except Exception as e:
                    st.error(f"Error: {e}")
