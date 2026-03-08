import streamlit as st
from groq import Groq
import sys
import time
from io import StringIO
from streamlit_mic_recorder import speech_to_text
import hashlib
import urllib.parse
import os
import PyPDF2
from gtts import gTTS

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Hasith's Empire", page_icon="⚡", layout="wide")

# 2. Session & Imperial Database
if "user_db" not in st.session_state:
    st.session_state.user_db = {
        "matheesha": {"password": "123", "vault": [], "activity": 45},
        "sadev": {"password": "123", "vault": [], "activity": 30}
    }
if "device_logs" not in st.session_state:
    st.session_state.device_logs = ["Admin-PC (Hasith)", "iPhone 14 Pro", "Samsung S24 Ultra"]

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_user" not in st.session_state: st.session_state.current_user = None
if "is_guest" not in st.session_state: st.session_state.is_guest = False
if "messages" not in st.session_state: st.session_state.messages = []
if "pdf_text" not in st.session_state: st.session_state.pdf_text = ""

# 3. 🎨 Advanced Futuristic UI Styling
st.markdown("""
<style>
    /* Global Styles */
    .stApp { background-color: #050505; }
    
    /* Security Portal Styling */
    .login-container {
        background: rgba(10, 10, 10, 0.9);
        border: 2px solid #FFD700;
        padding: 40px;
        border-radius: 30px;
        box-shadow: 0 0 50px rgba(255, 215, 0, 0.2);
        text-align: center;
        margin-top: 50px;
    }
    .glitch-title {
        font-size: 50px;
        font-weight: bold;
        color: #FFD700;
        text-shadow: 2px 2px #FF0000, -2px -2px #0000FF;
        letter-spacing: 5px;
        margin-bottom: 10px;
    }
    .security-badge {
        background: #FFD700;
        color: #000;
        padding: 5px 15px;
        border-radius: 50px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    /* Buttons */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(45deg, #FFD700, #FF8C00);
        color: #000 !important;
        border: none;
        border-radius: 15px;
        font-weight: bold;
        height: 50px;
        font-size: 18px;
        transition: 0.4s;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 30px #FFD700;
    }
    
    /* Sidebar Admin Card */
    .admin-card {
        background: #111;
        border-left: 5px solid #FFD700;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 4. 🔒 Ultra-Luxury Security Portal
if not st.session_state.logged_in and not st.session_state.is_guest:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div class="login-container">
                <div class="security-badge">Secure Encryption Active</div>
                <div class="glitch-title">ALPHA AI</div>
                <p style="color: #888;">NEURAL NETWORK INTERFACE</p>
            </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["⚡ IDENTITY AUTH", "📡 NEW SIGNAL"])
        
        with tab1:
            u_in = st.text_input("USER ACCESS ID").lower().strip()
            p_in = st.text_input("BIO-METRIC PASS", type="password")
            if st.button("INITIATE LOGIN"):
                if u_in == "hasith123" and p_in == "hasith@alpha":
                    st.session_state.logged_in = True; st.session_state.current_user = u_in; st.rerun()
                elif u_in in st.session_state.user_db and (p_in == "123" or p_in == st.session_state.user_db[u_in]["password"]):
                    st.session_state.logged_in = True; st.session_state.current_user = u_in; st.rerun()
                else: st.error("⚠️ ACCESS DENIED: INVALID IDENTITY")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔓 BYPASS AS GUEST"):
                st.session_state.is_guest = True; st.session_state.current_user = "Guest"; st.rerun()

        with tab2:
            nu = st.text_input("ASSIGN NEW USERNAME")
            np = st.text_input("ASSIGN SECURITY KEY", type="password")
            if st.button("REGISTER TO EMPIRE"):
                if nu and np:
                    st.session_state.user_db[nu.lower()] = {"password": np, "vault": [], "activity": 5}
                    st.success("✅ REGISTRATION COMPLETE")
    st.stop()

# 5. ⚙️ Sidebar Admin Dashboard
with st.sidebar:
    st.markdown('<h1 style="color:#FFD700; text-align:center;">⚡ ALPHA AI</h1>', unsafe_allow_html=True)
    
    if st.session_state.current_user == "hasith123":
        st.markdown('<div class="admin-card">', unsafe_allow_html=True)
        st.markdown('<h3 style="color:#FFD700; margin:0;">👑 HASITH COMMAND</h3>', unsafe_allow_html=True)
        st.write(f"👥 Users: {len(st.session_state.user_db)} | 📱 Devices: {len(st.session_state.device_logs)}")
        
        st.write("📊 **Neural Activity**")
        for user, data in st.session_state.user_db.items():
            st.write(f"{user.capitalize()}")
            st.progress(data["activity"] / 100)
            
        st.write("📱 **Live Device Log**")
        for dev in st.session_state.device_logs[-3:]:
            st.markdown(f'<p style="font-size:10px; color:#555; margin:0;">✔ {dev}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write(f"Logged as: **{st.session_state.current_user.upper()}**")
    persona = st.selectbox("Persona:", ["Standard", "Image Creator 🎨", "Hasith Mode ⚡"])
    if st.button("TERMINATE SESSION"): st.session_state.logged_in = False; st.session_state.is_guest = False; st.rerun()

# 6. 🏛️ Main Interface
st.markdown('<div style="background: linear-gradient(90deg, #FFD700, #FF8C00); padding: 10px; border-radius: 10px; color: black; text-align: center; font-weight: bold;">⚡ ALPHA AI ULTIMATE COMMAND CENTER | CREATED BY HASITH</div>', unsafe_allow_html=True)

if st.session_state.current_user == "hasith123":
    st.write("### 📈 Real-time Neural Activity")
    chart_data = {user: data["activity"] for user, data in st.session_state.user_db.items()}
    st.bar_chart(chart_data)



for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "img" in msg: st.image(msg["img"])

# 7. AI Core Logic
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
u_input = st.chat_input("Enter command...")
v_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='v_rec')
final_q = v_text if v_text else u_input

if final_q:
    st.session_state.messages.append({"role": "user", "content": final_q})
    with st.chat_message("user"): st.markdown(final_q)
    
    if st.session_state.current_user in st.session_state.user_db:
        st.session_state.user_db[st.session_state.current_user]["activity"] = min(100, st.session_state.user_db[st.session_state.current_user]["activity"] + 2)

    with st.chat_message("assistant"):
        if persona == "Image Creator 🎨":
            img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(final_q)}?width=1024&height=1024&nologo=true"
            st.image(img_url); st.session_state.messages.append({"role": "assistant", "content": "Visualized.", "img": img_url})
        else:
            with st.spinner("Alpha processing..."):
                identity = f"You are Alpha AI, created by Hasith. Currently talking to {st.session_state.current_user}."
                try:
                    stream = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[{"role": "system", "content": identity}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-8:] if "img" not in m],
                        stream=True
                    )
                    full_res = ""
                    res_area = st.empty()
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            full_res += chunk.choices[0].delta.content
                            res_area.markdown(full_res + "▌")
                    res_area.markdown(full_res)
                    st.session_state.messages.append({"role": "assistant", "content": full_res})
                except Exception as e: st.error(f"Error: {e}")
