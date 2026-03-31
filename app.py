import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
import requests, base64, asyncio, io, json
import edge_tts
from PIL import Image
import time
import urllib.parse
import random
from duckduckgo_search import DDGS 

# -----------------------
# 1. Page Config & Identity
# -----------------------
st.set_page_config(page_title="Alpha AI | Created by Hasith", layout="wide", page_icon="⚡")

# --- GOOGLE VERIFICATION TAG ---
st.markdown('<meta name="google-site-verification" content="W6jIGzCkkez2SpjygP6z0dJfinBNALmw2Hv-MkJvFB0" />', unsafe_allow_html=True)

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
</style>  """, unsafe_allow_html=True)

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
# 5. API Setup (Managed via Streamlit Secrets)
# -----------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")
POLLINATIONS_KEY = st.secrets.get("POLLINATIONS_API_KEY", "sk_Z0oEnm05szbphnbZ9ClRCukKV2HyDMH5")
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY")

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

def web_search_tool(query):
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=3)]
            if results:
                context = "\n".join([f"Source: {r['title']} - {r['body']}" for r in results])
                return context
    except: return ""
    return ""

def generate_video_robust(prompt):
    models = ["guoyww/AnimateDiff", "cerspense/zeroscope_v2_576w"]
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    for model_id in models:
        try:
            API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=60)
            if response.status_code == 200: return response.content
        except: continue
    return None

# -----------------------
# 7. Sidebar Control
# -----------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluent/100/000000/artificial-intelligence.png", width=70)
    st.title("Alpha Control")
    st.markdown(f"Operator: {st.session_state.user_full_name}")
    st.divider()
    mode = st.radio("Intelligence Level", ["Normal (Llama 3.3 70B)", "Pro (Llama 3.1 70B)", "Ultra (DeepSeek 671B)"])
    web_search_on = st.checkbox("Web Search (Real-time)", value=False)
    voice_on = st.checkbox("Voice Output", value=True)
    st.divider()
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()
    st.write("---")
    st.caption("Created by Hasith | Bandarawela Central College")

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
                        headers = {"Authorization": f"Bearer {POLLINATIONS_KEY}"}  
                        response = requests.get(url, headers=headers, timeout=60)  
                        if response.status_code == 200:  
                            st.image(response.content, caption=f"Created for {st.session_state.user_full_name}", use_container_width=True)  
                            st.download_button("Download Image 📥", response.content, f"alpha_{seed}.png", "image/png")  
                        else: st.error(f"Generation Failed: {response.status_code}")  
                    except Exception as e: st.error(f"Error: {e}")  
        st.markdown('</div>', unsafe_allow_html=True)

with tab_vid:
    with st.container():
        st.markdown('<div class="lab-box">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        vid_p = col1.text_input("Describe video scene:", key="vid_prompt")
        if col2.button("Generate Video"):
            if vid_p:
                with st.spinner("Alpha is directing... 🎬"):
                    vid_data = generate_video_robust(vid_p)
                    if vid_data:
                        st.video(vid_data)
                        st.download_button("Download Video 📥", vid_data, "alpha_video.mp4")
                    else: st.error("Cinema Lab is currently busy.")
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
            search_context = web_search_tool(user_input) if web_search_on else ""
            
            # --- IDENTITY SETTINGS (DO NOT CHANGE) ---
            sys_msg = (
                f"Your name is Alpha AI. You are a highly advanced and friendly AI assistant "
                f"created and developed by Hasith from Sri Lanka. You are currently studying "
                f"at Bandarawela Central College. You should be helpful, joking, and talk "
                f"like a close friend. Search context: {search_context}"
            )
            
            try:
                if "Ultra" in mode:
                    response = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                        data=json.dumps({
                            "model": "deepseek/deepseek-chat",
                            "messages": [{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:],
                            "temperature": 1.1
                        })
                    )
                    data = response.json()
                    if 'choices' in data:
                        full_res = data['choices'][0]['message']['content']
                        res_placeholder.markdown(full_res)
                    else:
                        error_msg = data.get('error', {}).get('message', 'Unknown API Error')
                        st.error(f"API Error: {error_msg}")
                        full_res = "Master, Alpha is facing a brain connectivity issue. Please check the API."
                else:
                    if "Normal" in mode:
                        selected_model = "llama-3.3-70b-versatile"
                        temp, top_p, max_tokens = 0.7, 0.9, 4096
                    else:
                        selected_model = "llama-3.1-70b-versatile"
                        temp, top_p, max_tokens = 1.0, 1.0, 8192
                    
                    stream = groq_client.chat.completions.create(
                        model=selected_model,
                        messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:],
                        temperature=temp,
                        top_p=top_p,
                        max_tokens=max_tokens,
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

st.markdown("---")
st.caption("Alpha AI Project | Bandarawela Central College | Created by Hasith")
