import streamlit as st
from groq import Groq
import time
import base64
import asyncio
import edge_tts
import os
import webbrowser
from PyPDF2 import PdfReader

# --- 1. Page Configuration & Cyber UI (Enhanced with Cyberpunk Loading) ---
st.set_page_config(page_title="Alpha AI | Next-Gen", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Inter:wght@300;900&display=swap');
    
    .stApp { background: #02050a; color: #ffffff; font-family: 'Inter', sans-serif; }
    
    /* ALPHA NEON TITLE */
    .alpha-neon-title {
        font-size: clamp(2.5em, 8vw, 4em);
        font-weight: 900;
        text-align: center;
        color: #fff;
        text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff, 0 0 40px #00d4ff;
        letter-spacing: clamp(5px, 3vw, 12px);
        font-family: 'Orbitron', sans-serif;
        margin-bottom: 20px;
    }

    /* --- CYBER LOADING SCREEN CSS --- */
    .loader-container {
        display: flex; flex-direction: column; align-items: center; justify-content: center; height: 90vh;
        background: radial-gradient(circle, #051937 0%, #000000 100%);
    }
    
    .loading-text {
        font-family: 'Orbitron', sans-serif;
        color: #00d4ff;
        font-size: 3rem;
        font-weight: 900;
        letter-spacing: 15px;
        text-shadow: 0 0 20px #00d4ff;
        margin-bottom: 30px;
        animation: glitch 1s infinite;
    }

    .progress-track {
        width: 600px;
        height: 12px;
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid #00d4ff;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
        position: relative;
    }

    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #00d4ff, #005f73);
        box-shadow: 0 0 20px #00d4ff;
        transition: width 0.1s ease-out;
    }

    .system-status {
        margin-top: 20px;
        font-family: 'monospace';
        color: #00d4ff;
        font-size: 0.9rem;
        letter-spacing: 2px;
    }

    @keyframes glitch {
        0% { transform: translate(0); }
        20% { transform: translate(-2px, 2px); }
        40% { transform: translate(-2px, -2px); }
        60% { transform: translate(2px, 2px); }
        80% { transform: translate(2px, -2px); }
        100% { transform: translate(0); }
    }

    /* GLASS CARD UI */
    .glass-card {
        background: rgba(0, 212, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 212, 255, 0.2);
        padding: 20px;
        border-radius: 20px;
        margin-bottom: 20px;
    }
    
    .hasith-badge {
        background: linear-gradient(135deg, #001f3f, #0074d9);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #00d4ff;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. OS & Web Controller Logic (Unchanged) ---
def execute_system_command(command):
    cmd = command.lower()
    if "youtube" in cmd and "search" in cmd:
        query = cmd.split("search")[-1].replace("for", "").strip()
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return f"හසීත්, මම YouTube හි {query} සෙව්වා. දැන් ඔබට වීඩියෝව තෝරාගත හැකියි."
    elif "open maps" in cmd or "location" in cmd:
        webbrowser.open("https://www.google.com/maps")
        return "GPS පද්ධතිය සහ සිතියම් විවෘත කළා, හසීත්."
    elif "open whatsapp" in cmd:
        webbrowser.open("https://web.whatsapp.com")
        return "WhatsApp පණිවිඩ පද්ධතිය සක්‍රීය කළා."
    elif "search for" in cmd:
        query = cmd.split("search for")[-1].strip()
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"මම Google හරහා {query} ගැන තොරතුරු සෙව්වා."
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
    return len(audio_data) / 15500

def type_effect(text, container):
    full = ""
    for char in text:
        full += char
        container.markdown(f"<div style='font-size:1.1em;'>{full} ⚡</div>", unsafe_allow_html=True)
        time.sleep(0.01)
    container.markdown(text)

# --- 4. Initialization & NEW CYBER LOADING SCREEN ---
if "loaded" not in st.session_state:
    placeholder = st.empty()
    for i in range(101):
        # අර පින්තූරයේ තියෙන විදියටම ලස්සන Loading Bar එකක්
        placeholder.markdown(f"""
            <div class="loader-container">
                <div class="loading-text">LOADING...</div>
                <div class="progress-track">
                    <div class="progress-fill" style="width: {i}%;"></div>
                </div>
                <div class="system-status">ALPHA CORE V2.0 INITIALIZING: {i}%</div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(0.04) # තත්පර 4කට ආසන්න කාලයක්
    st.session_state.loaded = True
    st.rerun()

# --- 5. Security & Login ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown('<div class="alpha-neon-title">ALPHA CORE</div>', unsafe_allow_html=True)
    bypass = st.text_input("Master Key", type="password")
    if st.button("Unlock Alpha"):
        if bypass == "Hasith12378": st.session_state.logged_in = True; st.rerun()
    st.stop()

# --- 6. Sidebar & UI ---
with st.sidebar:
    st.markdown(f'<div class="hasith-badge"><b>HASITH</b><br><small>SYSTEM ARCHITECT</small></div>', unsafe_allow_html=True)
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
            with st.spinner("Neural thinking..."):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                model = "openai/gpt-oss-120b" if "Pro" in mode else "llama-3.3-70b-versatile"
                res = client.chat.completions.create(model=model, messages=[{"role":"system","content":"You are Alpha AI developed by Hasith."}] + st.session_state.messages[-5:])
                ans = res.choices[0].message.content
        
        asyncio.run(speak_alpha(ans))
        type_effect(ans, text_ph)
        st.session_state.messages.append({"role": "assistant", "content": ans})
