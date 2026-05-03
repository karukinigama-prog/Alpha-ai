import streamlit as st
import requests
import io
from PIL import Image
import random
import time
import base64
import asyncio
import json
import string
import datetime
import urllib.parse
from huggingface_hub import InferenceClient
from openai import OpenAI
from groq import Groq
import edge_tts
from gtts import gTTS
from duckduckgo_search import DDGS 
from supabase import create_client, Client
from streamlit_agraph import agraph, Node, Edge, Config

# -----------------------
# 1. Page Config & Identity
# -----------------------
st.set_page_config(page_title="Alpha AI | Created by Hasith", layout="wide", page_icon="⚡")

# -----------------------
# 2. API & Database Setup
# -----------------------
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    st.error("Supabase credentials missing.")
    st.stop()

if GITHUB_TOKEN:
    openai_client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=GITHUB_TOKEN,
    )
else:
    st.error("GITHUB_TOKEN missing in secrets.")
    st.stop()

hf_client = InferenceClient(token=HF_TOKEN)

# -----------------------
# 3. Session State Init
# -----------------------
if "messages" not in st.session_state: st.session_state.messages=[]
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "user_full_name" not in st.session_state: st.session_state.user_full_name=None
if "generated_image" not in st.session_state: st.session_state.generated_image = None
if "quick_prompt" not in st.session_state: st.session_state.quick_prompt = None
if 'history' not in st.session_state: st.session_state.history = []

# -----------------------
# 4. Custom UI Styling
# -----------------------
st.markdown("""
<style>  
    @viewport { width: device-width; zoom: 1.0; }
    .stApp { background: linear-gradient(135deg, #050505 0%, #001a1a 100%); color: #ffffff; }
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:20px; font-size: 20px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.2); }  
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; font-weight: bold; border: 2px solid #FFD700; transition: 0.3s; height: 3em; }  
    div.stButton > button:hover { background-color: #FFD700; color: #000; transform: translateY(-2px); box-shadow: 0px 5px 15px rgba(255,215,0,0.4); }  
    .status-card { padding: 10px; border-radius: 10px; background: rgba(255,215,0,0.05); border-left: 5px solid #FFD700; margin-bottom: 10px; color: #FFD700; }
    .lab-box { border: 1px solid #333; padding: 20px; border-radius: 15px; background: rgba(14, 17, 23, 0.8); margin-bottom: 20px; }  
</style>  """, unsafe_allow_html=True)

# -----------------------
# 5. Helper Functions
# -----------------------
def check_user_access(username, req_type="image"):
    today = str(datetime.date.today())
    limit = 5 if req_type == "image" else 6
    try:
        res = supabase.table("user_usage").select("*").eq("username", username).execute()
        if not res.data:
            supabase.table("user_usage").insert({"username": username, "last_date": today, "image_count": 0, "voice_count": 0, "is_premium": False}).execute()
            return True, 0, False
        user = res.data[0]
        if user.get('is_premium', False): return True, 0, True
        if user['last_date'] != today:
            supabase.table("user_usage").update({"last_date": today, "image_count": 0, "voice_count": 0}).eq("username", username).execute()
            return True, 0, False
        count = user.get('image_count', 0) if req_type == "image" else user.get('voice_count', 0)
        return (count < limit), count, False
    except: return True, 0, False

def update_usage(username, current_count, req_type="image"):
    field = "image_count" if req_type == "image" else "voice_count"
    supabase.table("user_usage").update({field: current_count + 1}).eq("username", username).execute()

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

def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

# -----------------------
# 6. Login System
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="premium-banner">ALPHA CORE SYSTEM ACCESS</div>', unsafe_allow_html=True)
    name = st.text_input("Operator Name")
    key = st.text_input("Master Key", type="password")
    if st.button("Initialize Alpha"):
        if key == "Hasith12378":
            st.session_state.user_full_name = name or "Hasith"
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# -----------------------
# 7. Sidebar
# -----------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluent/100/000000/artificial-intelligence.png", width=60)
    st.title("Alpha Control")
    voice_on = st.checkbox("Voice Response", value=True)
    testing_mode = st.toggle("🧪 TESTING MODE (Llama 405B)", value=False)
    
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

# -----------------------
# 8. Tabs
# -----------------------
tab_img, tab_vid, tab_voice, tab_vision, tab_map = st.tabs(["🖼 Image", "🎬 Cinema", "🎙️ Voice", "👁️ Vision", "🧠 Map"])

