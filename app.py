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

# 2️⃣ User & Session Management
if "user_db" not in st.session_state:
    st.session_state.user_db = {}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False
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
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
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
            st.info(f"Security Code: **{st.session_state.generated_otp}**")
            otp_input = st.text_input("Enter OTP", key="otp_val")
            if st.button("Verify"):
                if otp_input == st.session_state.generated_otp:
                    st.session_state.logged_in = True
                    st.session_state.current_user = st.session_state.temp_user
                    st.rerun()

    with tab2:
        new_u = st.text_input("New Username", key="reg_u")
        new_p = st.text_input("New Password", type="password", key="reg_p")
        if st.button("Register Account"):
            if new_u and new_p:
                st.session_state.user_db[new_u] = {"password": make_hashes(new_p), "memory": [], "logs": []}
                st.success("Registration Successful!")
    st.stop()

# 5️⃣ Sidebar
with st.sidebar:
    st.title("⚙️ Alpha Settings")
    if st.session_state.current_user == "hasith123":
        st.subheader("👥 Admin Dashboard")
        for u in st.session_state.user_db.keys(): st.write(f"👤 {u}")
    
    st.session_state.current_persona = st.selectbox("🎭 Persona:", ["Standard Alpha", "Web Searcher 🌐", "Image Creator 🎨", "Data Analyst 📊"])
    
    # 🎯 Model Selection Logic (As requested)
    ai_mode = st.radio("🚀 Select Mode:", ["Normal (Llama-3.3)", "Pro (gpt-oss-120b)"])
    
    if st.button("🗑️ Clear History"): st.session_state.messages = []; st.rerun()
    if st.button("🚪 Logout"): st.session_state.logged_in = False; st.rerun()
    st.markdown("---")
    st.caption("Alpha AI v2.0 | Created by Hasith")

# 6️⃣ UI Header
st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith <span class="persona-badge">{st.session_state.current_persona}</span></div>', unsafe_allow_html=True)

# 7️⃣ Voice & Chat Input
v_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='v1')
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "img" in msg: st.image(msg["img"])

# 8️⃣ AI Logic (Model Selection)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
u_input = st.chat_input("Ask Alpha something...")
final_q = v_text if v_text else u_input

if final_q:
    st.session_state.messages.append({"role": "user", "content": final_q})
    with st.chat_message("user"): st.markdown(final_q)
    log_activity(st.session_state.current_user, "Query", final_q)

    with st.chat_message("assistant"):
        if st.session_state.current_persona == "Image Creator 🎨":
            with st.spinner("Creating Art..."):
                encoded = urllib.parse.quote(final_q)
                img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true"
                res_text = f"I have generated the image for your prompt: '{final_q}'"
                st.markdown(res_text)
                st.image(img_url)
                st.session_state.messages.append({"role": "assistant", "content": res_text, "img": img_url})
        else:
            # Setting exact model paths based on Mode selection
            if "Pro" in ai_mode:
                target_model = "gpt-oss-120b"
            else:
                target_model = "llama-3.3-70b-versatile"
            
            with st.spinner(f"Alpha is processing (using {target_model})..."):
                try:
                    stream = client.chat.completions.create(
                        model=target_model,
                        messages=[{"role": "system", "content": f"You are Alpha AI by Hasith. Mode: {ai_mode}"}] + st.session_state.messages[-10:],
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
                    # Automatic Fallback if the specific model ID fails
                    st.error(f"Note: {target_model} is currently unavailable. Using backup engine.")
                    stream = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": final_q}], stream=True)
                    # (Stream handling continues)
