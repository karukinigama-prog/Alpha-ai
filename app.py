import streamlit as st
from groq import Groq
import time
import base64
import asyncio
import edge_tts
import os
import webbrowser
from PyPDF2 import PdfReader

# --- 1. Page Configuration & Advanced Cyber UI ---
st.set_page_config(page_title="Alpha AI | Next-Gen", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Inter:wght@300;900&display=swap');
    
    .stApp { background: #02050a; color: #ffffff; font-family: 'Inter', sans-serif; }

    /* --- CYBER LOADING SCREEN CSS --- */
    .loader-container {
        display: flex; flex-direction: column; align-items: center; justify-content: center; 
        height: 90vh; background: #000;
    }
    .loading-text {
        font-family: 'Orbitron', sans-serif; color: #00d4ff; font-size: 2.5rem;
        font-weight: 900; letter-spacing: 12px; text-shadow: 0 0 20px #00d4ff;
        margin-bottom: 30px;
    }
    .progress-track {
        width: 500px; height: 6px; background: rgba(0, 212, 255, 0.1);
        border-radius: 10px; overflow: hidden;
    }
    .progress-fill {
        height: 100%; background: #00d4ff; box-shadow: 0 0 15px #00d4ff;
        transition: width 0.1s ease-out;
    }

    /* --- CYBER LOGIN INTERFACE --- */
    .login-container {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        height: 100vh; background: radial-gradient(circle, #051937 0%, #000000 100%);
    }
    .login-card {
        background: rgba(0, 212, 255, 0.05); backdrop-filter: blur(25px);
        border: 1px solid rgba(0, 212, 255, 0.3); padding: 40px;
        border-radius: 20px; width: 100%; max-width: 500px;
        text-align: center; box-shadow: 0 0 50px rgba(0, 212, 255, 0.2);
    }
    .alpha-neon-title {
        font-size: 3.5rem; font-weight: 900; color: #fff;
        text-shadow: 0 0 20px #00d4ff, 0 0 40px #00d4ff;
        letter-spacing: 10px; font-family: 'Orbitron', sans-serif;
        margin-bottom: 30px;
    }
    .secure-footer {
        margin-top: 30px; color: #00d4ff; font-family: 'monospace';
        font-size: 0.8rem; letter-spacing: 3px; opacity: 0.7;
    }
    .hasith-badge {
        background: linear-gradient(135deg, #001f3f, #0074d9);
        padding: 15px; border-radius: 15px; border: 1px solid #00d4ff; text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. OS & Web Controller Logic (Unchanged) ---
def execute_system_command(command):
    cmd = command.lower()
    if "youtube" in cmd and "search" in cmd:
        query = cmd.split("search")[-1].replace("for", "").strip()
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return f"හසීත්, මම YouTube හි {query} සෙව්වා."
    elif "open maps" in cmd or "location" in cmd:
        webbrowser.open("https://www.google.com/maps")
        return "GPS පද්ධතිය විවෘත කළා."
    return None

# --- 3. Core Functions (Unchanged) ---
async def speak_alpha(text):
    VOICE = "en-US-SteffanNeural"
    communicate = edge_tts.Communicate(text, VOICE)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio": audio_data += chunk["data"]
    b64 = base64.b64encode(audio_data).decode()
    st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)

def type_effect(text, container):
    full = ""
    for char in text:
        full += char
        container.markdown(f"<div style='font-size:1.1em;'>{full} ⚡</div>", unsafe_allow_html=True)
        time.sleep(0.01)

# --- 4. THE PROGRESSIVE LOADING SCREEN ---
if "loaded" not in st.session_state:
    l_ph = st.empty()
    for i in range(101):
        l_ph.markdown(f"""
            <div class="loader-container">
                <div class="loading-text">INITIALIZING ALPHA CORE...</div>
                <div class="progress-track">
                    <div class="progress-fill" style="width: {i}%;"></div>
                </div>
                <div style="color:#00d4ff; margin-top:15px; font-family:monospace;">SYSTEM BOOT: {i}%</div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(0.04)
    st.session_state.loaded = True; st.rerun()

# --- 5. THE ADVANCED LOGIN SCREEN ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="alpha-neon-title">ALPHA CORE</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        u_name = st.text_input("Username", placeholder="Operator Name")
        bypass = st.text_input("Master Key", type="password", placeholder="••••••••")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("👑 New Reg"): st.toast("Creator Access Only")
        with c2:
            if st.button("🛡️ LOGIN"):
                if bypass == "Hasith12378": 
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Access Denied")
        with c3:
            if st.button("🧪 Bypass"): st.info("Key Required")
            
        st.markdown('<div class="secure-footer">SECURE ACCESS SYSTEM V2.0</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 6. Main Interface (Unchanged Logic) ---
with st.sidebar:
    st.markdown(f'<div class="hasith-badge"><b>HASITH HESHAN</b><br><small>SYSTEM ARCHITECT</small></div>', unsafe_allow_html=True)
    mode = st.radio("Intelligence Unit", ["Llama 3.3 (Normal)", "GPT OSS 120B (Pro)"])
    if st.button("🔌 Log Out"): st.session_state.logged_in = False; st.rerun()

st.markdown('<div class="alpha-neon-title">ALPHA AI</div>', unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

user_input = st.chat_input("State command, Hasith...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    with st.chat_message("assistant"):
        text_ph = st.empty()
        auto_ans = execute_system_command(user_input)
        if auto_ans:
            ans = auto_ans
        else:
            with st.spinner("Thinking..."):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                model = "openai/gpt-oss-120b" if "Pro" in mode else "llama-3.3-70b-versatile"
                res = client.chat.completions.create(model=model, messages=[{"role":"system","content":"You are Alpha AI developed by Hasith."}] + st.session_state.messages[-5:])
                ans = res.choices[0].message.content
        
        asyncio.run(speak_alpha(ans))
        type_effect(ans, text_ph)
        st.session_state.messages.append({"role": "assistant", "content": ans})
