import streamlit as st
from groq import Groq
import time
from gtts import gTTS
import os

# --- 1. Page Configuration ---
st.set_page_config(page_title="Alpha AI ⚡ Hasith's Empire", page_icon="⚡", layout="wide")

# --- 2. ⚡ Imperial Loading Screen (Exactly 7 Seconds) ---
if "loaded" not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
            <style>
                .loader-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh; }
                .alpha-text { font-size: 65px; font-weight: bold; color: #FFD700; text-shadow: 0 0 30px #FF8C00; margin-bottom: 20px; font-family: 'Arial Black', sans-serif; animation: glow 1.5s infinite alternate; }
                .loading-bar { width: 450px; height: 8px; background: #222; border-radius: 10px; overflow: hidden; border: 1px solid #FFD700; }
                .progress { width: 100%; height: 100%; background: linear-gradient(90deg, #FFD700, #FF8C00); animation: load 7s linear forwards; }
                @keyframes load { 0% { width: 0; } 100% { width: 100%; } }
                @keyframes glow { from { text-shadow: 0 0 15px #FFD700; } to { text-shadow: 0 0 35px #FF8C00; } }
            </style>
            <div class="loader-container">
                <div class="alpha-text">⚡ ALPHA IS INITIALIZING</div>
                <div class="loading-bar"><div class="progress"></div></div>
                <p style="color: #888; margin-top: 20px; letter-spacing: 4px; font-weight: bold;">CREATED BY HASITH HESHAN</p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(7)
    st.session_state.loaded = True
    st.rerun()

# --- 3. Pure Real-Time Data Store (No Hallucinated Data) ---
if "user_db" not in st.session_state: st.session_state.user_db = {}
if "active_logs" not in st.session_state: st.session_state.active_logs = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_user" not in st.session_state: st.session_state.current_user = None
if "messages" not in st.session_state: st.session_state.messages = []

# --- 4. Premium Imperial UI Styling ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: white; }
    .login-container { background: rgba(10,10,10,0.95); border: 2px solid #FFD700; padding: 40px; border-radius: 30px; box-shadow: 0 0 50px rgba(255, 215, 0, 0.2); text-align: center; }
    div.stButton > button { background: linear-gradient(45deg, #FFD700, #FF8C00); color: black !important; font-weight: bold; border-radius: 15px; height: 50px; border: none; width: 100%; transition: 0.3s; }
    div.stButton > button:hover { transform: scale(1.02); box-shadow: 0 0 20px #FFD700; }
    .admin-card { background: #111; border-left: 5px solid #FFD700; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-top: 1px solid #333; }
    .engine-box { border: 1px solid #FFD700; padding: 15px; border-radius: 15px; background: rgba(255, 215, 0, 0.05); margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 5. Access Portal ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container"><h1 style="color:#FFD700; letter-spacing:5px;">ALPHA PRO ⚡</h1><p style="color:#888;">NEURAL ACCESS POINT</p></div>', unsafe_allow_html=True)
        t1, t2 = st.tabs(["🔐 AUTHORIZE", "📝 REGISTER"])
        with t1:
            u = st.text_input("Access Identity").lower().strip()
            p = st.text_input("Security Passcode", type="password")
            if st.button("EXECUTE ENTRY"):
                # Admin Access
                if u == "hasith123" and p == "hasith@alpha":
                    st.session_state.logged_in = True; st.session_state.current_user = u
                    st.session_state.active_logs.append(f"Admin (HASITH) - {time.strftime('%H:%M:%S')}")
                    st.rerun()
                # User Access
                elif u in st.session_state.user_db and st.session_state.user_db[u]["password"] == p:
                    st.session_state.logged_in = True; st.session_state.current_user = u
                    st.session_state.active_logs.append(f"User: {u.upper()} - {time.strftime('%H:%M:%S')}")
                    st.rerun()
                else: st.error("ACCESS DENIED: IDENTITY NOT RECOGNIZED")
        with t2:
            nu = st.text_input("New Identity Name")
            np = st.text_input("New Passcode", type="password")
            if st.button("SYNC TO SYSTEM"):
                if nu and np:
                    st.session_state.user_db[nu.lower()] = {"password": np, "activity": 0}
                    st.success(f"Identity '{nu}' Created Successfully!")
    st.stop()

# --- 6. Sidebar (Admin Panel & Model Selector Bar) ---
with st.sidebar:
    st.markdown('<h2 style="color:#FFD700;">⚙️ COMMAND CENTER</h2>', unsafe_allow_html=True)
    
    # Supreme Admin Panel (Visible only to Hasith)
    if st.session_state.current_user == "hasith123":
        st.markdown('<div class="admin-card">', unsafe_allow_html=True)
        st.markdown('<h3 style="color:#FFD700; text-align:center;">👑 SUPREME ADMIN</h3>', unsafe_allow_html=True)
        st.metric("Total Real Users", len(st.session_state.user_db))
        st.write("📊 **Neural Activity Tracking**")
        if not st.session_state.user_db: st.caption("No users registered.")
        else:
            for user, data in st.session_state.user_db.items():
                st.write(f"{user.capitalize()}")
                st.progress(min(100, data.get("activity", 0)) / 100)
        st.write("📱 **Live Session Logs**")
        for log in st.session_state.active_logs[-8:]: st.caption(f"✔ {log}")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- THE MODEL SELECTION BAR ---
    st.markdown('<div class="engine-box">', unsafe_allow_html=True)
    st.subheader("🧠 Intelligence Engine")
    model_choice = st.selectbox(
        "Select Neural Core:",
        [
            "Normal Mode (Llama 3.3 70B)", 
            "Pro Mode (GPT-OSS 120B)", 
            "Gemma 2 (Logic Pro)", 
            "Llama 3.1 (Turbo Speed)",
            "Mixtral (Data Specialist)"
        ]
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("TERMINATE SESSION"):
        st.session_state.logged_in = False
        st.rerun()

# --- 7. Main Interface ---
st.markdown('<div style="background: linear-gradient(90deg, #FFD700, #FF8C00); padding: 12px; border-radius: 12px; color: black; text-align: center; font-weight: bold; font-size: 18px;">⚡ ALPHA AI ULTIMATE COMMAND CENTER | CREATED BY HASITH</div>', unsafe_allow_html=True)

# Dashboard Graph for Hasith
if st.session_state.current_user == "hasith123" and st.session_state.user_db:
    st.write("### 📈 Real-time System Analytics")
    activity_chart = {u: d["activity"] for u, d in st.session_state.user_db.items()}
    st.bar_chart(activity_chart)

# Chat History Display
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# --- 8. AI Intelligence (Logic) ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
u_input = st.chat_input("Enter command to Alpha...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    # Update Real Activity
    if st.session_state.current_user in st.session_state.user_db:
        st.session_state.user_db[st.session_state.current_user]["activity"] += 5

    with st.chat_message("assistant"):
        with st.spinner(f"Alpha utilizing {model_choice}..."):
            # Real-time Model Mapping
            model_map = {
                "Normal Mode (Llama 3.3 70B)": "llama-3.3-70b-versatile",
                "Pro Mode (GPT-OSS 120B)": "openai/gpt-oss-120b",
                "Gemma 2 (Logic Pro)": "gemma2-9b-it",
                "Llama 3.1 (Turbo Speed)": "llama-3.1-8b-instant",
                "Mixtral (Data Specialist)": "mixtral-8x7b-32768"
            }
            active_model = model_map.get(model_choice)
            
            sys_prompt = f"You are Alpha AI, an imperial neural system created by Hasith Heshan. You are operating in {model_choice}. Be helpful, wise, and respond in Sinhala or English."
            
            try:
                stream = client.chat.completions.create(
                    model=active_model,
                    messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages[-10:],
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
                
                # Voice feedback
                tts = gTTS(text=full_res[:200], lang='en')
                tts.save("response.mp3")
                st.audio("response.mp3")
            except Exception as e: st.error(f"Neural Sync Error: {e}")
