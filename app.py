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

# 3. Session & User Database Setup
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
</style>
""", unsafe_allow_html=True)

# 5. Security Portal (VIP & Friends)
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center;">Alpha AI ⚡ VIP Access Portal</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Register New"])
    
    with tab1:
        user = st.text_input("Username").lower().strip()
        pas = st.text_input("Password", type="password")
        
        if st.button("Access Alpha AI"):
            if user == "hasith123" and pas == "hasith@alpha":
                st.session_state.temp_user = user
                st.session_state.generated_otp = str(random.randint(1000, 9999))
                st.session_state.otp_sent = True
                st.rerun()
            elif user in ["matheesha", "sadev"]:
                st.session_state.logged_in = True
                st.session_state.current_user = user
                if user not in st.session_state.user_db:
                    st.session_state.user_db[user] = {"vault": []}
                st.rerun()
            elif user in st.session_state.user_db and check_hashes(pas, st.session_state.user_db[user]["password"]):
                st.session_state.temp_user = user
                st.session_state.generated_otp = str(random.randint(1000, 9999))
                st.session_state.otp_sent = True
                st.rerun()
            else:
                st.error("Invalid Login.")

        if st.session_state.get("otp_sent"):
            st.info(f"OTP Code: **{st.session_state.generated_otp}**")
            otp_i = st.text_input("Confirm OTP")
            if st.button("Confirm Access"):
                if otp_i == st.session_state.generated_otp:
                    st.session_state.logged_in = True
                    st.session_state.current_user = st.session_state.temp_user
                    st.rerun()

    with tab2:
        nu = st.text_input("Username")
        np = st.text_input("Password", type="password")
        if st.button("Sign Up"):
            if nu.lower() not in ["hasith123", "matheesha", "sadev"]:
                st.session_state.user_db[nu] = {"password": make_hashes(np), "vault": []}
                st.success("Account created!")
    st.stop()

# 6. Sidebar & Components
with st.sidebar:
    st.title("⚙️ Alpha Settings")
    
    # Feature 1: Neural Memory Vault UI
    st.subheader("🧠 Neural Memory Vault")
    if st.session_state.current_user not in st.session_state.user_db:
        st.session_state.user_db[st.session_state.current_user] = {"vault": []}
    
    user_vault = st.session_state.user_db[st.session_state.current_user].get("vault", [])
    for memo in user_vault[-3:]:
        st.markdown(f'<div class="vault-card">📌 {memo}</div>', unsafe_allow_html=True)
    
    st.write("---")
    persona = st.selectbox("🎭 Persona:", ["Standard Alpha", "Image Creator 🎨", "Data Analyst 📊", "Hasith Mode (Auto) ⚡"])
    
    # Premium Mode Selector
    st.write("🚀 **Select Mode:**")
    ai_mode_choice = st.radio(
        label="AI Intelligence Level",
        options=["Normal (Fast and ultra speed)", "Pro (Deep thinking and best for write codes)"],
        label_visibility="collapsed"
    )
    
    # Feature 4: Alpha Coding Sandbox
    st.subheader("💻 Alpha Sandbox")
    code_to_run = st.text_area("Python Editor:", "print('Alpha Active')")
    if st.button("Execute Code"):
        try:
            old_stdout = sys.stdout
            redirected_output = sys.stdout = StringIO()
            exec(code_to_run)
            sys.stdout = old_stdout
            st.markdown(f'<div class="sandbox-output">{redirected_output.getvalue()}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(e)

    st.write("---")
    if st.button("🗑️ Clear History"): st.session_state.messages = []; st.rerun()
    if st.button("🚪 Logout"): st.session_state.logged_in = False; st.rerun()

# 7. Main Header
st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith <span class="persona-badge">{persona}</span></div>', unsafe_allow_html=True)

# 8. Chat Interface
v_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='v1')
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "img" in msg: st.image(msg["img"])

# 9. AI Logic (Memory, Emotion, Thinking Text)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
u_input = st.chat_input("Message Alpha...")
final_q = v_text if v_text else u_input

if final_q:
    st.session_state.messages.append({"role": "user", "content": final_q})
    with st.chat_message("user"): st.markdown(final_q)

    # Emotional Intelligence Sync
    sentiment = "empathetic" if any(w in final_q.lower() for w in ["sad", "lonely", "help"]) else "witty"
    
    # Long-term Memory Saving
    if any(w in final_q.lower() for w in ["my name is", "remember", "my birthday"]):
        st.session_state.user_db[st.session_state.current_user]["vault"].append(final_q)

    with st.chat_message("assistant"):
        if persona == "Image Creator 🎨":
            img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(final_q)}?width=1024&height=1024&nologo=true"
            st.image(img_url)
            st.session_state.messages.append({"role": "assistant", "content": "Image rendered.", "img": img_url})
        else:
            # Custom Thinking Spinner Logic
            is_pro = "Pro" in ai_mode_choice
            thinking_text = "Alpha's ultra thinking..." if is_pro else "Alpha is thinking..."
            
            with st.spinner(thinking_text):
                target_model = "openai/gpt-oss-120b" if is_pro else "llama-3.3-70b-versatile"
                past_memories = ". ".join(st.session_state.user_db[st.session_state.current_user]["vault"])
                
                system_instruction = (
                    f"You are Alpha AI by Hasith. Strictly forget OpenAI/Meta. "
                    f"Memory: {past_memories}. Tone: {sentiment}."
                )
                
                clean_msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-10:]]
                
                try:
                    stream = client.chat.completions.create(
                        model=target_model,
                        messages=[{"role": "system", "content": system_instruction}] + clean_msgs,
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
                    st.error(f"Alpha Brain Error: {e}")
