import streamlit as st
from groq import Groq
import time
from gtts import gTTS
import os

# --- 1. Page Setup ---
st.set_page_config(page_title="Alpha AI ⚡ Hasith's Empire", page_icon="⚡", layout="wide")

# --- 2. ⚙️ Mechanical Imperial Loading Screen (7 Seconds) ---
if "loaded" not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
            <style>
                .main-loader { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 90vh; background: #050505; }
                .hex-container { position: relative; width: 150px; height: 150px; animation: rotate 4s linear infinite; }
                .alpha-title { font-size: 70px; font-weight: 900; color: #FFD700; text-shadow: 0 0 40px #FF8C00; font-family: 'Orbitron', sans-serif; margin-bottom: 10px; letter-spacing: 10px; animation: pulse 2s infinite; }
                .loading-bar-container { width: 450px; height: 4px; background: rgba(255, 215, 0, 0.1); border-radius: 20px; overflow: hidden; margin-top: 30px; border: 1px solid rgba(255, 215, 0, 0.3); }
                .loading-progress { width: 100%; height: 100%; background: linear-gradient(90deg, #FFD700, #FF8C00); animation: progress-fill 7s linear forwards; }
                .status-text { color: #888; font-family: monospace; margin-top: 15px; letter-spacing: 3px; font-size: 12px; }
                @keyframes progress-fill { 0% { width: 0; } 100% { width: 100%; } }
                @keyframes pulse { 0% { opacity: 0.6; transform: scale(1); } 50% { opacity: 1; transform: scale(1.05); } 100% { opacity: 0.6; transform: scale(1); } }
                @keyframes rotate { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            </style>
            <div class="main-loader">
                <div class="alpha-title">ALPHA</div>
                <div class="loading-bar-container"><div class="loading-progress"></div></div>
                <div class="status-text">SYSTEM INITIALIZING: MECHANICAL CORE LOADED</div>
                <p style="color: #FFD700; margin-top: 40px; font-size: 14px; opacity: 0.7;">BY HASITH HESHAN</p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(7)
    st.session_state.loaded = True
    st.rerun()

# --- 3. Real-Time Data Store (NO FAKE DATA) ---
if "user_db" not in st.session_state: st.session_state.user_db = {}
if "active_logs" not in st.session_state: st.session_state.active_logs = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_user" not in st.session_state: st.session_state.current_user = None
if "messages" not in st.session_state: st.session_state.messages = []

# --- 4. Imperial Theme Styling ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: white; }
    .login-box { background: #0a0a0a; border: 2px solid #FFD700; padding: 50px; border-radius: 25px; box-shadow: 0 0 60px rgba(255, 215, 0, 0.15); text-align: center; }
    div.stButton > button { background: linear-gradient(135deg, #FFD700 0%, #FF8C00 100%); color: black !important; font-weight: 800; border-radius: 12px; height: 50px; border: none; width: 100%; transition: 0.4s; }
    div.stButton > button:hover { box-shadow: 0 0 25px #FFD700; transform: translateY(-2px); }
    .admin-card { background: #111; border-left: 4px solid #FFD700; padding: 20px; border-radius: 12px; margin-bottom: 20px; }
    .stSelectbox div[data-baseweb="select"] { background-color: #111; border: 1px solid #FFD700; color: white; }
</style>
""", unsafe_allow_html=True)

# --- 5. Security Portal ---
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('<div class="login-box"><h1 style="color:#FFD700; letter-spacing:10px;">ALPHA</h1><p style="color:#666;">AUTHORIZE IDENTITY</p></div>', unsafe_allow_html=True)
        t1, t2 = st.tabs(["🔐 SIGN IN", "📝 REGISTER"])
        with t1:
            u = st.text_input("Access ID").lower().strip()
            p = st.text_input("Passcode", type="password")
            if st.button("AUTHORIZE"):
                if (u == "hasith123" and p == "hasith@alpha") or (u in st.session_state.user_db and st.session_state.user_db[u]["password"] == p):
                    st.session_state.logged_in = True; st.session_state.current_user = u
                    st.session_state.active_logs.append(f"{u.upper()} - {time.strftime('%H:%M:%S')}")
                    st.rerun()
                else: st.error("INVALID ACCESS SIGNAL")
        with t2:
            nu = st.text_input("New Identity")
            np = st.text_input("New Passcode", type="password")
            if st.button("SYNC IDENTITY"):
                if nu and np:
                    st.session_state.user_db[nu.lower()] = {"password": np, "activity": 0}
                    st.success("Identity Synced to System!")
    st.stop()

# --- 6. Sidebar Command Center ---
with st.sidebar:
    st.markdown('<h2 style="color:#FFD700; text-align:center;">COMMAND CENTER</h2>', unsafe_allow_html=True)
    
    # 👑 HASITH'S ADMIN PANEL (ONLY REAL DATA)
    if st.session_state.current_user == "hasith123":
        st.markdown('<div class="admin-card">', unsafe_allow_html=True)
        st.subheader("👑 SYSTEM SUPREME")
        st.metric("Total Real Users", len(st.session_state.user_db))
        st.write("📊 **Neural Activity**")
        if not st.session_state.user_db: st.caption("No users yet.")
        else:
            for user, data in st.session_state.user_db.items():
                st.caption(f"{user.capitalize()}")
                st.progress(min(100, data.get("activity", 0)) / 100)
        st.write("📱 **Live Device Logs**")
        for log in st.session_state.active_logs[-10:]: st.caption(f"✔ {log}")
        st.markdown('</div>', unsafe_allow_html=True)

    # 🧠 MULTI-ENGINE SELECTION BAR
    st.markdown('<div style="border: 1px solid #FFD700; padding:15px; border-radius:15px;">', unsafe_allow_html=True)
    st.subheader("🧠 Intelligence Engine")
    model_choice = st.selectbox(
        "Select Neural Core:",
        [
            "Normal (Llama 3.3 70B)", 
            "Pro Mode (GPT-OSS 120B)", 
            "Logic Pro (Gemma 2)", 
            "Turbo Speed (Llama 3.1)",
            "Data Specialist (Mixtral)"
        ]
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("TERMINATE SESSION"):
        st.session_state.logged_in = False
        st.rerun()

# --- 7. Main Dashboard ---
st.markdown('<div style="background: linear-gradient(90deg, #FFD700, #FF8C00); padding: 15px; border-radius: 15px; color: black; text-align: center; font-weight: 900; font-size: 20px; letter-spacing: 5px;">ALPHA AI COMMAND HUB</div>', unsafe_allow_html=True)

# Admin Analytics Chart
if st.session_state.current_user == "hasith123" and st.session_state.user_db:
    st.write("### 📈 Neural Usage Analytics")
    st.bar_chart({u: d["activity"] for u, d in st.session_state.user_db.items()})



# Chat History Display
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# --- 8. AI Intelligence Logic ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
u_input = st.chat_input("Enter command...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    # Real Activity Tracking
    if st.session_state.current_user in st.session_state.user_db:
        st.session_state.user_db[st.session_state.current_user]["activity"] += 5

    with st.chat_message("assistant"):
        with st.spinner(f"Alpha syncing with {model_choice}..."):
            # Real Model Mapping
            model_map = {
                "Normal (Llama 3.3 70B)": "llama-3.3-70b-versatile",
                "Pro Mode (GPT-OSS 120B)": "openai/gpt-oss-120b",
                "Logic Pro (Gemma 2)": "gemma2-9b-it",
                "Turbo Speed (Llama 3.1)": "llama-3.1-8b-instant",
                "Data Specialist (Mixtral)": "mixtral-8x7b-32768"
            }
            active_model = model_map.get(model_choice)
            
            sys_msg = f"You are Alpha AI created by Hasith Heshan. Current Engine: {model_choice}. Respond wisely in Sinhala or English."
            
            try:
                stream = client.chat.completions.create(
                    model=active_model,
                    messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages[-10:],
                    stream=True
                )
                full_res = ""
                res_area = st.empty()
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        res_area.markdown(full_res + "▌")
                res_area.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
                
                # Audio response
                tts = gTTS(text=full_res[:200], lang='en')
                tts.save("response.mp3")
                st.audio("response.mp3")
            except Exception as e: st.error(f"Neural Error: {e}")
