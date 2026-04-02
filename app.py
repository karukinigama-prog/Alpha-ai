import streamlit as st
from supabase import create_client, Client
import extra_streamlit_components as stx
from huggingface_hub import InferenceClient
from groq import Groq
import requests, base64, asyncio, io, json, datetime
import edge_tts
import random, urllib.parse
from duckduckgo_search import DDGS

# -----------------------
# 1. Supabase & API Setup
# -----------------------
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")
POLLINATIONS_KEY = st.secrets.get("POLLINATIONS_API_KEY")
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)
hf_client = InferenceClient(token=HF_TOKEN)

st.set_page_config(page_title="Alpha AI | Pro Business Edition", layout="wide", page_icon="⚡")

# -----------------------
# PREMIUM UI STYLING (The "Penumi" Update)
# -----------------------
st.markdown("""
<style>
    /* Main Background & Text */
    .stApp { background-color: #050505; color: #E0E0E0; }
    
    /* Premium Banner */
    .premium-header {
        background: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #FBF5B7, #AA771C);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: #1a1a1a;
        font-weight: 900;
        font-size: 24px;
        letter-spacing: 2px;
        box-shadow: 0px 4px 20px rgba(191, 149, 63, 0.4);
        margin-bottom: 25px;
        border: 1px solid rgba(255, 215, 0, 0.3);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        background-color: #111;
        border: 1px solid #333;
        color: #888;
        border-radius: 10px 10px 0px 0px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(180deg, #BF953F, #AA771C) !important;
        color: black !important;
        font-weight: bold;
    }

    /* Buttons */
    div.stButton > button {
        background: linear-gradient(90deg, #1a1a1a, #333);
        color: #FFD700;
        border: 1px solid #FFD700;
        border-radius: 8px;
        transition: 0.3s all ease;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background: #FFD700;
        color: black;
        box-shadow: 0px 0px 15px #FFD700;
    }

    /* Input Fields */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #121212 !important;
        color: white !important;
        border: 1px solid #333 !important;
    }
    
    /* Chat Message Bubbles */
    .stChatMessage { border-radius: 15px; border: 1px solid #222; background-color: #0d0d0d !important; }
</style>
""", unsafe_allow_html=True)

# -----------------------
# 2. Cookie & Session Management
# -----------------------
cookie_manager = stx.CookieManager()
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = None
if "messages" not in st.session_state: st.session_state.messages = []

saved_token = cookie_manager.get(cookie="alpha_master_token")
if saved_token and not st.session_state.logged_in:
    try:
        res = supabase.table("profiles").select("*").eq("master_key", saved_token).execute()
        if res.data:
            st.session_state.user_data = res.data[0]
            st.session_state.logged_in = True
    except: pass

# -----------------------
# 3. Helper Functions
# -----------------------
def generate_master_key():
    return f"ALPHA-{random.randint(1000, 9999)}-{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"

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
                return "\n".join([f"Source: {r['title']} - {r['body']}" for r in results])
    except: return ""
    return ""

# -----------------------
# 4. Master Key Auth UI
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="premium-header">⚡ ALPHA AI CORE ACCESS</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#888; font-style:italic;">Developed by Hasith | Bandarawela Central College</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
        
        with auth_tab2:
            st.subheader("Create Operator Profile")
            reg_name = st.text_input("Operator Name")
            reg_email = st.text_input("Terminal Email")
            if st.button("Generate Master Key"):
                if reg_name and reg_email:
                    new_key = generate_master_key()
                    try:
                        data = {"full_name": reg_name, "email": reg_email, "master_key": new_key}
                        supabase.table("profiles").insert(data).execute()
                        st.success("Access Granted.")
                        st.code(f"KEY: {new_key}")
                    except: st.error("Email terminal already registered.")

        with auth_tab1:
            st.subheader("Unlock Terminal")
            log_email = st.text_input("Email", key="login_email")
            log_key = st.text_input("Master Key", type="password", key="login_key")
            if st.button("Initialize"):
                res = supabase.table("profiles").select("*").eq("email", log_email).eq("master_key", log_key).execute()
                if res.data:
                    st.session_state.user_data = res.data[0]
                    st.session_state.logged_in = True
                    cookie_manager.set("alpha_master_token", log_key, expires_at=datetime.datetime.now() + datetime.timedelta(days=30))
                    st.rerun()
                else: st.error("Access Denied.")
    st.stop()

# -----------------------
# 5. Main UI & Sidebar
# -----------------------
user_info = st.session_state.user_data
status_label = "🌟 PRO OPERATOR" if user_info.get("is_pro") else "🆓 FREE OPERATOR"

st.markdown(f'<div class="premium-header">⚡ {user_info["full_name"]} | {status_label}</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<h2 style="color:#FFD700;">COMMAND CENTER</h2>', unsafe_allow_html=True)
    mode = st.radio("Intelligence Engine", ["Normal (Llama 3.3)", "Pro (GPT OSS 120B)", "Ultra (DeepSeek)"])
    st.divider()
    web_search_on = st.checkbox("Live Matrix Search", value=False)
    voice_on = st.checkbox("Audio Uplink", value=True)
    if st.button("Terminate Session"):
        cookie_manager.delete("alpha_master_token")
        st.session_state.logged_in = False
        st.rerun()
    st.caption("Alpha AI Ultimate Edition | Created by Hasith")

# -----------------------
# 6. Multimedia Labs
# -----------------------
tab_img, tab_vid = st.tabs(["🖼 IMAGE LAB", "🎬 CINEMA LAB"])

with tab_img:
    col1, col2 = st.columns([3, 1])
    img_p = col1.text_input("Neural Prompt:", key="img_prompt", placeholder="Describe your vision...")
    img_model = col2.selectbox("Engine:", ["flux", "turbo", "zimage", "p-image"])
    if st.button("Paint Vision"):
        if img_p:
            with st.spinner("Processing Neural Pathways..."):
                seed = random.randint(1, 1000000)
                url = f"https://gen.pollinations.ai/image/{urllib.parse.quote(img_p)}?width=1024&height=1024&seed={seed}&model={img_model}&nologo=true"
                st.image(url, caption=f"Alpha Gen ID: {seed}", use_container_width=True)

# -----------------------
# 7. Hybrid Chat System
# -----------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

user_input = st.chat_input("Enter command for Alpha AI...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)
    
    with st.chat_message("assistant"):
        res_placeholder = st.empty()
        search_results = web_search_tool(user_input) if web_search_on else ""
        sys_msg = (
            f"Your name is Alpha AI. Created by Hasith from Bandarawela Central College. "
            f"User: {user_info['full_name']}. Search context: {search_results}"
        )
        
        try:
            if "Pro" in mode:
                stream = groq_client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:],
                    temperature=0.7, stream=True
                )
            elif "Ultra" in mode:
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                    data=json.dumps({
                        "model": "deepseek/deepseek-chat",
                        "messages": [{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:]
                    })
                )
                full_res = response.json()['choices'][0]['message']['content']
                res_placeholder.markdown(full_res)
            else:
                stream = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:],
                    stream=True
                )
            
            if "Ultra" not in mode:
                full_res = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        res_placeholder.markdown(full_res + "▌")
                res_placeholder.markdown(full_res)
                
            if voice_on: asyncio.run(speak_alpha(full_res))
            st.session_state.messages.append({"role": "assistant", "content": full_res})
        except Exception as e: st.error(f"Engine Fault: {e}")

st.divider()
st.caption("Alpha AI Ultimate Edition | Powering the Future | Created by Hasith")
