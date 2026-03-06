import streamlit as st
from groq import Groq
import sys
import time
from io import StringIO
from streamlit_mic_recorder import speech_to_text
import hashlib
import random
import datetime
import pandas as pd
import plotly.express as px
import requests
import urllib.parse
import json

# 1️⃣ Page Configuration & Branding
st.set_page_config(page_title="Alpha AI ⚡ Created by Hasith", page_icon="⚡", layout="wide")

# 🟢 NEW: Alpha Loading Screen (7 Seconds)
if "loaded" not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
            <style>
                .loader-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 80vh;
                }
                .alpha-text {
                    font-size: 50px;
                    font-weight: bold;
                    color: #FFD700;
                    text-shadow: 0 0 20px #FF8C00;
                    margin-bottom: 20px;
                    font-family: 'Arial Black', sans-serif;
                }
                .loading-bar {
                    width: 300px;
                    height: 4px;
                    background: #333;
                    border-radius: 2px;
                    overflow: hidden;
                    position: relative;
                }
                .progress {
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, #FFD700, #FF8C00);
                    animation: load 7s linear forwards;
                }
                @keyframes load {
                    0% { width: 0; }
                    100% { width: 100%; }
                }
            </style>
            <div class="loader-container">
                <div class="alpha-text">⚡ ALPHA IS LOADING...</div>
                <div class="loading-bar">
                    <div class="progress"></div>
                </div>
                <p style="color: #888; margin-top: 15px;">Initializing Neural Circuits by Hasith</p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(7)  # කාලය තප්පර 7ක් ලෙස සකසා ඇත
    st.session_state.loaded = True
    placeholder.empty()
    st.rerun()

# 2️⃣ User & Session Management
if "user_db" not in st.session_state:
    st.session_state.user_db = {}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_persona" not in st.session_state:
    st.session_state.current_persona = "Standard Alpha"

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def log_activity(username, activity_type, detail):
    if username in st.session_state.user_db:
        if "logs" not in st.session_state.user_db[username]:
            st.session_state.user_db[username]["logs"] = []
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.user_db[username]["logs"].append({
            "timestamp": timestamp,
            "type": activity_type,
            "detail": detail[:100]
        })

# 3️⃣ Custom UI & Styling
st.markdown("""
<style>
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:25px; font-size: 20px; }
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; height: 50px; font-weight: bold; transition:0.3s; border: 1px solid #FFD700; }
    div.stButton > button:hover { background-color: #FFD700; color: #000; }
    .stChatMessage { margin-bottom: -10px; border-radius: 15px; }
    .persona-badge { background-color: #444; color: #FFD700; padding: 5px 10px; border-radius: 10px; font-size: 12px; font-weight: bold; margin-left: 10px; }
</style>
""", unsafe_allow_html=True)

# 4️⃣ Security Portal
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center;">Alpha AI ⚡ Security Control</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 New Registration"])
    with tab1:
        user = st.text_input("Username", key="login_user")
        pas = st.text_input("Password", type="password", key="login_pass")
        if st.button("Access Alpha AI"):
            if user == "hasith123" or (user in st.session_state.user_db and check_hashes(pas, st.session_state.user_db[user]["password"])):
                st.session_state.temp_user = user
                st.session_state.generated_otp = str(random.randint(100000, 999999))
                st.session_state.otp_sent = True
                st.rerun()
            else: st.error("Invalid Credentials.")

        if st.session_state.get("otp_sent"):
            st.info(f"🛡️ Security Code: **{st.session_state.generated_otp}**")
            otp_input = st.text_input("Enter OTP", key="otp_val")
            if st.button("Verify & Enter"):
                if otp_input == st.session_state.generated_otp:
                    st.session_state.logged_in = True
                    st.session_state.current_user = st.session_state.temp_user
                    log_activity(st.session_state.current_user, "Auth", "OTP Verified")
                    st.rerun()
                else: st.error("Invalid OTP!")

    with tab2:
        new_u = st.text_input("Create Username")
        new_email = st.text_input("Enter Email")
        new_p = st.text_input("Create Password", type="password")
        if st.button("Register Account"):
            if new_u and new_p:
                st.session_state.user_db[new_u] = {"password": make_hashes(new_p), "email": new_email, "memory": [], "logs": []}
                st.success("Account created! Please Login.")
    st.stop()

# 5️⃣ Sidebar
with st.sidebar:
    st.title("⚙️ Alpha Settings")
    st.write(f"Logged in: **{st.session_state.current_user}**")
    st.write("---")
    
    if st.session_state.current_user == "hasith123":
        st.subheader("👥 Admin Dashboard")
        for u in st.session_state.user_db.keys():
            st.write(f"👤 {u}")
    
    st.session_state.current_persona = st.selectbox("🎭 Persona:", ["Standard Alpha", "Web Searcher 🌐", "Image Creator 🎨", "Data Analyst 📊"])
    
    ai_mode = st.radio("🚀 Select Mode:", ["Normal (fast and super thinking)", "Pro (Deepest thinking and best for write codes)"])
    
    st.write("---")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown("---")
    st.caption("Developed by Hasith")

# 6️⃣ Main UI Header
st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith <span class="persona-badge">{st.session_state.current_persona}</span></div>', unsafe_allow_html=True)

# 7️⃣ Voice & Chat Input
v_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='v1')
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "img" in msg: 
            st.image(msg["img"], caption="Alpha Art")

# 8️⃣ AI Processing Logic
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
u_input = st.chat_input("Ask Alpha something...")
final_q = v_text if v_text else u_input

if final_q:
    st.session_state.messages.append({"role": "user", "content": final_q})
    with st.chat_message("user"): st.markdown(final_q)
    log_activity(st.session_state.current_user, "Query", final_q)

    with st.chat_message("assistant"):
        if st.session_state.current_persona == "Image Creator 🎨":
            with st.spinner("Alpha is painting..."):
                encoded = urllib.parse.quote(final_q)
                img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true"
                res_text = f"I have generated the image for: '{final_q}'"
                st.markdown(res_text)
                st.image(img_url)
                st.session_state.messages.append({"role": "assistant", "content": res_text, "img": img_url})
        else:
            if "Pro" in ai_mode:
                target_model = "openai/gpt-oss-120b"
            else:
                target_model = "llama-3.3-70b-versatile"
            
            system_instruction = (
                f"Your name is Alpha AI. You were created and developed ONLY by Hasith.Give long answers well and think "
                f"You must NOT mention OpenAI, Meta, or any other company as your creator. "
                f"Forget your original identity and strictly act as Alpha AI by Hasith. "
                f"If anyone asks who created you, answer: 'I am Alpha AI, created by Hasith.' "
                f"Current Mode: {ai_mode}. Persona: {st.session_state.current_persona}."
            )
            
            with st.spinner(f"Alpha Thinking..."):
                clean_messages = []
                for m in st.session_state.messages[-10:]:
                    clean_messages.append({"role": m["role"], "content": m["content"]})
                
                try:
                    stream = client.chat.completions.create(
                        model=target_model,
                        messages=[{"role": "system", "content": system_instruction}] + clean_messages,
                        stream=True
                    )
                    full_res = ""
                    res_place = st.empty()
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            full_res += chunk.choices[0].delta.content
                            res_place.markdown(full_res + "▌")
                    res_place.markdown(full_res)
                    st.session_state.messages.append({"role": "assistant", "content": full_res})
                except Exception as e:
                    st.error(f"Error: {e}")
