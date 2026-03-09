import streamlit as st
from groq import Groq
import time
import base64
import asyncio
import edge_tts
import os
from duckduckgo_search import DDGS

# --- 1. CORE SYSTEM CONFIG ---
st.set_page_config(page_title="MOVIE KITT | GLOBAL HUB", page_icon="🏎️", layout="wide")

# --- 2. THE MECHANICAL SCANNER SOUND ---
def play_kitt_sound():
    # Ensure you have 'kitt_scanner.mp3' in your folder
    sound_file = "kitt_scanner.mp3"
    if os.path.exists(sound_file):
        with open(sound_file, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
        time.sleep(1.8) # Wait for the 'WVV WVV' to finish

# --- 3. IMPERIAL STYLING ---
st.markdown("""
    <style>
    .stApp { background: #000; color: #fff; font-family: 'Share Tech Mono', monospace; }
    .loader-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 85vh; }
    .k-title { font-size: 80px; color: red; text-shadow: 0 0 30px red; letter-spacing: 15px; }
    .scanner-track { width: 400px; height: 12px; background: #111; border: 1px solid #333; position: relative; overflow: hidden; }
    .scanner-light { width: 100px; height: 100%; background: red; box-shadow: 0 0 20px red; position: absolute; animation: scan 1.2s infinite alternate ease-in-out; }
    @keyframes scan { 0% { left: -10%; } 100% { left: 85%; } }
    .diag-box { color: red; opacity: 0.6; font-size: 13px; margin-top: 20px; text-align: left; }
    </style>
""", unsafe_allow_html=True)

# --- 4. ⚙️ LOADING SCREEN (7 SECONDS) ---
if "loaded" not in st.session_state:
    l_ph = st.empty()
    with l_ph.container():
        st.markdown(f"""<div class="loader-container"><div class="k-title">KITT</div><div class="scanner-track"><div class="scanner-light"></div></div>
        <div class="diag-box">> RELOADING MULTILINGUAL DATABASE... [OK]<br>> SYNCING VOICE SYNTHESIZER... [OK]<br>> MASTER: HASITH HESHAN [FOUND]</div></div>""", unsafe_allow_html=True)
        time.sleep(7)
    st.session_state.loaded = True
    st.rerun()

# --- 5. AUTHENTICATION (The Master Key: I CREATED YOU) ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("KITT SECURITY")
        bypass = st.text_input("ENTER MASTER PHRASE", type="password")
        if st.button("AUTHORIZE"):
            if bypass == "I CREATED YOU":
                st.session_state.logged_in = True; st.session_state.user = "Hasith"
                st.rerun()
            else: st.error("ACCESS DENIED")
    st.stop()

# --- 6. VOICE & LOGIC ---
async def speak_text(text):
    # Auto-detects language and speaks. Connor is good for English, 
    # but KITT will use a clear neural voice for all.
    communicate = edge_tts.Communicate(text, "en-IE-ConnorNeural")
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio": audio_data += chunk["data"]
    return audio_data

# --- 7. MAIN INTERFACE ---
st.title("MOVIE KITT COMMAND CENTER")

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("State your command, Hasith...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    with st.chat_message("assistant"):
        text_ph = st.empty()
        # 1. Play Scanner Sound first
        play_kitt_sound()
        
        # 2. Get AI Response
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        sys_prompt = "You are MOVIE KITT. You were created by Hasith Heshan. You are a multilingual expert. Always explain things clearly and in detail. Respond in the language Hasith uses (Sinhala/English/etc)."
        
        resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":sys_prompt}] + st.session_state.messages[-5:])
        ans = resp.choices[0].message.content
        
        # 3. Voice & Typewriter
        audio = asyncio.run(speak_text(ans))
        b64 = base64.b64encode(audio).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
        
        full = ""
        for char in ans:
            full += char
            text_ph.markdown(full + "▌")
            time.sleep(0.01)
        text_ph.markdown(full)
        st.session_state.messages.append({"role": "assistant", "content": ans})
