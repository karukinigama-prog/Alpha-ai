import streamlit as st
from huggingface_hub import InferenceClient
from groq import Groq
from supabase import create_client, Client
import extra_streamlit_components as stx
import requests, base64, asyncio, io, json, datetime
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
# 2. Session State & Cookie Management
# -----------------------
if "messages" not in st.session_state: st.session_state.messages = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = None

cookie_manager = stx.CookieManager()
saved_email = cookie_manager.get(cookie="alpha_session_email")

# -----------------------
# 3. API & Database Setup
# -----------------------
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")
POLLINATIONS_KEY = st.secrets.get("POLLINATIONS_API_KEY", "sk_Z0oEnm05szbphnbZ9ClRCukKV2HyDMH5")
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    st.error("Supabase Credentials Missing!")
    st.stop()

# Auto-login check
if saved_email and not st.session_state.logged_in:
    st.session_state.logged_in = True
    st.session_state.user_data = {"email": saved_email}

groq_client = Groq(api_key=GROQ_API_KEY)
hf_client = InferenceClient(token=HF_TOKEN)

# -----------------------
# 4. Custom UI Styling
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
# 5. Auth Logic (GitHub & Email)
# -----------------------
def login_user(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user_data = {"email": res.user.email, "name": res.user.user_metadata.get("full_name", "User")}
        st.session_state.logged_in = True
        cookie_manager.set("alpha_session_email", res.user.email, expires_at=datetime.datetime.now() + datetime.timedelta(days=30))
        st.rerun()
    except: st.error("Access Denied: Invalid Credentials")

def signup_user(email, password, name):
    try:
        supabase.auth.sign_up({"email": email, "password": password, "options": {"data": {"full_name": name}}})
        st.success("Identity Created! If email confirmation is ON, check your inbox. If OFF, you can login now.")
    except Exception as e: st.error(f"Signup Error: {e}")

def github_login_ui():
    try:
        res = supabase.auth.sign_in_with_oauth({"provider": "github"})
        st.markdown(f'<a href="{res.url}" target="_self"><button style="background-color: #24292e; color: white; padding: 12px; border-radius: 10px; width: 100%; cursor: pointer; border: none; font-weight: bold;">🚀 Login with GitHub</button></a>', unsafe_allow_html=True)
    except: st.error("GitHub Connection Failed.")

# -----------------------
# 6. Login System UI
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="premium-banner">ALPHA CORE SYSTEM ACCESS</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#FFD700; font-weight:bold;">Developed by Hasith Karunarathna</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_l, tab_r = st.tabs(["🔐 Master Login", "📝 Create Identity"])
        with tab_l:
            l_email = st.text_input("Operator Email")
            l_pass = st.text_input("Master Key", type="password")
            if st.button("Initialize Alpha"): login_user(l_email, l_pass)
            st.divider()
            github_login_ui()
        with tab_r:
            r_name = st.text_input("Full Name")
            r_email = st.text_input("Official Email")
            r_pass = st.text_input("Create Password", type="password")
            if st.button("Register with Alpha"): signup_user(r_email, r_pass, r_name)
    st.stop()

# -----------------------
# 7. Helper Functions
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
# 8. Sidebar Control
# -----------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluent/100/000000/artificial-intelligence.png", width=70)
    st.title("Alpha Control")
    st.markdown(f"Operator: **{st.session_state.user_data.get('email')}**")
    st.divider()
    mode = st.radio("Intelligence Level", ["Normal (Llama 3.3 70B)", "Pro (Llama 3.1 70B)", "Ultra (DeepSeek 671B)"])
    web_search_on = st.checkbox("Web Search (Real-time)", value=False)
    voice_on = st.checkbox("Voice Output", value=True)
    st.divider()
    if st.button("Log Out"):
        supabase.auth.sign_out()
        cookie_manager.delete("alpha_session_email")
        st.session_state.logged_in = False
        st.rerun()
    st.write("---")
    st.caption("Created by Hasith | Bandarawela Central College")

st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

# -----------------------
# 9. AI Multimodal Labs
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
                            st.image(response.content, caption=f"Created for Operator", use_container_width=True)  
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
# 10. Hybrid Intelligence Chat
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
                f"Your name is Alpha AI. You are a highly advanced AI assistant "
                f"developed by Hasith Heshan Karunarathna from Sri Lanka. Hasith is a student "
                f"at Bandarawela Central College. Be friendly and helpful. "
                f"Search context: {search_context}"
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
                        st.error("DeepSeek API Error. Check your OpenRouter Key.")
                        full_res = "Master, I'm having trouble connecting to my Ultra core."
                else:
                    if "Normal" in mode:
                        selected_model = "llama-3.3-70b-versatile"
                    else:
                        selected_model = "llama-3.1-70b-versatile"
                    
                    stream = groq_client.chat.completions.create(
                        model=selected_model,
                        messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:],
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
