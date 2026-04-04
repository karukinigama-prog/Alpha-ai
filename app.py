import streamlit as st
from supabase import create_client, Client
import extra_streamlit_components as stx
from huggingface_hub import InferenceClient
from groq import Groq
import requests, base64, asyncio, io, json, datetime
import edge_tts
import random, urllib.parse, time
from duckduckgo_search import DDGS

# -----------------------
# 1. Supabase & API Setup
# -----------------------
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)
hf_client = InferenceClient(token=HF_TOKEN)

st.set_page_config(page_title="Alpha AI | Pro Business Edition", layout="wide", page_icon="⚡")

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
    st.markdown('<h1 style="text-align:center; color:#FFD700;">⚡ ALPHA AI CORE ACCESS</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#888;">Created by Hasith | Bandarawela Central College</p>', unsafe_allow_html=True)
    
    auth_tab1, auth_tab2 = st.tabs(["🔑 Sign In", "📝 Create Account"])

    with auth_tab2: 
        st.subheader("Register for Alpha AI")
        reg_name = st.text_input("Full Name", placeholder="Enter your name")
        reg_email = st.text_input("Email Address", placeholder="Enter your email")
        if st.button("Register & Get Master Key"):
            if reg_name and reg_email:
                new_key = generate_master_key()
                try:
                    data = {"full_name": reg_name, "email": reg_email, "master_key": new_key}
                    supabase.table("profiles").insert(data).execute()
                    st.success(f"Registration Successful! Welcome {reg_name}.")
                    st.code(f"YOUR MASTER KEY: {new_key}", language="text")
                except: st.error("Registration failed.")
            else: st.info("Please fill all details.")

    with auth_tab1: 
        st.subheader("Login with Master Key")
        log_email = st.text_input("Email", key="login_email")
        log_key = st.text_input("Master Key", type="password", key="login_key")
        if st.button("Access Alpha System"):
            res = supabase.table("profiles").select("*").eq("email", log_email).eq("master_key", log_key).execute()
            if res.data:
                st.session_state.user_data = res.data[0]
                st.session_state.logged_in = True
                cookie_manager.set("alpha_master_token", log_key, expires_at=datetime.datetime.now() + datetime.timedelta(days=30))
                st.rerun()
            else: st.error("Invalid Email or Master Key.")
    st.stop()

# -----------------------
# 5. Main UI & Sidebar
# -----------------------
user_info = st.session_state.user_data
status_label = "🌟 PRO" if user_info.get("is_pro") else "🆓 FREE"

st.markdown(f"""
<div style="background: linear-gradient(90deg, #FFD700, #FF8C00); padding:15px; border-radius:15px; text-align:center; color:black; font-weight:bold; margin-bottom:20px;">
    ⚡ ALPHA AI ULTIMATE | User: {user_info['full_name']} | Status: {status_label}
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/fluent/100/000000/artificial-intelligence.png", width=70)
    st.title("Alpha Settings")
    mode = st.radio("Intelligence Level", ["Normal (Llama 3.3)", "Pro (GPT OSS 120B)", "Ultra (DeepSeek)"])
    web_search_on = st.checkbox("Live Web Search", value=False)
    voice_on = st.checkbox("Voice Output", value=True)
    if st.button("Log Out"):
        cookie_manager.delete("alpha_master_token")
        st.session_state.logged_in = False
        st.rerun()

# -----------------------
# 6. Multimedia Labs (Images, Cinema & Music)
# -----------------------
tab_img, tab_vid, tab_mus = st.tabs(["🖼 Image Lab", "🎬 Cinema Lab", "🎵 Music Lab"])

with tab_img:
    col1, col2 = st.columns([3, 1])
    img_p = col1.text_input("Describe your vision:", key="img_prompt")
    img_model = st.selectbox("Model:", ["flux", "turbo", "zimage", "p-image"])
    if col2.button("Generate"):
        if img_p:
            with st.spinner("Generating..."):
                seed = random.randint(1, 1000000)
                url = f"https://gen.pollinations.ai/image/{urllib.parse.quote(img_p)}?width=1024&height=1024&seed={seed}&model={img_model}&nologo=true"
                st.image(url, use_container_width=True)

# --- මෙන්න හසීත් ඉල්ලපු Music Lab එක ---
with tab_mus:
    st.subheader("🎤 Alpha AI Music Studio")
    m_lyrics = st.text_area("සින්දුවේ පද (Lyrics):", "Yo, Alpha AI is here,\nHasith has no fear.")
    
    m_styles = {
        "🎧 Hip-Hop / Rap": "en_male_m03_lobby",
        "🎸 Rock Style": "en_male_m03_sunshine",
        "✨ Pop Style": "en_female_f08_twinkle",
        "🎙️ Deep Voice": "en_male_narration"
    }
    m_style = st.selectbox("Style:", list(m_styles.keys()))
    
    if st.button("Generate Full Music 🎼"):
        if m_lyrics:
            lines = [l.strip() for l in m_lyrics.split('\n') if l.strip()]
            combined_audio = io.BytesIO()
            with st.spinner("Music එක හදනවා..."):
                for line in lines:
                    try:
                        time.sleep(1) # සර්වර් එක ආරක්ෂා කිරීමට
                        u = "https://tiktok-tts.weilnet.workers.dev/api/generation"
                        p = {"text": line, "voice": m_styles[m_style]}
                        r = requests.post(u, json=p).json()
                        if "data" in r:
                            combined_audio.write(base64.b64decode(r["data"]))
                    except: continue
                
                combined_audio.seek(0)
                audio_data = combined_audio.read()
                if audio_data:
                    st.audio(audio_data, format='audio/mp3')
                    st.download_button("Download Full MP3 📥", audio_data, "Alpha_Song.mp3", "audio/mp3")

# -----------------------
# 7. Hybrid Chat System (කලින් තිබුණ විදිහටම)
# -----------------------
# ... (ඔයාගේ ඉතිරි chat කෝඩ් එක මෙතනට දාන්න) ...
