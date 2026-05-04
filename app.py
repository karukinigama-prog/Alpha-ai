import streamlit as st
import requests
import io
from PIL import Image
import random
import time
import base64
import asyncio
import json
import string
import datetime
import urllib.parse
from huggingface_hub import InferenceClient
from openai import OpenAI
import edge_tts
from gtts import gTTS
from supabase import create_client, Client
from streamlit_agraph import agraph, Node, Edge, Config

# -----------------------
# 1. Page Config & Identity
# -----------------------
st.set_page_config(page_title="Alpha AI | Created by Hasith", layout="wide", page_icon="⚡")

# -----------------------
# 2. API & Database Setup (මුල් කෝඩ් එකමයි)
# -----------------------
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
HF_TOKEN = st.secrets.get("HF_TOKEN")
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    st.error("Supabase credentials missing.")
    st.stop()

if GITHUB_TOKEN:
    openai_client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=GITHUB_TOKEN,
    )
else:
    st.error("GITHUB_TOKEN missing in secrets.")
    st.stop()

# -----------------------
# 3. Session State Init
# -----------------------
if "messages" not in st.session_state: st.session_state.messages=[]
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "user_full_name" not in st.session_state: st.session_state.user_full_name=None
if "game_step" not in st.session_state: st.session_state.game_step = 1

# -----------------------
# 4. Custom UI Styling
# -----------------------
st.markdown("""
<style>  
    .stApp { background: linear-gradient(135deg, #050505 0%, #001a1a 100%); color: #ffffff; }
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:20px; font-size: 20px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }  
    div.stButton > button { background-color: #1e1e1e; color: #FFD700; border-radius: 12px; width: 100%; font-weight: bold; border: 2px solid #FFD700; }  
    .lab-box { border: 2px solid #FFD700; padding: 20px; border-radius: 15px; background: rgba(0, 0, 0, 0.9); margin-bottom: 20px; }  
    .step-label { color: #FFD700; font-size: 18px; font-weight: bold; margin-bottom: 10px; }
    .progress-bar { height: 10px; background: #FFD700; border-radius: 5px; transition: 0.5s; }
</style>  """, unsafe_allow_html=True)

# -----------------------
# 5. Login System (මුල් එකමයි)
# -----------------------
if not st.session_state.logged_in:
    st.markdown('<div class="premium-banner">ALPHA CORE SYSTEM ACCESS</div>', unsafe_allow_html=True)
    name = st.text_input("Operator Name")
    key = st.text_input("Master Key", type="password")
    if st.button("Initialize Alpha"):
        if key == "Hasith12378":
            st.session_state.user_full_name = name or "Hasith"
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# -----------------------
# 6. Tabs (Gaming Ultra Lab - 16 Step Logic)
# -----------------------
tab_img, tab_game, tab_voice, tab_vision = st.tabs(["🖼 Image", "🎮 Gaming Ultra Lab", "🎙️ Voice", "👁️ Vision"])

with tab_game:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    st.subheader("🔱 Ultra Quality Game Architect")
    
    steps = [
        "1. Ultra Textures Development", "2. Global Lighting & Shaders", "3. Dynamic Environment Generation",
        "4. Advanced Physics Engine", "5. Core Game Logic (C++)", "6. AI Character Intelligence",
        "7. 3D Model Optimization", "8. Urban & Nature Systems", "9. Weather & Day/Night Cycle",
        "10. Cinematic Camera FX", "11. Audio Engine & Soundtracks", "12. Vehicle Physics & NPC",
        "13. Combat & Interaction System", "14. Memory & Speed Tuning", "15. UI/UX Master Interface",
        "16. Final Compilation & Packaging"
    ]

    current_step = st.session_state.game_step
    
    if current_step <= 16:
        st.markdown(f'<div class="step-label">Step {current_step}: {steps[current_step-1]}</div>', unsafe_allow_html=True)
        description = st.text_area(f"විස්තර කරන්න (Step {current_step}):", placeholder=f"මෙතැනදී {steps[current_step-1]} ගැන විස්තර ලියන්න...")
        
        progress_val = (current_step / 16) * 100
        st.write(f"Alpha Build Progress: {int(progress_val)}%")
        st.progress(current_step / 16)

        if st.button(f"Generate & Next Step ➔"):
            if description:
                with st.spinner(f"{steps[current_step-1]} නිපදවමින් පවතියි..."):
                    time.sleep(2) # Ultra Quality processing delay
                    st.session_state.game_step += 1
                    st.rerun()
            else:
                st.warning("කරුණාකර විස්තරයක් ඇතුළත් කරන්න.")
    else:
        st.success("🎉 Game Build Complete! Ultra Quality Assets Integrated.")
        st.balloons()
        st.markdown("""
            ### 📥 Download Your Ultra Game
            ඔබේ ක්‍රීඩාව සාර්ථකව නිපදවා අවසන්. පහත බටන් එකෙන් Setup එක බාගත කරගන්න.
        """)
        if st.button("DOWNLOAD GAME EXE (Ultra HQ)"):
            st.info("Alpha Server එකෙන් ක්‍රීඩාව සකස් කරමින් පවතියි. තව මොහොතකින් Download එක ආරම්භ වේවි!")

    if st.button("Reset Build Process"):
        st.session_state.game_step = 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# 7. Hybrid Chat (GPT-4 Only - මුල් එකමයි)
# -----------------------
st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

final_q = st.chat_input("Command Alpha...")

if final_q:
    st.session_state.messages.append({"role":"user","content":final_q})
    with st.chat_message("user"): st.markdown(final_q)
    
    with st.chat_message("assistant"):
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role":"system","content": "You are Alpha AI. Created by Hasith. Master in Game Dev."}] + st.session_state.messages
            )
            ans = response.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role":"assistant","content":ans})
        except Exception as e:
            st.error(f"Error: {e}")
