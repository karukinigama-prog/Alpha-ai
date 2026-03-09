import streamlit as st
from groq import Groq
import time
import base64
import asyncio
import edge_tts
import os
import requests

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="MOVIE KITT | VIDEO GEN", page_icon="🏎️", layout="wide")

# --- 2. IMPERIAL DYNAMIC UI (CSS) ---
st.markdown("""
    <style>
    .stApp { background: #000; color: #fff; font-family: 'Share Tech Mono', monospace; }
    
    /* THE 100-BAR SCANNER */
    .loader-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 85vh; }
    .k-title { font-size: 110px; color: red; text-shadow: 0 0 50px red; letter-spacing: 30px; font-weight: 900; margin: 0; }
    .scanner-track { width: 850px; height: 30px; background: #050505; border: 1.5px solid #444; display: flex; gap: 2px; padding: 5px; overflow: hidden; }
    .light-bar { width: 6.5px; height: 100%; background: #1a0000; transition: 0.1s; }
    .light-bar.active { background: #ff0000; box-shadow: 0 0 15px #ff0000; }

    /* VOICE BOX VISUALIZER */
    .voice-box { display: flex; align-items: center; justify-content: center; gap: 5px; height: 80px; background: #000; border: 2px solid #222; padding: 15px; width: 250px; margin: 0 auto; border-radius: 8px; }
    .v-bar { width: 12px; background: #ff0000; box-shadow: 0 0 12px #ff0000; border-radius: 2px; height: 10px; }
    @keyframes voice-jump { 0% { height: 10px; } 50% { height: 60px; } 100% { height: 15px; } }
    .v-anim { animation: voice-jump 0.3s infinite ease-in-out; }

    /* SIDEBAR & PANELS */
    section[data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1.5px solid red; }
    .glass-panel { background: linear-gradient(180deg, rgba(255,0,0,0.2) 0%, transparent 100%); border: 1px solid rgba(255, 0, 0, 0.4); padding: 20px; border-radius: 12px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- 3. THE MECHANICAL SCANNER BOOT ---
if "loaded" not in st.session_state:
    l_ph = st.empty()
    for i in range(40):
        bars = "".join([f'<div class="light-bar {"active" if abs((j%100)-(i*3.5%100)) < 12 else ""}"></div>' for j in range(100)])
        l_ph.markdown(f'<div class="loader-container"><div class="k-title">KITT</div><div class="scanner-track">{bars}</div></div>', unsafe_allow_html=True)
        time.sleep(0.1)
    st.session_state.loaded = True
    st.rerun()

# --- 4. BYPASS & SECURITY ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown('<div class="glass-panel"><h1>KITT IMPERIAL ACCESS</h1></div>', unsafe_allow_html=True)
    bypass = st.text_input("MASTER BYPASS KEY", type="password")
    if st.button("OVERRIDE"):
        if bypass == "I CREATED YOU":
            st.session_state.logged_in, st.session_state.user = True, "Hasith"
            st.rerun()
    st.stop()

# --- 5. VOICE & SOUND ENGINE (MALE SINHALA) ---
def play_kitt_sound():
    if os.path.exists("kitt_scanner.mp3"):
        with open("kitt_scanner.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
        time.sleep(1.6)

async def speak_male(text):
    is_sinhala = any('\u0d80' <= char <= '\u0dff' for char in text)
    voice = "si-LK-SameerNeural" if is_sinhala else "en-IE-ConnorNeural"
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio": audio_data += chunk["data"]
    return audio_data

# --- 6. SIDEBAR: VIDEO GENERATION CONTROL ---
with st.sidebar:
    st.markdown("### SYSTEM SLIDE-BAR")
    with st.expander("🚀 KITT CAPABILITIES"):
        st.write("• Video Generation Core\n• Multilingual Male Voice\n• Blender & C++ Expert")
    
    st.markdown("---")
    st.markdown("### 🎬 VIDEO GENERATOR")
    v_prompt = st.text_area("Describe Video Scene (English for Best Results):", placeholder="A red sports car drifting in Bandarawela hills...")
    if st.button("GENERATE VIDEO"):
        if v_prompt:
            st.warning("Connecting to Imperial Cloud... This may take a moment.")
            # This is where the Video Generation API (like Replicate) connects
            st.info("Video Generation Module initialized for Hasith Heshan.")
            # Note: Real video generation requires a paid API Key from Replicate or OpenAI.

# --- 7. MAIN INTERFACE ---
st.markdown(f'<div class="glass-panel">MOVIE KITT | OPERATOR: {st.session_state.user.upper()}</div>', unsafe_allow_html=True)

v_box = st.empty()
v_box.markdown('<div class="voice-box"><div class="v-bar"></div><div class="v-bar" style="height:30px;"></div><div class="v-bar" style="height:50px;"></div><div class="v-bar" style="height:30px;"></div><div class="v-bar"></div></div>', unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("State command, Hasith...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    with st.chat_message("assistant"):
        play_kitt_sound()
        v_box.markdown('<div class="voice-box"><div class="v-bar v-anim"></div><div class="v-bar v-anim"></div><div class="v-bar v-anim"></div><div class="v-bar v-anim"></div><div class="v-bar v-anim"></div></div>', unsafe_allow_html=True)
        
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        sys_p = "You are MOVIE KITT. Creator: Hasith Heshan. Expert in Blender, C++, and Space. Speak in Sinhala or English with a professional male voice."
        resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":sys_p}] + st.session_state.messages[-5:])
        ans = resp.choices[0].message.content
        
        audio = asyncio.run(speak_male(ans))
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{base64.b64encode(audio).decode()}">', unsafe_allow_html=True)
        
        ph = st.empty(); full = ""
        for char in ans:
            full += char; ph.markdown(full + "▌"); time.sleep(0.01)
        ph.markdown(full)
        
        v_box.markdown('<div class="voice-box"><div class="v-bar"></div><div class="v-bar" style="height:30px;"></div><div class="v-bar" style="height:50px;"></div><div class="v-bar" style="height:30px;"></div><div class="v-bar"></div></div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": ans})
