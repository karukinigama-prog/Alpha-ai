import streamlit as st
from groq import Groq
import time
import base64
import asyncio
import edge_tts
import os
from duckduckgo_search import DDGS

# --- 1. System Configurations ---
st.set_page_config(page_title="MOVIE KITT | HASITH HESHAN", page_icon="🏎️", layout="wide")

# --- 2. Imperial Mechanical UI (Full CSS) ---
st.markdown("""
    <style>
    .stApp { background: #000; color: #fff; font-family: 'Share Tech Mono', monospace; }
    
    /* 🏎️ 100-BAR MECHANICAL SCANNER LOADER */
    .loader-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 90vh; }
    .k-title { font-size: 100px; color: red; text-shadow: 0 0 40px red; letter-spacing: 25px; font-weight: 900; margin: 0; }
    .scanner-track { width: 800px; height: 25px; background: #080808; border: 1px solid #333; display: flex; gap: 2px; padding: 4px; overflow: hidden; }
    .light-bar { width: 6px; height: 100%; background: #1a0000; transition: 0.1s; }
    .light-bar.active { background: red; box-shadow: 0 0 15px red; }
    .diag-text { width: 750px; color: red; opacity: 0.6; font-size: 13px; margin-top: 25px; text-align: left; line-height: 1.4; }

    /* SIDEBAR STYLING */
    section[data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid red; }
    .sidebar-option { border-left: 3px solid red; background: #111; padding: 10px; margin-bottom: 8px; border-radius: 4px; font-size: 14px; }
    
    /* GLASS DASHBOARD */
    .glass-banner { background: linear-gradient(180deg, rgba(255,0,0,0.2) 0%, transparent 100%); border: 1px solid rgba(255, 0, 0, 0.4); padding: 20px; border-radius: 15px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- 3. THE MECHANICAL BOOT (7 SECONDS) ---
if "loaded" not in st.session_state:
    l_ph = st.empty()
    for frame in range(45):
        bars = "".join([f'<div class="light-bar {"active" if abs((j%100)-(frame*2.5%100)) < 8 else ""}"></div>' for j in range(100)])
        l_ph.markdown(f"""
            <div class="loader-container">
                <div class="k-title">KITT</div>
                <div class="scanner-track">{bars}</div>
                <div class="diag-text">
                    > ANALYZING BLENDER RIGGING CORE... [OK]<br>
                    > C++ COMPILER INITIALIZED... [OK]<br>
                    > BANDARAWELA LOCAL UPLINK... [STABLE]<br>
                    > MASTER CREATOR: HASITH HESHAN [VERIFIED]
                </div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(0.1)
    st.session_state.loaded = True
    st.rerun()

# --- 4. LOGIN / REGISTER / CREATOR BYPASS ---
if "user_db" not in st.session_state: st.session_state.user_db = {"matheesha": "123", "sadev": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="glass-banner"><h1>KITT SECURITY PORTAL</h1></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🔐 AUTHORIZE", "📝 REGISTER", "👑 CREATOR"])
    with tab1:
        u = st.text_input("Operator ID")
        p = st.text_input("Key", type="password")
        if st.button("LOGIN"):
            if u.lower() in st.session_state.user_db and st.session_state.user_db[u.lower()] == p:
                st.session_state.logged_in, st.session_state.user = True, u
                st.rerun()
    with tab2:
        nu = st.text_input("New ID")
        np = st.text_input("New Key", type="password")
        if st.button("SYNC"): st.session_state.user_db[nu.lower()] = np; st.success("Identity Synced.")
    with tab3:
        bypass = st.text_input("MASTER BYPASS PHRASE", type="password")
        if st.button("OVERRIDE"):
            if bypass == "I CREATED YOU":
                st.session_state.logged_in, st.session_state.user = True, "Hasith"
                st.rerun()
    st.stop()

# --- 5. SIDEBAR WITH 100+ OPTIONS (CAPABILITIES & CODE) ---
with st.sidebar:
    st.markdown("<h2 style='color:red;'>SYSTEM SLIDE-BAR</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    with st.expander("🚀 KITT CAPABILITIES (SUMMARY)"):
        st.markdown("""
        <div class="sidebar-option">✔ Multilingual Neural Voice</div>
        <div class="sidebar-option">✔ C++ Code Architect</div>
        <div class="sidebar-option">✔ Blender Rigging Assistant</div>
        <div class="sidebar-option">✔ Real-time Web Scraper</div>
        <div class="sidebar-output">KITT can analyze complex physics, write clean code, and assist in 3D animation production.</div>
        """, unsafe_allow_html=True)

    with st.expander("💻 WRITE CODE MODULE"):
        st.markdown("<div class='sidebar-option'>Select Language: C++, Python, JS</div>", unsafe_allow_html=True)
        code_type = st.selectbox("Type", ["Main Logic", "UI Design", "Database", "3D Script"])
        if st.button("Generate Template"): st.code("// MOVIE KITT Generated Code\n#include <iostream>\nint main() { return 0; }")

    st.markdown("### DIAGNOSTIC MODES")
    mode = st.radio("Intelligence Level", ["Normal Efficiency", "Pro Master (GPT-OSS)"])
    
    if st.button("SYSTEM SHUTDOWN"): st.session_state.logged_in = False; st.rerun()

# --- 6. CORE LOGIC & VOICE ---
st.markdown(f'<div class="glass-banner">MOVIE KITT | ACTIVE OPERATOR: {st.session_state.user.upper()}</div>', unsafe_allow_html=True)

def play_scanner_sound():
    sound_file = "kitt_scanner.mp3"
    if os.path.exists(sound_file):
        with open(sound_file, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
        time.sleep(1.5)

async def kitt_voice(text):
    communicate = edge_tts.Communicate(text, "en-IE-ConnorNeural")
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio": audio_data += chunk["data"]
    return audio_data

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("State your command, Hasith...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    with st.chat_message("assistant"):
        play_scanner_sound()
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        sys_p = "You are MOVIE KITT. Creator: Hasith Heshan. Expert in C++, Blender, and Physics. Explain clearly in Sinhala or English."
        
        resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":sys_p}] + st.session_state.messages[-5:])
        ans = resp.choices[0].message.content
        
        audio = asyncio.run(kitt_voice(ans))
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{base64.b64encode(audio).decode()}">', unsafe_allow_html=True)
        
        # Typewriter
        ph = st.empty()
        full = ""
        for char in ans:
            full += char
            ph.markdown(full + "▌")
            time.sleep(0.01)
        ph.markdown(full)
        st.session_state.messages.append({"role": "assistant", "content": ans})
