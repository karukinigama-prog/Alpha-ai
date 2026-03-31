import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
from supabase import create_client, Client
import extra_streamlit_components as stx
import requests, base64, asyncio, io, json, datetime
import edge_tts
from PIL import Image
import urllib.parse
import random
from duckduckgo_search import DDGS 

# -----------------------
# 1. Page Config & Identity
# -----------------------
st.set_page_config(page_title="Alpha AI | Created by Hasith", layout="wide", page_icon="⚡")
st.markdown('<meta name="google-site-verification" content="W6jIGzCkkez2SpjygP6z0dJfinBNALmw2Hv-MkJvFB0" />', unsafe_allow_html=True)

# -----------------------
# 2. Session & Cookie Management
# -----------------------
if "messages" not in st.session_state: st.session_state.messages = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_email" not in st.session_state: st.session_state.user_email = None

cookie_manager = stx.CookieManager()
saved_email = cookie_manager.get(cookie="alpha_persistent_login")

# -----------------------
# 3. API & Database Setup
# -----------------------
# Getting credentials from your Supabase settings
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")
POLLINATIONS_KEY = st.secrets.get("POLLINATIONS_API_KEY", "sk_Z0oEnm05szbphnbZ9ClRCukKV2HyDMH5")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    st.error("Check Streamlit Secrets for Supabase URL/Key.")
    st.stop()

# Persistent login check
if saved_email and not st.session_state.logged_in:
    st.session_state.logged_in = True
    st.session_state.user_email = saved_email

groq_client = Groq(api_key=GROQ_API_KEY)
hf_client = InferenceClient(token=HF_TOKEN)

# -----------------------
# 4. Custom UI Styling
# -----------------------
st.markdown("""
<style>  
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:20px; font-size: 22px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }  
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; height: 45px; font-weight: bold; border: 1px solid #FFD700; transition: 0.3s; }  
    div.stButton > button:hover { background-color: #FFD700; color: #000; }  
    .lab-box { border: 1px solid #333; padding: 20px; border-radius: 15px; background: #0e1117; margin-bottom: 20px; }  
</style>  """, unsafe_allow_html=True)

# -----------------------
# 5. Auth Functions
# -----------------------
def login_user(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user_email = res.user.email
        st.session_state.logged_in = True
        cookie_manager.set("alpha_persistent_login", res.user.email, expires_at=datetime.datetime.now() + datetime.timedelta(days=30))
        st.rerun()
    except: st.error("Login Failed. Please check credentials.")

def github_login_ui():
    try:
        res = supabase.auth.sign_in_with_oauth({"provider": "github"})
        # Custom button to prevent Iframe connection error
        st.markdown(f'<a href="{res.url}" target="_self"><button style="background-color: #24292e; color: white; padding: 12px; border-radius: 10px; width: 100%; cursor: pointer; border: none; font-weight: bold;">🚀 Login with GitHub</button></a>', unsafe_allow_html=True)
    except: st.error("GitHub Login Redirect Failed.")

# -----------------------
# 6. Auth UI
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="premium-banner">ALPHA CORE SYSTEM ACCESS</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        l_email = st.text_input("Operator Email")
        l_pass = st.text_input("Master Key", type="password")
        if st.button("Initialize Alpha"): login_user(l_email, l_pass)
        st.divider()
        github_login_ui()
    st.stop()

# -----------------------
# 7. Core Logic & Labs
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
            if results: return "\n".join([f"Source: {r['title']} - {r['body']}" for r in results])
    except: return ""
    return ""

def generate_video_robust(prompt):
    models = ["guoyww/AnimateDiff", "cerspense/zeroscope_v2_576w"]
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    for model_id in models:
        try:
            API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
            res = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=60)
            if res.status_code == 200: return res.content
        except: continue
    return None

# -----------------------
# 8. Main Dashboard
# -----------------------
with st.sidebar:
    st.title("Alpha Control")
    st.markdown(f"Operator: **{st.session_state.user_email}**")
    st.divider()
    # Models from your Groq dashboard
    mode = st.radio("Intelligence Engine", ["Normal (Llama 3.3 70B)", "Pro (GPT OSS 120B)"])
    web_on = st.checkbox("Web Search", value=False)
    voice_on = st.checkbox("Voice Feedback", value=True)
    if st.button("Log Out"):
        supabase.auth.sign_out()
        cookie_manager.delete("alpha_persistent_login")
        st.session_state.logged_in = False
        st.rerun()
    st.caption("Developed by Hasith Karunarathna")

st.markdown('<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

tab_img, tab_vid = st.tabs(["🖼 Image Lab", "🎬 Cinema Lab"])

with tab_img:
    with st.container():
        st.markdown('<div class="lab-box">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        img_p = col1.text_input("Describe image:", key="img_in")
        img_model = st.selectbox("Style Mode:", ["flux", "turbo", "zimage", "p-image"])
        if col2.button("Generate Photo"):
            if img_p:
                with st.spinner("Painting..."):
                    try:
                        encoded = urllib.parse.quote(img_p)
                        seed = random.randint(1, 1000000)
                        url = f"https://gen.pollinations.ai/image/{encoded}?width=1024&height=1024&seed={seed}&model={img_model}&nologo=true"
                        res = requests.get(url, timeout=60)
                        if res.status_code == 200:
                            st.image(res.content, caption=f"Alpha Gen {seed}", use_container_width=True)
                            st.download_button("Download 📥", res.content, f"alpha_{seed}.png", "image/png")
                    except Exception as e: st.error(f"Image Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

with tab_vid:
    with st.container():
        st.markdown('<div class="lab-box">', unsafe_allow_html=True)
        v_p = st.text_input("Describe video scene:", key="vid_in")
        if st.button("Direct Video"):
            if v_p:
                with st.spinner("Directing..."):
                    v_data = generate_video_robust(v_p)
                    if v_data:
                        st.video(v_data)
                        st.download_button("Download 📥", v_data, "alpha_vid.mp4")
                    else: st.error("Video core busy.")
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# 9. Persistent Conversation
# -----------------------
st.write("### 💬 Heartfelt Conversation")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

user_cmd = st.chat_input("State your command...")

if user_cmd:
    st.session_state.messages.append({"role": "user", "content": user_cmd})
    with st.chat_message("user"): st.markdown(user_cmd)
    
    with st.chat_message("assistant"):
        box = st.empty()
        full_res = ""
        context = web_search_tool(user_cmd) if web_on else ""
        sys_msg = f"You are Alpha AI, created by Hasith Karunarathna. Friendly, helpful. Context: {context}"
        
        # Model mapping based on your Groq availability
        target_model = "llama-3.3-70b-versatile" if "Normal" in mode else "openai/gpt-oss-120b"
        
        try:
            stream = groq_client.chat.completions.create(
                model=target_model,
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:],
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    box.markdown(full_res + "▌")
            box.markdown(full_res)
            
            if voice_on: asyncio.run(speak_alpha(full_res))
            st.session_state.messages.append({"role": "assistant", "content": full_res})
        except Exception as e: st.error(f"Engine Error: {e}")

st.markdown("---")
st.caption("Alpha AI Project | Created by Hasith Heshan Karunarathna")
