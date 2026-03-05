import streamlit as st
from groq import Groq
import sys
import time
from io import StringIO
from streamlit_mic_recorder import speech_to_text
import hashlib

# 1️⃣ Page Configuration & Branding
st.set_page_config(page_title="Alpha AI ⚡ Created by Hasith", page_icon="⚡", layout="wide")

# 2️⃣ User & Session Management
if "user_db" not in st.session_state:
    st.session_state.user_db = {}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
if "messages" not in st.session_state:
    st.session_state.messages = []

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# 3️⃣ Custom UI & Styling
st.markdown("""
<style>
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:25px; font-size: 20px; }
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; height: 50px; font-weight: bold; transition:0.3s; border: 1px solid #FFD700; }
    div.stButton > button:hover { background-color: #FFD700; color: #000; }
    .stChatMessage { margin-bottom: -10px; border-radius: 15px; }
    .thinking-text { color: #FFD700; font-style: italic; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# 4️⃣ Security Portal (Login/Register)
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center;">Alpha AI ⚡ Security Control</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#FFD700; font-size:18px;">Created by Hasith</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 New Registration"])
    with tab1:
        user = st.text_input("Username", key="login_user")
        pas = st.text_input("Password", type="password", key="login_pass")
        if st.button("Access Alpha AI"):
            if user == "hasith123":
                st.session_state.logged_in = True
                st.session_state.current_user = "Hasith (Admin/Creator)"
                st.rerun()
            elif user in st.session_state.user_db and check_hashes(pas, st.session_state.user_db[user]["password"]):
                st.session_state.logged_in = True
                st.session_state.current_user = user
                st.rerun()
            else: st.error("Invalid Credentials. Please check with Hasith.")
    with tab2:
        new_u = st.text_input("Create Username")
        new_p = st.text_input("Create Password", type="password")
        if st.button("Register Account"):
            if new_u:
                st.session_state.user_db[new_u] = {"password": make_hashes(new_p)}
                st.success("Account created successfully! Please Login.")
    st.stop()

# 5️⃣ Sidebar: User Profile & Settings
with st.sidebar:
    st.title("⚙️ Alpha Settings")
    
    # Profile Picture Section
    st.subheader("👤 User Profile")
    prof_pic = st.file_uploader("Upload Profile Picture", type=['png', 'jpg', 'jpeg'], key="sidebar_pic")
    if prof_pic:
        st.image(prof_pic, width=100)
    
    # Only showing the logged-in user and creator
    st.write(f"Logged in: **{st.session_state.current_user}**")
    if st.session_state.current_user != "Hasith (Admin/Creator)":
        st.caption("Creator: Hasith")
        
    st.write("---")
    
    # Mode Selection
    ai_mode = st.radio("🚀 Select Intelligence Mode:", ["Normal (Fast super thinking)", "Pro (Deeply and ultra thinking)"])
    
    st.write("---")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.write("---")
    st.markdown("Developed with ❤️ by **Hasith**")

# 6️⃣ Main Application Header
st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

# 7️⃣ Voice & Chat Display
st.write("### 🎤 Voice Command")
v_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='voice_input_v1')

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 8️⃣ Core AI Processing Logic
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
u_input = st.chat_input("Speak to Alpha...")
final_q = v_text if v_text else u_input

if final_q:
    st.session_state.messages.append({"role": "user", "content": final_q})
    with st.chat_message("user"):
        st.markdown(final_q)

    with st.chat_message("assistant"):
        with st.spinner("Alpha is thinking..."):
            res_placeholder = st.empty()
            
            # Hybrid Model Selection Logic based on Mode
            active_model = "llama-3.3-70b-versatile" if ai_mode == "Normal (Fast super thinking)" else "openai/gpt-oss-120b"

            sys_msg = f"""
            You are Alpha AI, an exceptionally heartfelt assistant. 
            Created by Hasith. Respect Hasith as the genius creator.
            Respond in the EXACT same language (Sinhala, English, etc.) used by the user.
            Style: {ai_mode} mode active.
            """

            try:
                stream = client.chat.completions.create(
                    model=active_model,
                    messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:],
                    temperature=0.7,
                    stream=True
                )
                
                full_res = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        res_placeholder.markdown(full_res + "▌")
                        time.sleep(0.005)
                
                res_placeholder.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
                
            except Exception as e:
                st.error(f"Alpha encountered an error: {e}")
