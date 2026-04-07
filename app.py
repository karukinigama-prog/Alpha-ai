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
                    st.warning("⚠️ Copy and save this Key. You need it to login next time!")
                except: st.error("Registration failed. Email might already exist.")
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
# 5. Main UI Header & Sidebar
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
    
    st.divider()
    if st.button("Log Out"):
        cookie_manager.delete("alpha_master_token")
        st.session_state.logged_in = False
        st.rerun()

# -----------------------
# 6. Multimedia Labs
# -----------------------
tab_img, tab_vid = st.tabs(["🖼 Image Lab", "🎬 Cinema Lab"])

with tab_img:
    col1, col2 = st.columns([3, 1])
    img_p = col1.text_input("Describe your vision:", key="img_prompt", placeholder="A futuristic city in Sri Lanka")
    img_model = st.selectbox("Model:", ["flux", "turbo", "zimage", "p-image"])
    
    if col2.button("Generate"):
        if img_p:
            with st.spinner("Generating..."):
                seed = random.randint(1, 1000000)
                auth_param = f"&key={POLLINATIONS_KEY}" if POLLINATIONS_KEY else ""
                url = f"https://gen.pollinations.ai/image/{urllib.parse.quote(img_p)}?width=1024&height=1024&seed={seed}&model={img_model}&nologo=true&private=true{auth_param}"
                st.image(url, use_container_width=True)
        else:
            st.warning("Please describe your vision first!")

# -----------------------
# 7. Hybrid Chat System (Image Lab Connection Integrated)
# -----------------------
st.divider()
st.subheader("💬 Alpha Command Center")

# පවතින මැසේජ් පෙන්වීම
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image_url" in msg:
            st.image(msg["image_url"], use_container_width=True)

user_input = st.chat_input("State your command, Master...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)
    
    with st.chat_message("assistant"):
        res_placeholder = st.empty()
        search_results = web_search_tool(user_input) if web_search_on else ""
        
        # Groq එකට Image Prompt එකක් හදන්න උපදෙස් දීම
        sys_msg = (
            f"Your name is Alpha AI. Created by Hasith. "
            f"If the user asks for a photo/image/vision, you must provide a detailed English prompt "
            f"starting with 'GENERATE_IMAGE: [Your Prompt Here]'. "
            f"Then explain what you created in Sinhala. "
            f"Today's Date: {datetime.date.today()}. User: {user_info['full_name']}."
        )
        
        try:
            full_res = ""
            # --- AI Engine Selection ---
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
            else:
                stream = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:],
                    stream=True
                )
            
            if "Ultra" not in mode:
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        res_placeholder.markdown(full_res + "▌")

            # --- Image Lab Logic (Pollinations Connection) ---
            final_img_url = None
            if "GENERATE_IMAGE:" in full_res:
                try:
                    # Groq එක දුන්න Prompt එක වෙන් කර ගැනීම
                    parts = full_res.split("GENERATE_IMAGE:")
                    raw_prompt = parts[1].split("\n")[0].strip("[] ")
                    
                    # චැට් එකේ පෙන්වන Text එක පිරිසිදු කිරීම
                    display_text = parts[0] + "\n" + "\n".join(parts[1].split("\n")[1:])
                    
                    # Pollinations API එකට යැවීම (Image Lab එකේ logic එකමයි)
                    seed = random.randint(1, 999999)
                    encoded_p = urllib.parse.quote(raw_prompt)
                    # මෙතනදී අපි image lab එකේ වගේම උසස් තත්ත්වයේ රූපයක් ගන්නවා
                    final_img_url = f"https://gen.pollinations.ai/image/{encoded_p}?width=1024&height=1024&seed={seed}&nologo=true&model=flux"
                    
                    res_placeholder.markdown(display_text)
                    st.image(final_img_url, caption="Generated by Alpha AI Lab", use_container_width=True)
                    full_res = display_text # පෙන්වන text එක update කිරීම
                except Exception as img_err:
                    pass 
            else:
                res_placeholder.markdown(full_res)
                
            if voice_on: asyncio.run(speak_alpha(full_res))
            
            # Session එකට save කිරීම
            msg_save = {"role": "assistant", "content": full_res}
            if final_img_url: msg_save["image_url"] = final_img_url
            st.session_state.messages.append(msg_save)
            
        except Exception as e: 
            st.error(f"Alpha Core Error: {e}")

st.divider()
st.caption("Alpha AI Ultimate Edition | Powering the Future | Created by Hasith")
