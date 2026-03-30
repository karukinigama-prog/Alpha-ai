import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
import requests, base64, asyncio, io
import edge_tts
import urllib.parse
import random  

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

# --- FIXED: Pollinations Video Generation ---
def generate_video_pollinations(prompt, duration=4, aspect_ratio="16:9", audio=True):
    encoded_prompt = urllib.parse.quote(prompt)
    url = (
        f"https://gen.pollinations.ai/video/{encoded_prompt}"
        f"?model=wan&duration={duration}&aspectRatio={aspect_ratio}&audio={str(audio).lower()}"
    )
    try:
        response = requests.get(url, timeout=120)
        if response.status_code == 200:
            return io.BytesIO(response.content)  # wrap in BytesIO for Streamlit
        else:
            st.error(f"Video generation failed: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# -----------------------
# 7. Sidebar Control
# -----------------------
with st.sidebar:
    st.title("Alpha Control")
    st.markdown(f"**Operator:** {st.session_state.user_full_name}")
    mode = st.radio("Intelligence Level", ["Normal (Llama 3.3 Fast)", "Pro (GPT OSS 120B)"])
    voice_on = st.checkbox("Voice Output", value=True)
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

# -----------------------
# 8. AI Multimodal Labs
# -----------------------
tab_img, tab_vid = st.tabs(["🖼 Image Generation Lab", "🎬 Cinema Lab (AI Video)"])

with tab_img:
    with st.container():
        st.markdown('<div class="lab-box">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        img_p = col1.text_input("Describe image:", key="img_prompt")
        img_model = st.selectbox("Intelligence Mode:", ["flux", "turbo", "zimage", "p-image"], key="img_model_select")
        
        if col2.button("Generate Photo"):
            if img_p:
                with st.spinner("Alpha is painting... 🖌️"):
                    try:
                        encoded_p = urllib.parse.quote(img_p)
                        seed = random.randint(1, 1000000)
                        url = f"https://gen.pollinations.ai/image/{encoded_p}?width=1024&height=1024&seed={seed}&model={img_model}&nologo=true"
                        response = requests.get(url, timeout=60)
                        
                        if response.status_code == 200:
                            st.image(response.content, caption=f"Created for {st.session_state.user_full_name}", use_container_width=True)
                            st.download_button("Download Image 📥", response.content, f"alpha_{seed}.png", "image/png")
                        else:
                            st.error(f"Generation Failed: {response.status_code}")
                    except Exception as e: st.error(f"Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

with tab_vid:
    with st.container():
        st.markdown('<div class="lab-box">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        vid_p = col1.text_input("Describe video scene:", key="vid_prompt")
        
        v_col1, v_col2 = st.columns(2)
        v_ratio = v_col1.selectbox("Aspect Ratio", ["16:9", "9:16"])
        v_audio = v_col2.checkbox("Include Audio", value=True)

        if col2.button("Generate Video"):
            if vid_p:
                with st.spinner("Alpha is directing via Wan Model... 🎬 (This may take a minute)"):
                    vid_data = generate_video_pollinations(vid_p, duration=4, aspect_ratio=v_ratio, audio=v_audio)
                    if vid_data:
                        st.video(vid_data)
                        st.download_button("Download Video 📥", vid_data.getvalue(), "alpha_video.mp4")
                    else:
                        st.error("Cinema Lab is currently busy or Request failed.")
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# 9. Hybrid Intelligence Chat
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
            selected_model = "llama-3.3-70b-versatile" if "Normal" in mode else "llama-3.1-8b-instant" 
            sys_msg = f"You are Alpha AI, a heartfelt assistant created by Hasith Karunarathna. Respond warmly."
            try:
                stream = groq_client.chat.completions.create(
                    model=selected_model,
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
                if voice_on: asyncio.run(speak_alpha(full_res))
                st.session_state.messages.append({"role":"assistant","content":full_res})
            except Exception as e: st.error(f"Brain Error: {e}")
