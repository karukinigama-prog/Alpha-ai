import streamlit as st
from groq import Groq
import time
import base64
import asyncio
import edge_tts
import os

# --- 1. CORE SYSTEM CONFIG ---
st.set_page_config(page_title="ALPHA AI | ELITE", page_icon="🏎️", layout="wide")

# --- 2. THE SIGNATURE IMPERIAL UI (RED & BLACK) ---
st.markdown("""
    <style>
    .stApp { background: #000; color: #fff; font-family: 'Share Tech Mono', monospace; }
    
    /* ALPHA SCANNER - 100 LIGHT BARS */
    .loader-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 90vh; }
    .alpha-title { font-size: 80px; color: red; text-shadow: 0 0 30px red; letter-spacing: 15px; font-weight: 900; }
    .scanner-track { width: 800px; height: 30px; background: #050505; border: 1px solid #333; display: flex; gap: 2px; padding: 4px; overflow: hidden; }
    .bar { width: 6px; height: 100%; background: #1a0000; transition: 0.1s; }
    .bar.active { background: #ff0000; box-shadow: 0 0 15px #ff0000; }

    /* VOICE ORB VISUALIZER */
    .voice-orb { display: flex; align-items: center; justify-content: center; gap: 5px; height: 60px; margin: 20px 0; }
    .orb-bar { width: 8px; background: #ff0000; box-shadow: 0 0 10px #ff0000; border-radius: 5px; height: 10px; }
    @keyframes pulse { 0% { height: 10px; } 50% { height: 50px; } 100% { height: 15px; } }
    .pulse-anim { animation: pulse 0.4s infinite ease-in-out; }
    
    /* SIDEBAR STYLING */
    section[data-testid="stSidebar"] { background-color: #050505 !important; border-right: 2px solid red; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 7-SECOND ALPHA BOOT SEQUENCE ---
if "booted" not in st.session_state:
    placeholder = st.empty()
    for i in range(45):
        bars_html = "".join([f'<div class="bar {"active" if abs((j%100)-(i*4.5%100)) < 15 else ""}"></div>' for j in range(100)])
        placeholder.markdown(f'<div class="loader-container"><div class="alpha-title">ALPHA AI</div><div class="scanner-track">{bars_html}</div><div style="color:red; margin-top:15px;">INITIALIZING SUPER ANIMATION ENGINE...</div></div>', unsafe_allow_html=True)
        time.sleep(0.1)
    st.session_state.booted = True
    st.rerun()

# --- 4. CREATOR AUTHENTICATION ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🛡️ ALPHA SYSTEM ACCESS")
    key = st.text_input("ENTER MASTER KEY:", type="password")
    if st.button("AUTHENTICATE"):
        if key == "I CREATED YOU":
            st.session_state.auth = True
            st.session_state.user = "Hasith Heshan"
            st.rerun()
    st.stop()

# --- 5. NEURAL VOICE ENGINE ---
async def alpha_speak(text):
    is_sinhala = any('\u0d80' <= char <= '\u0dff' for char in text)
    voice = "si-LK-SameerNeural" if is_sinhala else "en-IE-ConnorNeural"
    comm = edge_tts.Communicate(text, voice)
    audio = b""
    async for chunk in comm.stream():
        if chunk["type"] == "audio": audio += chunk["data"]
    return audio

# --- 6. COMMAND CENTER (SIDEBAR) ---
with st.sidebar:
    st.header("COMMAND CENTER")
    st.markdown("---")
    
    with st.expander("🛠️ BLENDER TOOLKIT"):
        st.write("• Auto-Rigging Scripts\n• IK/FK Switcher\n• Weight Paint Optimizer")
        if st.button("GENERATE RIG SCRIPT"): st.code("# Blender Rigging Template\nimport bpy")

    with st.expander("📺 YOUTUBE SEO (SUPER ANIMATION)"):
        st.text_input("Video Topic:")
        if st.button("GET TAGS"): st.success("Tags Generated for YouTube!")

    with st.expander("💻 CODE ARCHITECT"):
        lang = st.selectbox("Language", ["Python", "C++", "Streamlit"])
        if st.button("BUILD"): st.code(f"# Alpha {lang} Architect Active")

    st.markdown("---")
    if st.button("FORCE SHUTDOWN"):
        st.session_state.auth = False
        st.rerun()

# --- 7. MAIN INTERFACE ---
st.markdown(f"<div style='text-align:center; border:1px solid red; padding:10px; border-radius:5px;'>OPERATOR: {st.session_state.user.upper()} | STATUS: STABLE</div>", unsafe_allow_html=True)

orb_placeholder = st.empty()
orb_placeholder.markdown('<div class="voice-orb"><div class="orb-bar"></div><div class="orb-bar" style="height:30px;"></div><div class="orb-bar" style="height:45px;"></div><div class="orb-bar" style="height:30px;"></div><div class="orb-bar"></div></div>', unsafe_allow_html=True)

if "chat_history" not in st.session_state: st.session_state.chat_history = []
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

user_cmd = st.chat_input("Command Alpha AI...")

if user_cmd:
    st.session_state.chat_history.append({"role": "user", "content": user_cmd})
    with st.chat_message("user"): st.markdown(user_cmd)

    with st.chat_message("assistant"):
        orb_placeholder.markdown('<div class="voice-orb"><div class="orb-bar pulse-anim"></div><div class="orb-bar pulse-anim"></div><div class="orb-bar pulse-anim"></div><div class="orb-bar pulse-anim"></div><div class="orb-bar pulse-anim"></div></div>', unsafe_allow_html=True)
        
        # Groq Llama Integration
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are Alpha AI. Created by Hasith Heshan. Expert in 3D Modeling (Blender) and Python."}] + st.session_state.chat_history[-5:]
        )
        answer = response.choices[0].message.content
        
        # Audio playback
        audio_content = asyncio.run(alpha_speak(answer))
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{base64.b64encode(audio_content).decode()}">', unsafe_allow_html=True)
        
        # Text animation
        ph = st.empty(); full_txt = ""
        for c in answer:
            full_txt += c; ph.markdown(full_txt + "▌"); time.sleep(0.01)
        ph.markdown(full_txt)
        
        orb_placeholder.markdown('<div class="voice-orb"><div class="orb-bar"></div><div class="orb-bar" style="height:30px;"></div><div class="orb-bar" style="height:45px;"></div><div class="orb-bar" style="height:30px;"></div><div class="orb-bar"></div></div>', unsafe_allow_html=True)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
