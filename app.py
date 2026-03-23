import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
import requests, base64, asyncio, io
import edge_tts
from PIL import Image

# -----------------------
# 1. Page Config & Identity
# -----------------------
st.set_page_config(page_title="Alpha AI | Created by Hasith", layout="wide", page_icon="⚡")

# -----------------------
# 2. Session State Init
# -----------------------
if "messages" not in st.session_state: st.session_state.messages=[]
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "user_full_name" not in st.session_state: st.session_state.user_full_name=None

# -----------------------
# 3. Custom UI Styling
# -----------------------
st.markdown("""
<style>
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:20px; font-size: 22px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }
    .stChatMessage { border-radius: 15px; }
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; height: 45px; font-weight: bold; border: 1px solid #FFD700; transition: 0.3s; }
    div.stButton > button:hover { background-color: #FFD700; color: #000; }
    .lab-box { border: 1px solid #333; padding: 20px; border-radius: 15px; background: #0e1117; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# -----------------------
# 4. Login System
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="premium-banner">ALPHA CORE SYSTEM ACCESS</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#FFD700; font-weight:bold;">Developed by Hasith</p>', unsafe_allow_html=True)
    name = st.text_input("Operator Name")
    password = st.text_input("Master Key", type="password")
    if st.button("Initialize Alpha"):
        if password == "Hasith12378":
            st.session_state.user_full_name = name or "Hasith"
            st.session_state.logged_in = True
            st.rerun()
        else: st.error("Access Denied: Invalid Master Key")
    st.stop()

# -----------------------
# 5. API Setup
# -----------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")

groq_client = Groq(api_key=GROQ_API_KEY)
# We use InferenceClient without a provider to stay on the free tier longer
hf_client = InferenceClient(token=HF_TOKEN)

# -----------------------
# 6. Helper Functions
# -----------------------
async def speak_alpha(text):
    try:
        comm = edge_tts.Communicate(text, "en-US-SteffanNeural")
        audio = b""
        async for chunk in comm.stream():
            if chunk["type"]=="audio": audio+=chunk["data"]
        if audio:
            b64 = base64.b64encode(audio).decode()
            st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: pass

def generate_image_direct(prompt):
    # Direct API call to Z-Image-Turbo to avoid Provider payment errors
    API_URL = "https://api-inference.huggingface.co/models/Tongyi-MAI/Z-Image-Turbo"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=60)
        if response.status_code == 200:
            return response.content
        elif response.status_code == 503:
            st.warning("Model is currently loading on Hugging Face. Try again in 30 seconds.")
        return None
    except:
        return None

def generate_video_direct(prompt):
    # Direct API call to Wan2.1
    API_URL = "https://api-inference.huggingface.co/models/Wan-AI/Wan2.1-T2V-1.3B"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=180)
        if response.status_code == 200:
            return response.content
        return None
    except:
        return None

# -----------------------
# 7. Main Interface
# -----------------------
st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

tab_img, tab_vid = st.tabs(["🖼 Image Generation Lab", "🎬 Cinema Lab (AI Video)"])

with tab_img:
    with st.container():
        st.markdown('<div class="lab-box">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        img_p = col1.text_input("Describe image:", key="img_prompt")
        if col2.button("Generate Photo"):
            if img_p:
                with st.spinner("Alpha is painting (Direct Connection)... 🖌️"):
                    img_data = generate_image_direct(img_p)
                    if img_data:
                        st.image(img_data, caption=f"Created for {st.session_state.user_full_name}")
                        st.download_button("Download Image", img_data, "alpha_image.png")
                    else:
                        st.error("Free Credits might be low or Model is busy. Try a different Hugging Face Token.")
        st.markdown('</div>', unsafe_allow_html=True)

with tab_vid:
    with st.container():
        st.markdown('<div class="lab-box">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        vid_p = col1.text_input("Describe video scene:", key="vid_prompt")
        if col2.button("Generate Video"):
            if vid_p:
                with st.spinner("Alpha is directing Wan2.1... 🎬"):
                    vid_data = generate_video_direct(vid_p)
                    if vid_data:
                        st.video(vid_data)
                        st.download_button("Download Video", vid_data, "alpha_video.mp4")
                    else:
                        st.error("Video server is busy. Please try again shortly.")
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# 8. Chat System
# -----------------------
st.write("### 💬 Heartfelt Conversation")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

user_input = st.chat_input("State your command, Master...")

if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"): st.markdown(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("Alpha is thinking..."):
            res_placeholder = st.empty()
            sys_msg = "You are Alpha AI, a heartfelt assistant created by Hasith. Respond warmly."
            try:
                stream = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
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
                asyncio.run(speak_alpha(full_res))
                st.session_state.messages.append({"role":"assistant","content":full_res})
            except Exception as e: st.error(f"Brain Error: {e}")