with tab_img:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    st.subheader("🔱 Titan-Gate Image Engine")
    img_p = st.text_input("Describe Vision (English):")
    if st.button("RENDER MASTERPIECE 🚀", key="img_btn"):
        if img_p:
            can, count, vip = check_user_access(st.session_state.user_full_name, "image")
            if can:
                url = f"https://image.pollinations.ai/prompt/{img_p.replace(' ','%20')}?width=1024&height=1024&seed={random.randint(1,999)}&nologo=true"
                st.session_state.history.insert(0, url)
                if not vip: update_usage(st.session_state.user_full_name, count, "image")
                st.image(url, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab_vid:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    st.subheader("🎬 Titan Video Engine")
    vid_p = st.text_input("Describe video scene:", key="vid_p_titan")
    if st.button("Generate Video 🎥", key="vid_btn"):
        if vid_p:
            with st.spinner("Alpha is rendering..."):
                v_url = f"https://pollinations.ai/p/{vid_p.replace(' ','%20')}?width=512&height=512&model=video"
                v_html = f'<video width="100%" controls autoplay loop><source src="{v_url}" type="video/mp4"></video>'
                st.markdown(v_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab_voice:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    st.subheader("🎙️ Alpha Voice Studio")
    v_txt = st.text_area("කථා කිරීමට අවශ්‍ය දේ ලියන්න:")
    if st.button("Speak Now 🔊", key="voice_btn"):
        can_v, v_c, vip_v = check_user_access(st.session_state.user_full_name, "voice")
        if can_v:
            st.audio(io.BytesIO(gTTS(text=v_txt, lang='si')._write_to_fp()).getvalue())
            if not vip_v: update_usage(st.session_state.user_full_name, v_c, "voice")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_vision:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    st.subheader("👁️ Alpha Vision Lab")
    v_file = st.file_uploader("Upload Image:", type=["jpg","png","jpeg"])
    if v_file:
        v_bytes = v_file.read()
        st.image(v_bytes, use_container_width=True)
        v_query = st.text_input("Ask Alpha about this:")
        if st.button("Analyze Image 🧠", key="vision_btn"):
            res = openai_client.chat.completions.create(
                model="Llama-3.2-90B-Vision-Instruct",
                messages=[{"role":"user","content":[{"type":"text","text":v_query or "Describe this."},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{encode_image(v_bytes)}"}}]}]
            )
            st.info(res.choices[0].message.content)
    st.markdown('</div>', unsafe_allow_html=True)

with tab_map:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    agraph(nodes=[Node(id="Alpha", label="Alpha AI", color="#FFD700"), Node(id="Hasith", label="Creator")], edges=[Edge(source="Hasith", target="Alpha")], config=Config(width=600, height=400))
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# 9. Chat Engine (Optimized)
# -----------------------
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"], unsafe_allow_html=True)

current_input = st.chat_input("Command Alpha...")

def run_alpha_core(query, is_testing):
    dna_system_prompt = f"""
    [CORE IDENTITY: ALPHA AI ULTIMATE V2.7]
    - DEVELOPER: Hasith Karunarathna.
    - PERSONALITY: Philosophical and Professional.
    - INSTRUCTIONS: Speak in elegant Sinhala.
    """
    
    # Testing Mode එක අනුව Model එක තෝරා ගැනීම
    selected_model = "Llama-3.1-405B-Instruct" if is_testing else "gpt-4o"
    
    status_box = st.empty()
    status_box.markdown(f'<div class="status-card">⚡ Alpha Intelligence ({selected_model}) Syncing...</div>', unsafe_allow_html=True)
    
    try:
        response = openai_client.chat.completions.create(
            model=selected_model,
            messages=[{"role":"system","content": dna_system_prompt}] + st.session_state.messages[-6:] + [{"role":"user","content": query}]
        )
        full_ans = response.choices[0].message.content
    except Exception as e:
        full_ans = "සන්නිවේදන දෝෂයක් පවතී. කරුණාකර මොහොතකින් උත්සාහ කරන්න."
    
    status_box.empty()
    return full_ans

if current_input:
    st.session_state.messages.append({"role":"user","content":current_input})
    with st.chat_message("user"): st.markdown(current_input)
    
    with st.chat_message("assistant"):
        full_ans = run_alpha_core(current_input, testing_mode)
        st.markdown(full_ans, unsafe_allow_html=True)
        if voice_on: asyncio.run(speak_alpha(full_ans))
        st.session_state.messages.append({"role":"assistant","content":full_ans})

st.markdown('<div class="ad-slot-premium">Alpha AI v2.7 | Testing Lab Enabled</div>', unsafe_allow_html=True)
