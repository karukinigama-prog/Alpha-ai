import streamlit as st
from groq import Groq
import time, base64, asyncio, requests, webbrowser
import edge_tts
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from streamlit_mic_recorder import mic_recorder
from email_validator import validate_email

# -----------------------
# 1. Page Configuration
# -----------------------
st.set_page_config(page_title="Alpha AI | Jarvis v3.3", page_icon="⚡", layout="wide")

# -----------------------
# 2. Advanced CSS UI
# -----------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Inter:wght@300;900&display=swap');
.stApp{background:#02050a;color:white;font-family:'Inter',sans-serif;}

/* REMOVE OVERLAYS */
iframe, .stDeployButton, [data-testid="stHeader"] { display: none !important; }
header {visibility: hidden !important;}

.alpha-title{font-size:5vw;text-align:center;font-weight:900;letter-spacing:0.5vw;text-shadow:0 0 25px #00d4ff; font-family:'Orbitron';}
.chat-box{background:rgba(0,212,255,0.05);padding:2vw;border-radius:2vw;border:1px solid rgba(0,212,255,0.2);margin:2vw 0;max-height:70vh;overflow-y:auto;}
.stButton>button{border-radius:1vw;background:rgba(0,212,255,0.08);border:1px solid rgba(0,212,255,0.2);color:white;font-size:1vw; width:100%;}
.stButton>button:hover{background:#00d4ff;color:black;box-shadow:0 0 15px #00d4ff;}
input[type=text], input[type=password]{border-radius:1vw;padding:0.8vw;width:100%; background:rgba(255,255,255,0.05); color:white; border:1px solid #00d4ff;}

.welcome-header {
    background: linear-gradient(90deg, #00d4ff, #0055ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: 'Orbitron', sans-serif;
    font-size: 2.8rem;
    font-weight: 900;
    text-align: center;
    margin-top: 20px;
}
.assist-text {
    color: #00d4ff;
    font-family: 'Inter', sans-serif;
    font-size: 1.2rem;
    text-align: center;
    letter-spacing: 2px;
    margin-bottom: 30px;
}

/* CYBER LOGIN INTERFACE */
.login-container {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    height: 85vh; background: radial-gradient(circle, #051937 0%, #000000 100%);
}
.login-card {
    background: rgba(0, 212, 255, 0.05); backdrop-filter: blur(25px);
    border: 1px solid rgba(0, 212, 255, 0.3); padding: 40px;
    border-radius: 20px; width: 100%; max-width: 550px;
    text-align: center; box-shadow: 0 0 50px rgba(0, 212, 255, 0.2);
}

.loader-container{display:flex;flex-direction:column;align-items:center;justify-content:center;height:90vh;background:#000;}
.loading-text{font-family:'Orbitron',sans-serif;color:#00d4ff;font-size:3vw;font-weight:900;letter-spacing:0.8vw;text-shadow:0 0 20px #00d4ff;margin-bottom:2vw;}
.progress-track{width:50vw;height:1vw;background:rgba(0,212,255,0.1);border-radius:1vw;overflow:hidden;}
.progress-fill{height:100%;background:#00d4ff;box-shadow:0 0 15px #00d4ff;transition:width 0.1s ease-out;}
</style>
""", unsafe_allow_html=True)

# -----------------------
# 3. Session State Init
# -----------------------
if "messages" not in st.session_state: st.session_state.messages=[]
if "memory" not in st.session_state: st.session_state.memory=[]
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "loaded" not in st.session_state: st.session_state.loaded=False
if "user_full_name" not in st.session_state: st.session_state.user_full_name=None

# -----------------------
# 4. Loading Screen
# -----------------------
if not st.session_state.loaded:
    l_ph=st.empty()
    for i in range(101):
        l_ph.markdown(f"""
        <div class='loader-container'>
            <div class='loading-text'>INITIALIZING ALPHA CORE...</div>
            <div class='progress-track'>
                <div class='progress-fill' style='width:{i}%;'></div>
            </div>
            <div style='color:#00d4ff;font-family:monospace;margin-top:1vw'>SYSTEM BOOT: {i}%</div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.03)
    st.session_state.loaded=True
    st.rerun()

# -----------------------
# 5. One-Time Login/Registration
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="alpha-title">ALPHA CORE</h1>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        u_full_name = st.text_input("Operator Name", placeholder="Your Name")
        u_email = st.text_input("Operator Email", placeholder="hasith@example.com")
        u_pass = st.text_input("Master Key", type="password", placeholder="••••••••")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("👑 REGISTER"):
                if u_full_name and u_email and u_pass:
                    try:
                        validate_email(u_email)
                        st.session_state.user_full_name = u_full_name
                        st.session_state.logged_in = True
                        st.rerun()
                    except: st.error("Invalid Email")
                else: st.warning("Fill all fields")
        with c2:
            if st.button("🛡️ LOGIN"):
                if u_pass == "Hasith12378":
                    st.session_state.user_full_name = u_full_name if u_full_name else "Hasith"
                    st.session_state.logged_in = True
                    st.rerun()
                elif u_email and u_pass and u_full_name:
                    st.session_state.user_full_name = u_full_name
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Access Denied")
        with c3:
            if st.button("🧪 BYPASS"):
                if u_pass == "Hasith12378":
                    st.session_state.user_full_name = u_full_name if u_full_name else "Creator"
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.warning("Key Required")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# -----------------------
# 6. Core Logic Functions
# -----------------------
async def speak_alpha(text):
    try:
        voice = "en-US-SteffanNeural"
        safe_text = text.encode("ascii", errors="ignore").decode()
        if not safe_text.strip(): return
        comm = edge_tts.Communicate(safe_text, voice)
        audio = b""
        async for chunk in comm.stream():
            if chunk["type"]=="audio": audio+=chunk["data"]
        if audio:
            b64 = base64.b64encode(audio).decode()
            st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}">', unsafe_allow_html=True)
    except: st.warning("TTS failed.")

def read_file(upload):
    if upload.name.endswith(".pdf"):
        reader = PdfReader(upload)
        text = "".join([p.extract_text() for p in reader.pages])
        return text[:4000]
    else: return upload.read().decode()

def internet_search(query):
    url=f"https://www.google.com/search?q={query}"
    headers={"User-Agent":"Mozilla/5.0"}
    r=requests.get(url, headers=headers)
    soup=BeautifulSoup(r.text,"html.parser")
    results=[g.text for g in soup.select("div.BNeawe")[:5]]
    return "\n".join(results)

def system_command(cmd):
    c=cmd.lower()
    if "youtube" in c: webbrowser.open("https://youtube.com"); return "Opening YouTube"
    if "maps" in c: webbrowser.open("https://maps.google.com"); return "Opening Maps"
    if "google" in c: webbrowser.open("https://google.com"); return "Opening Google"
    return None

client=Groq(api_key=st.secrets["GROQ_API_KEY"])
def ask_ai(prompt, mode):
    memory="\n".join(st.session_state.memory[-5:])
    model="llama-3.3-70b-versatile" if mode=="Llama 3.3 (Normal)" else "openai/gpt-oss-120b"
    messages=[{"role":"system","content":"You are Alpha AI created by Hasith."},
              {"role":"system","content":memory},
              {"role":"user","content":prompt}]
    res=client.chat.completions.create(model=model, messages=messages)
    return res.choices[0].message.content

# -----------------------
# 7. Sidebar (Full Original Options)
# -----------------------
with st.sidebar:
    st.markdown(f"<div style='text-align:center; border:1px solid #00d4ff; padding:15px; border-radius:15px; background:rgba(0,212,255,0.05);'><b>OPERATOR: {st.session_state.user_full_name}</b></div>", unsafe_allow_html=True)
    st.caption("System Architect")
    st.divider()
    
    # Intelligence Mode
    mode=st.radio("Intelligence Unit", ["Llama 3.3 (Normal)","GPT OSS 120B (Pro)"])
    st.divider()
    
    # AI Tools
    st.subheader("AI Tools")
    voice_mode=st.checkbox("🎤 Voice Chat")
    internet_mode=st.checkbox("🌐 Internet Search")
    memory_mode=st.checkbox("🧠 Memory")
    st.divider()
    
    # File Uploader
    uploaded=st.file_uploader("📂 Upload File")
    if uploaded:
        text=read_file(uploaded)
        st.session_state.memory.append(text)
        st.success("File loaded into memory")
    
    st.divider()
    if st.button("Clear Memory"): st.session_state.memory=[]
    if st.button("Log Out"): 
        st.session_state.logged_in=False
        st.rerun()

# -----------------------
# 8. Main Dashboard Greeting
# -----------------------
st.markdown(f"<div class='welcome-header'>WELCOME, {st.session_state.user_full_name.upper()}</div>", unsafe_allow_html=True)
st.markdown("<div class='assist-text'>HOW CAN WE ASSIST TODAY? SYSTEMS STANDING BY...</div>", unsafe_allow_html=True)

# -----------------------
# 9. Main Chat Interface
# -----------------------
st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])
st.markdown("</div>", unsafe_allow_html=True)

user_input=st.chat_input("State your command...")

if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"): st.markdown(user_input)
    with st.chat_message("assistant"):
        plugin=system_command(user_input)
        if plugin: answer=plugin
        else:
            prompt=f"{user_input}\n\nInternet Data:\n{internet_search(user_input)}" if internet_mode else user_input
            with st.spinner("Neural Processing..."): answer=ask_ai(prompt, mode)
        st.markdown(answer)
        if voice_mode: asyncio.run(speak_alpha(answer))
        st.session_state.messages.append({"role":"assistant","content":answer})
