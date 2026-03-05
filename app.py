import streamlit as st
from groq import Groq
import time
import hashlib
from streamlit_mic_recorder import speech_to_text

# 1️⃣ Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Created by Hasith", page_icon="⚡", layout="wide")

# 2️⃣ Session Management
if "user_db" not in st.session_state:
    st.session_state.user_db = {}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# 3️⃣ UI Styling
st.markdown("""
<style>
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:25px; font-size: 20px; }
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; height: 50px; font-weight: bold; border: 1px solid #FFD700; }
    .stChatMessage { margin-bottom: 10px; border-radius: 15px; }
    .stFileUploader section { padding: 0; min-height: unset; border: none; }
</style>
""", unsafe_allow_html=True)

# 4️⃣ Login Portal
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center;">Alpha AI ⚡ Security Control</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    with tab1:
        user = st.text_input("Username", key="l_u")
        pas = st.text_input("Password", type="password", key="l_p")
        if st.button("Access Alpha"):
            if user == "hasith123" or (user in st.session_state.user_db and check_hashes(pas, st.session_state.user_db[user]["password"])):
                st.session_state.logged_in = True
                st.rerun()
    with tab2:
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")
        if st.button("Register"):
            st.session_state.user_db[new_u] = {"password": make_hashes(new_p)}
            st.success("Account Created!")
    st.stop()

# 5️⃣ Sidebar
with st.sidebar:
    st.title("⚙️ Alpha Settings")
    # THE LOGIC: Normal = Llama 3.3 | Pro = GPT-OSS 120B
    ai_mode = st.radio("🚀 Select Intelligence Mode:", ["Normal (Llama 3.3)", "Pro (GPT-OSS 120B)"])
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# 6️⃣ Header
st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

# 7️⃣ Voice Input
v_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='voice_input')

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 8️⃣ Core Logic
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

col_plus, col_chat = st.columns([1, 10])
with col_plus:
    uploaded_file = st.file_uploader("➕", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

with col_chat:
    u_input = st.chat_input("Speak to Alpha...")

if uploaded_file:
    st.image(uploaded_file, caption="Selected Image", width=120)

final_q = v_text if v_text else u_input

if final_q:
    st.session_state.messages.append({"role": "user", "content": final_q})
    with st.chat_message("user"):
        st.markdown(final_q)

    with st.chat_message("assistant"):
        with st.spinner("Alpha is thinking..."):
            res_placeholder = st.empty()
            
            # MODEL ASSIGNMENT BASED ON YOUR REQUEST
            if "Normal" in ai_mode:
                active_model = "llama-3.3-70b-versatile"
            else:
                active_model = "openai/gpt-oss-120b"

            sys_msg = f"You are Alpha AI created by Hasith. Mode: {ai_mode}. Respond in user's language (Sinhala/English)."

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
                
                res_placeholder.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
                
            except Exception as e:
                st.error(f"Alpha encountered an error: {e}")
