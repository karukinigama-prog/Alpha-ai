import streamlit as st
from groq import Groq
import replicate
import time
import base64
import asyncio
import edge_tts
import os

# --- 1. SYSTEM CORE CONFIGURATION ---
st.set_page_config(page_title="MOVIE KITT | IMPERIAL CORE", page_icon="🏎️", layout="wide")

# --- 2. CSS & UI RULES SYSTEM (THE IMPERIAL LOOK) ---
st.markdown("""
    <style>
    .stApp { background: #000; color: #fff; font-family: 'Share Tech Mono', monospace; }
    
    /* 100-BAR MECHANICAL SCANNER / LOADING SCREEN */
    .loader-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 90vh; }
    .k-title { font-size: 110px; color: red; text-shadow: 0 0 50px red; letter-spacing: 30px; font-weight: 900; margin: 0; }
    .scanner-track { width: 850px; height: 35px; background: #050505; border: 2px solid #333; display: flex; gap: 3px; padding: 5px; overflow: hidden; }
    .light-bar { width: 6px; height: 100%; background: #1a0000; transition: 0.1s; border-radius: 2px; }
    .light-bar.active { background: #ff0000; box-shadow: 0 0 20px #ff0000, 0 0 8px white inset; }

    /* DYNAMIC VOICE VISUALIZER BARS */
    .voice-box { display: flex; align-items: center; justify-content: center; gap: 6px; height: 90px; background: #050505; border: 2px solid #222; width: 320px; margin: 20px auto; border-radius: 12px; }
    .v-bar { width: 14px; background: #ff0000; box-shadow: 0 0 15px #ff0000; border-radius: 2px; height: 12px; transition: height 0.1s; }
    @keyframes voice-jump { 0% { height: 12px; } 50% { height: 75px; } 100% { height: 18px; } }
    .v-anim { animation: voice-jump 0.35s infinite ease-in-out; }

    /* SIDEBAR & UI ELEMENTS */
    section[data-testid="stSidebar"] { background-color: #050505 !important; border-right: 2px solid red; }
    .glass-panel { background: linear-gradient(180deg, rgba(255,0,0,0.2) 0%, transparent 100%); border: 1px solid rgba(255, 0, 0, 0.4); padding: 20px; border-radius: 12px; text-align: center; }
    div.stChatFloatingInputContainer { background-color: transparent !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. THE 7-SECOND LOADING SCREEN ---
if "loaded" not in st.session_state:
    l_ph = st.empty()
    for i in range(45):
        bars = "".join([f'<div class="light-bar {"active" if abs((j%100)-(i*4.5%100)) < 15 else ""}"></div>' for j in range(100)])
        l_ph.markdown(f'<div class="loader-container"><div class="k-title">KITT</div><div class="scanner-track">{bars}</div><div style="color:red; margin-top:20px;">> SYSTEM INITIALIZING... [OK]</div></div>', unsafe_allow_html=True)
        time.sleep(0.1)
    st.session_state.loaded = True
    st.rerun()

# --- 4. SECURITY SYSTEM & BYPASS ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown('<div class="glass-panel"><h1>KITT IMPERIAL SECURITY</h1></div>', unsafe_allow_html=True)
    bypass = st.text_input("MASTER BYPASS KEY", type="password")
    if st.button("OVERRIDE"):
        if bypass == "I CREATED YOU":
            st.session_state.logged_in, st.session_state.user = True, "Hasith Heshan"
            st.rerun()
    st.stop()

# --- 5. API SECRETS INTEGRATION ---
try:
    replicate.client.api_token = st.secrets["REPLICATE_API_KEY"]
except Exception as e:
    st.error("SYSTEM ALERT: Replicate API Key missing in st.secrets.")

# --- 6. VOICE & AUDIO ENGINE ---
def play_kitt_scanner_sound():
    if os.path.exists("kitt_scanner.mp3"):
        with open("kitt_scanner.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
        time.sleep(1.6)

async def generate_male_voice(text):
    is_sinhala = any('\u0d80' <= char <= '\u0dff' for char in text)
    voice = "si-LK-SameerNeural" if is_sinhala else "en-IE-ConnorNeural"
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio": audio_data += chunk["data"]
    return audio_data

# --- 7. SIDEBAR COMMAND CENTER (ORDERED AS REQUESTED) ---
with st.sidebar:
    st.title("KITT COMMANDS")
    st.markdown("---")
    
    # 7.1 Text-to-Image Generation
    with st.expander("🖼️ IMAGE GENERATION"):
        i_prompt = st.text_area("Image Prompt (English):", placeholder="Describe the image...")
        if st.button("GENERATE IMAGE"):
            if i_prompt:
                play_kitt_scanner_sound()
                with st.spinner("Rendering Image..."):
                    try:
                        output = replicate.run("stability-ai/sdxl:39ed7e2e143169866380c10a402517f6e392576b2c45e85c137452d37c6381e4", input={"prompt": i_prompt})
                        st.image(output[0], caption="Rendered by KITT")
                    except Exception as e: st.error(f"Error: {e}")

    # 7.2 Text-to-Video Generation
    with st.expander("🎬 VIDEO GENERATION"):
        v_prompt = st.text_area("Video Prompt (English):", placeholder="Describe the video scene...")
        if st.button("GENERATE VIDEO"):
            if v_prompt:
                play_kitt_scanner_sound()
                with st.spinner("Rendering Video (Takes a few minutes)..."):
                    try:
                        output = replicate.run("zsxkib/animate-diff:05f963032d8478413a9686008892120e2e283f6f9765239a0680145b2b2b2025", input={"prompt": v_prompt})
                        st.video(output[0])
                    except Exception as e: st.error(f"Error: {e}")

    # 7.3 Code Architect & Builder
    with st.expander("💻 CODE ARCHITECT"):
        lang = st.selectbox("Select Core:", ["C++", "Python", "Blender Script"])
        c_prompt = st.text_input("Code Functionality:")
        if st.button("BUILD CODE"):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Write professional {lang} code for: {c_prompt}"}])
            st.code(res.choices[0].message.content)

    # 7.4 System Capabilities Summary
    with st.expander("🚀 CAPABILITIES"):
        st.write("• Dual-Core Generation (Image/Video)\n• Male Neural Voice Engine\n• C++ & Blender Expert\n• YouTube Content Analysis")

    st.markdown("---")
    if st.button("SYSTEM SHUTDOWN"): st.session_state.logged_in = False; st.rerun()

# --- 8. MAIN COMMUNICATION HUB ---
st.markdown(f"<div style='text-align:center; border:1px solid red; padding:15px; border-radius:10px;'>OPERATOR: {st.session_state.user.upper()} | STATUS: ACTIVE</div>", unsafe_allow_html=True)

# The Dynamic Voice Box
v_box = st.empty()
v_box.markdown('<div class="voice-box"><div class="v-bar"></div><div class="v-bar" style="height:40px;"></div><div class="v-bar" style="height:65px;"></div><div class="v-bar" style="height:40px;"></div><div class="v-bar"></div></div>', unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("State your command...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    with st.chat_message("assistant"):
        play_kitt_scanner_sound()
        
        # Animate visualizer while "thinking/speaking"
        v_box.markdown('<div class="voice-box"><div class="v-bar v-anim"></div><div class="v-bar v-anim"></div><div class="v-bar v-anim"></div><div class="v-bar v-anim"></div><div class="v-bar v-anim"></div></div>', unsafe_allow_html=True)
        
        # Connect to Groq LLM
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        sys_p = "You are MOVIE KITT. Creator: Hasith Heshan. Professional Male Voice. Expert in Blender, C++, and YouTube optimization."
        resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":sys_p}] + st.session_state.messages[-5:])
        ans = resp.choices[0].message.content
        
        # Audio Generation
        audio = asyncio.run(generate_male_voice(ans))
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{base64.b64encode(audio).decode()}">', unsafe_allow_html=True)
        
        # Typewriter Effect Output
        ph = st.empty(); full = ""
        for char in ans:
            full += char; ph.markdown(full + "▌"); time.sleep(0.015)
        ph.markdown(full)
        
        # Stop animation
        v_box.markdown('<div class="voice-box"><div class="v-bar"></div><div class="v-bar" style="height:40px;"></div><div class="v-bar" style="height:65px;"></div><div class="v-bar" style="height:40px;"></div><div class="v-bar"></div></div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": ans})
