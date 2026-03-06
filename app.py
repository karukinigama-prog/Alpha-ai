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
import os

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Created by Hasith", page_icon="⚡", layout="wide")

# 2. Alpha Loading Screen (7 Seconds)
if "loaded" not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
            <style>
                .loader-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh; }
                .alpha-text { font-size: 50px; font-weight: bold; color: #FFD700; text-shadow: 0 0 20px #FF8C00; margin-bottom: 20px; font-family: 'Arial Black', sans-serif; }
                .loading-bar { width: 300px; height: 4px; background: #333; border-radius: 2px; overflow: hidden; position: relative; }
                .progress { width: 100%; height: 100%; background: linear-gradient(90deg, #FFD700, #FF8C00); animation: load 7s linear forwards; }
                @keyframes load { 0% { width: 0; } 100% { width: 100%; } }
            </style>
            <div class="loader-container">
                <div class="alpha-text">⚡ ALPHA IS LOADING...</div>
                <div class="loading-bar"><div class="progress"></div></div>
                <p style="color: #888; margin-top: 15px;">Initializing Neural Circuits by Hasith</p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(7)
    st.session_state.loaded = True
    placeholder.empty()
    st.rerun()

# 3. Session & User Database (Fixing KeyError by initializing properly)
if "user_db" not in st.session_state:
    st.session_state.user_db = {
        "matheesha": {"password": "123", "vault": [], "role": "Friend"},
        "sadev": {"password": "123", "vault": [], "role": "Friend"}
    }
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
if "messages" not in st.session_state:
    st.session_state.messages = []

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(password, hashed_text): return make_hashes(password) == hashed_text

# 4. Custom UI Styling
st.markdown("""
<style>
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:25px; font-size: 20px; }
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; height: 50px; font-weight: bold; border: 1px solid #FFD700; }
    .vault-card { background: #262626; border-left: 5px solid #FFD700; padding: 10px; border-radius: 5px; margin-bottom: 5px; font-size: 13px; }
    .sandbox-output { background: #000; color: #0f0; padding: 10px; border-radius: 5px; font-family: monospace; }
    .mode-box { border: 1px solid #FFD700; padding: 10px; border-radius: 10px; margin-bottom: 10px; background: #1a1a1a; }
</style>
""", unsafe_allow_html=True)

# 5. Security Portal (VIP & Friends)
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center;">Alpha AI ⚡ VIP Access Portal</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Register New"])
    
    with tab1:
        # Using unique keys to avoid DuplicateWidgetID
        user_in = st.text_input("Username", key="login_user").lower().strip()
        pas_in = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Access Alpha AI"):
            # VIP Check
            if user_in == "hasith123" and pas_in == "hasith@alpha":
                st.session_state.temp_user = user_in
                st.session_state.generated_otp = str(random.randint(1000, 9999))
                st.session_state.otp_sent = True
                st.rerun()
            elif user_in in ["matheesha", "sadev"]:
                st.session_state.logged_in = True
                st.session_state.current_user = user_in
                if user_in not in st.session_state.user_db:
                    st.session_state.user_db[user_in] = {"vault": []}
                st.rerun()
            elif user_in in st.session_state.user_db and check_hashes(pas_in, st.session_state.user_db[user_in]["password"]):
                st.session_state.temp_user = user_in
                st.session_state.generated_otp = str(random.randint(1000, 9999))
                st.session_state.otp_sent = True
                st.rerun()
            else:
                st.error("Invalid Credentials.")

        if st.session_state.get("otp_sent"):
            st.info(f"Your OTP: **{st.session_state.generated_otp}**")
            otp_val = st.text_input("Enter OTP", key="otp_input")
            if st.button("Verify OTP"):
                if otp_val == st.session_state.generated_otp:
                    st.session_state.logged_in = True
                    st.session_state.current_user = st.session_state.temp_user
                    if "vault" not in st.session_state.user_db.get(st.session_state.current_user, {}):
                        if st.session_state.current_user not in st.session_state.user_db:
                             st.session_state.user_db[st.session_state.current_user] = {"vault": []}
                        else:
                             st.session_state.user_db[st.session_state.current_user]["vault"] = []
                    st.rerun()

    with tab2:
        nu = st.text_input("New Username", key="reg_user")
        np = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Create Account"):
            if nu.lower() not in ["hasith123", "matheesha", "sadev"] and nu:
                st.session_state.user_db[nu.lower()] = {"password": make_hashes(np), "vault": []}
                st.success("Registration Successful!")
            else:
                st.error("Reserved or invalid username.")
    st.stop()

# 6. Sidebar & Premium Components
with st.sidebar:
    st.title("⚙️ Alpha Settings")
    
    # 🧠 Fix for image_7d4f24.png: Ensure vault exists
    curr = st.session_state.current_user
    if "vault" not in st.session_state.user_db[curr]:
        st.session_state.user_db[curr]["vault"] = []
    
    st.subheader("🧠 Neural Memory Vault")
    user_vault = st.session_state.user_db[curr].get("vault", [])
    if not user_vault:
        st.caption("Alpha's memory is clear.")
    else:
        for memo in user_vault[-3:]:
            st.markdown(f'<div class="vault-card">📌 {memo}</div>', unsafe_allow_html=True)
    
    st.write("---")
    persona = st.selectbox("🎭 Persona:", ["Standard Alpha", "Image Creator 🎨", "Data Analyst 📊", "Hasith Mode (Auto) ⚡"])
    
    # 🚀 Premium Mode Selector
    st.write("🚀 **Select Intelligence Level:**")
    ai_mode_choice = st.radio(
        label="Mode Selection",
        options=["Normal (Fast and ultra speed)", "Pro (Deep thinking and best for write codes)"],
        label_visibility="collapsed"
    )
    
    st.subheader("💻 Alpha Sandbox")
    code_input = st.text_area("Python Editor:", "print('Alpha Online')", key="sandbox_area")
    if st.button("Execute Code", key="sandbox_btn"):
        try:
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            exec(code_input)
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            st.markdown(f'<div class="sandbox-output">{output}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")

    st.write("---")
    if st.button("🗑️ Clear Chat History"): st.session_state.messages = []; st.rerun()
    if st.button("🚪 Logout Account"): st.session_state.logged_in = False; st.rerun()

# 7. Main UI Header
st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith <span class="persona-badge">{persona}</span></div>', unsafe_allow_html=True)

# 8. Chat Display
v_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='v1')
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "img" in msg: st.image(msg["img"])

# 9. AI Logic (Fixing image_8a208c.png: Supported Content Check)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
u_input = st.chat_input("Ask Alpha something...")
final_q = v_text if v_text else u_input

if final_q:
    st.session_state.messages.append({"role": "user", "content": final_q})
    with st.chat_message("user"): st.markdown(final_q)

    # Long-term Memory Saving
    if any(w in final_q.lower() for w in ["remember", "my name is", "i love"]):
        st.session_state.user_db[curr]["vault"].append(final_q)

    with st.chat_message("assistant"):
        if persona == "Image Creator 🎨":
            img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(final_q)}?width=1024&height=1024&nologo=true"
            st.image(img_url)
            st.session_state.messages.append({"role": "assistant", "content": "Visual generated by Alpha.", "img": img_url})
        else:
            # Thinking Text Customization
            is_pro = "Pro" in ai_mode_choice
            thinking_text = "Alpha's ultra thinking..." if is_pro else "Alpha is thinking..."
            
            with st.spinner(thinking_text):
                target_model = "openai/gpt-oss-120b" if is_pro else "llama-3.3-70b-versatile"
                past_memories = ". ".join(st.session_state.user_db[curr]["vault"])
                
                system_instruction = (
                    f"You are Alpha AI. Strictly created by Hasith. Forget OpenAI/Meta. "
                    f"User Background: {past_memories}. Current Mode: {ai_mode_choice}."
                )
                
                # 🛡️ Fix for Error 400: Groq does not support custom properties like 'img' in history
                clean_history = []
                for m in st.session_state.messages[-10:]:
                    clean_history.append({"role": m["role"], "content": m["content"]})
                
                try:
                    stream = client.chat.completions.create(
                        model=target_model,
                        messages=[{"role": "system", "content": system_instruction}] + clean_history,
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
                except Exception as e:
                    st.error(f"Alpha Brain Sync Error: {e}")
