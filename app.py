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
# 4. Custom UI Styling (Enhanced UX & Premium Gold)
# -----------------------
st.markdown("""
<style>  
    @viewport { width: device-width; zoom: 1.0; }
    .stApp { background: linear-gradient(135deg, #050505 0%, #001a1a 100%); color: #ffffff; }
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:20px; font-size: 20px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.2); }  
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; font-weight: bold; border: 2px solid #FFD700; transition: 0.3s; height: 3em; }  
    div.stButton > button:hover { background-color: #FFD700; color: #000; transform: translateY(-2px); box-shadow: 0px 5px 15px rgba(255,215,0,0.4); }  
    .status-card { padding: 10px; border-radius: 10px; background: rgba(255,215,0,0.1); border-left: 5px solid #FFD700; margin-bottom: 10px; font-family: monospace; font-size: 0.9em; }
    .ad-slot-premium { border: 1px dashed #FFD700; border-radius: 10px; padding: 10px; text-align: center; color: #FFD700; background: rgba(255,215,0,0.05); margin: 10px 0; font-size: 12px; text-transform: uppercase; }
    .lab-box { border: 1px solid #333; padding: 20px; border-radius: 15px; background: rgba(14, 17, 23, 0.8); margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }  
    .limit-box { padding:10px; border-radius:10px; background:#262730; border:1px solid #FFD700; text-align:center; margin-bottom:10px; font-weight:bold; }
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
# 7. Sidebar (Quick Actions & Ads)
# -----------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluent/100/000000/artificial-intelligence.png", width=60)
    st.title("Alpha Control")
    st.markdown('<div class="ad-slot-premium">Sponsor Ad<br>300 x 50 Banner</div>', unsafe_allow_html=True)
    
    can_gen_img, img_count, is_vip = check_user_access(st.session_state.user_full_name, "image")
    if is_vip: st.markdown('<div class="limit-box">💎 PREMIUM OPERATOR</div>', unsafe_allow_html=True)
    else: st.markdown(f'<div class="limit-box">🖼 Photos: {img_count}/5</div>', unsafe_allow_html=True)

    st.write("---")
    st.subheader("⚡ Quick Actions")
    q_actions = {
        "📘 FB Post Generator": "Create a creative Sinhala Facebook post about: ",
        "🎬 YouTube Script": "Write a YouTube video script for: ",
        "📚 Study Help": "Explain this subject simply in Sinhala: "
    }
    for label, prompt in q_actions.items():
        if st.button(label): st.session_state.quick_prompt = prompt

    st.write("---")
    voice_on = st.checkbox("Voice Response", value=True)
    ultra_mode = st.toggle("🚀 ULTRA MODE (Async Active)", value=True)
    
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown('<div class="ad-slot-premium">Alpha VIP Active</div>', unsafe_allow_html=True)

st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

# -----------------------
# 8. Tabs (The Functional Labs)
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
    st.subheader("🎬 Titan Video Engine (No-Linux Mode)")
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
    st.subheader("👁️ Alpha Vision Lab (Llama-3.2-90B)")
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
# 9. Hybrid Chat (Optimized Multi-Agent & UX)
# -----------------------
st.markdown('<div class="ad-slot-premium">📢 PROMOTED: Ella Cab and Tours - Contact Sumith 📢</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"], unsafe_allow_html=True)

current_input = st.chat_input("Command Alpha...")
final_q = current_input or st.session_state.quick_prompt
st.session_state.quick_prompt = None

async def run_multi_agent(query):
    dna_system_prompt = """
    [CORE IDENTITY: ALPHA AI ULTIMATE V2.6]
    - DEVELOPER: Hasith (Bandarawela Central College).
    - DNA PROTOCOL: Self-evolving logic.
    - TEAM: gpt-4o (Lead & Consolidator), o1 (Complex Reasoner).
    """
    
    # UI Phase 1: Initiation
    status_box = st.empty()
    status_box.markdown('<div class="status-card">⚡ SYSTEM: DNA Analysis Initiated...</div>', unsafe_allow_html=True)
    
    # Session State Fix: Move data to local variables before thread execution
    context_msgs = list(st.session_state.messages[-5:])
    
    loop = asyncio.get_event_loop()
    
    # Task 1: Lead Analysis (gpt-4o)
    task1 = loop.run_in_executor(None, lambda: openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role":"system","content": dna_system_prompt}] + context_msgs + [{"role":"user","content": query}]
    ))
    
    # Task 2: Deep Reasoning (o1)
    task2 = loop.run_in_executor(None, lambda: openai_client.chat.completions.create(
        model="o1",
        messages=[{"role":"user","content": f"Analyze and solve: {query}"}]
    ))
    
    status_box.markdown('<div class="status-card">🧬 AGENTS: gpt-4o & o1 Synchronizing in parallel...</div>', unsafe_allow_html=True)
    
    # Wait for both tasks (Efficiency Update)
    res1, res2 = await asyncio.gather(task1, task2)
    
    lead_out = res1.choices[0].message.content
    reason_out = res2.choices[0].message.content
    
    status_box.markdown('<div class="status-card">✨ UI: Finalizing Alpha Response...</div>', unsafe_allow_html=True)
    
    # Final Consolidation
    final_res = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role":"system","content": f"{dna_system_prompt}\nCombine inputs into a final creative Sinhala output. Include [LIVE_UI] if needed."},
                  {"role":"user","content": f"Lead: {lead_out}\nReasoner: {reason_out}\nOriginal Query: {query}"}]
    )
    
    status_box.empty()
    return final_res.choices[0].message.content

if final_q:
    st.session_state.messages.append({"role":"user","content":final_q})
    with st.chat_message("user"): st.markdown(final_q)
    
    with st.chat_message("assistant"):
        live_ui_placeholder = st.empty()
        full_ans = asyncio.run(run_multi_agent(final_q))
        
        st.markdown(full_ans, unsafe_allow_html=True)
        
        if "[LIVE_UI]" in full_ans:
            try:
                ui_content = full_ans.split("[LIVE_UI]")[1].split("[/LIVE_UI]")[0]
                live_ui_placeholder.markdown(ui_content, unsafe_allow_html=True)
            except: pass

        if voice_on: asyncio.run(speak_alpha(full_ans.replace("[LIVE_UI]", "").replace("[/LIVE_UI]", "")))
        st.session_state.messages.append({"role":"assistant","content":full_ans})

st.markdown('<div class="ad-slot-premium">Alpha AI v2.6 | DNA, Multi-Agent & Live UI Active</div>', unsafe_allow_html=True)
