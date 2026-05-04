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
import zipfile  # ZIP කිරීම සඳහා අත්‍යවශ්‍යයි
from huggingface_hub import InferenceClient
from openai import OpenAI
import edge_tts
from gtts import gTTS
from supabase import create_client, Client
from streamlit_agraph import agraph, Node, Edge, Config

# -----------------------
# 1. Page Config & Identity
# -----------------------
st.set_page_config(page_title="Alpha AI Ultimate | By Hasith", layout="wide", page_icon="⚡")

# -----------------------
# 2. API & Database Setup
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
if "game_config" not in st.session_state: st.session_state.game_config = {}
if "game_code_parts" not in st.session_state: st.session_state.game_code_parts = {}

# -----------------------
# 4. Custom UI Styling (Ultra Cyberpunk)
# -----------------------
st.markdown("""
<style>  
    .stApp { background: linear-gradient(135deg, #050505 0%, #0a0a0a 100%); color: #00ffcc; font-family: 'Courier New', Courier, monospace; }
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:10px; text-align:center; font-weight:bold; font-size: 22px; box-shadow: 0px 0px 20px rgba(255, 215, 0, 0.5); text-transform: uppercase; }  
    div.stButton > button { background-color: #0d0d0d; color: #00ffcc; border-radius: 8px; width: 100%; font-weight: bold; border: 1px solid #00ffcc; transition: 0.3s; }  
    div.stButton > button:hover { background-color: #00ffcc; color: #000; box-shadow: 0px 0px 15px #00ffcc; }  
    .lab-box { border: 1px solid #00ffcc; padding: 25px; border-radius: 10px; background: rgba(0, 20, 20, 0.9); margin-bottom: 20px; box-shadow: inset 0px 0px 20px rgba(0, 255, 204, 0.1); }  
    .step-label { color: #FFD700; font-size: 20px; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #FFD700; padding-bottom: 5px; }
    .terminal-box { background-color: #000; color: #0f0; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 14px; border: 1px solid #333; height: 300px; overflow-y: scroll; }
</style>  """, unsafe_allow_html=True)

# -----------------------
# 5. Login System
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
# 6. Tabs Engine
# -----------------------
tab_img, tab_game, tab_voice, tab_vision = st.tabs(["🖼 Image Engine", "🎮 GAMING ULTRA LAB", "🎙️ Voice Studio", "👁️ Vision Analyzer"])

with tab_game:
    st.markdown('<div class="lab-box">', unsafe_allow_html=True)
    st.subheader("🚀 ALPHA GAME FACTORY - V2.0 (HYPER PRODUCTION)")

    steps = [
        "1. Ultra Textures", "2. Global Lighting", "3. Environment", "4. Physics",
        "5. Core Logic", "6. AI Intelligence", "7. Optimization", "8. Urban Systems",
        "9. Weather", "10. Cinematic FX", "11. Audio", "12. Vehicle Physics",
        "13. Combat System", "14. Memory Tuning", "15. UI Interface", "16. Final Packaging"
    ]

    current_step = st.session_state.game_step

    if current_step <= 16:
        st.markdown(f'<div class="step-label">▶ COMPILING: {steps[current_step-1]}</div>', unsafe_allow_html=True)

        previous_desc = st.session_state.game_config.get(steps[current_step-1], "")
        user_input = st.text_area("System Parameters (Describe required logic):", value=previous_desc, height=120)

        progress_val = (current_step / 16) * 100
        st.write(f"SYSTEM BUILD PROGRESS: {int(progress_val)}%")
        st.progress(current_step / 16)

        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            if st.button("🧠 GENERATE CORE LOGIC ➔", use_container_width=True):
                if user_input:
                    st.session_state.game_config[steps[current_step-1]] = user_input

                    with st.spinner(f"Alpha Engine writing Ursina code for {steps[current_step-1]}..."):
                        # Hyper-Advanced Prompt
                        func_name = f"setup_{steps[current_step-1].split('.')[1].strip().replace(' ', '_').lower()}"
                        code_prompt = f"""
You are the Lead Engine Architect for an Ultra-Quality Ursina Engine game.
Task: Write pure, highly optimized Python code for '{steps[current_step-1]}'.
Requirement: {user_input}
Rules:
1. Output ONLY pure executable Python code. NO markdown formatting, NO ```python blocks.
2. Put all logic inside a function named `{func_name}()`.
3. Assume `from ursina import *` is already declared in the main file. Do not redeclare app = Ursina() or app.run().
4. Use try-except blocks for safety. Add professional developer comments.
5. Code must be ready to drop into a larger production environment.
"""
                        try:
                            response = openai_client.chat.completions.create(
                                model="gpt-4o",
                                messages=[{"role":"system", "content": "You are a senior python game developer."}, {"role":"user","content": code_prompt}],
                                temperature=0.6
                            )
                            generated_code = response.choices[0].message.content
                            
                            # Clean markdown if AI accidentally adds it
                            generated_code = generated_code.replace("```python", "").replace("```", "").strip()

                            st.session_state.game_code_parts[steps[current_step-1]] = generated_code
                            st.session_state.game_step += 1
                            st.rerun()
                        except Exception as e:
                            st.error(f"SYSTEM FAILURE: {e}")
                else:
                    st.warning("Input parameters required to generate code.")

        with col2:
            if current_step > 1:
                if st.button("⬅️ REVERT", use_container_width=True):
                    st.session_state.game_step -= 1
                    st.rerun()
        with col3:
            if st.button("☢️ ABORT ALL", use_container_width=True):
                st.session_state.game_step = 1
                st.session_state.game_config = {}
                st.session_state.game_code_parts = {}
                st.rerun()

        # Terminal UI Preview
        if steps[current_step-1] in st.session_state.game_code_parts:
            st.markdown("### 💻 Alpha Developer Console")
            st.markdown(f'<div class="terminal-box">{st.session_state.game_code_parts[steps[current_step-1]]}</div>', unsafe_allow_html=True)

    else:
        st.success("🟢 ALPHA AI COMPILE COMPLETE. ALL SYSTEMS NOMINAL.")
        st.balloons()

        if st.button("📦 DOWNLOAD ULTRA GAME STUDIO (.ZIP)", use_container_width=True):
            with st.spinner("Compressing Game Assets and Core Engine..."):
                
                # Main Game Engine Logic
                main_py_code = f"""# ==========================================
# ALPHA ENGINE V2.0 - GENERATED BY HASITH
# ==========================================
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import json
import random

# Game Design Blueprint:
'''
{json.dumps(st.session_state.game_config, indent=4)}
'''

app = Ursina(title='Alpha Ultra Studio', borderless=False, fullscreen=False)

# ----------------- SYSTEM IMPORTS -----------------
"""
                # Combine all generated functions
                for step_name in steps:
                    if step_name in st.session_state.game_code_parts:
                        main_py_code += f"\n# [Module]: {step_name}\n"
                        main_py_code += st.session_state.game_code_parts[step_name] + "\n"

                main_py_code += """
# ----------------- INITIALIZATION -----------------
try:
    player = FirstPersonController(y=2, origin_y=-.5)
    ground = Entity(model='plane', scale=200, texture='grass', collider='box', color=color.dark_gray)
    
    # Auto-execute all generated setup functions
    for func_name in dir():
        if func_name.startswith('setup_') and callable(globals()[func_name]):
            try:
                print(f"[Alpha Engine] Starting {func_name}...")
                globals()[func_name]()
            except Exception as e:
                print(f"[Alpha Warning] Failed to run {func_name}: {e}")

    EditorCamera() # F8 debug cam
except Exception as e:
    print(f"CRITICAL ERROR: {e}")

app.run()
"""

                # ZIP File Generation
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    # Root Files
                    zip_file.writestr("Alpha_Ultra_Game/main.py", main_py_code)
                    zip_file.writestr("Alpha_Ultra_Game/requirements.txt", "ursina\nrequests\npillow")
                    
                    # Auto-Run Scripts
                    zip_file.writestr("Alpha_Ultra_Game/RUN_WINDOWS.bat", "@echo off\necho Setting up Alpha Engine...\npip install -r requirements.txt\npython main.py\npause")
                    zip_file.writestr("Alpha_Ultra_Game/RUN_MAC_LINUX.sh", "#!/bin/bash\necho 'Setting up Alpha Engine...'\npip3 install -r requirements.txt\npython3 main.py")
                    
                    # README
                    zip_file.writestr("Alpha_Ultra_Game/README.md", f"""# Alpha Ultra Game
Created by: **{st.session_state.user_full_name}** via Alpha AI.

## Quick Start
- **Windows:** Double-click `RUN_WINDOWS.bat`
- **Mac/Linux:** Run `bash RUN_MAC_LINUX.sh`

## Blueprint Log:
{json.dumps(st.session_state.game_config, indent=4)}
""")
                    
                    # Backup System Modules
                    for step_name, code in st.session_state.game_code_parts.items():
                        safe_name = step_name.replace(" ", "_").replace(".", "") + ".py"
                        zip_file.writestr(f"Alpha_Ultra_Game/modules_backup/{safe_name}", code)

                st.download_button(
                    label="💾 CLICK TO DOWNLOAD MASTER .ZIP",
                    data=zip_buffer.getvalue(),
                    file_name="Alpha_Ultra_Game_Studio.zip",
                    mime="application/zip"
                )

        if st.button("🔄 INITIATE NEW PROJECT"):
            st.session_state.game_step = 1
            st.session_state.game_config = {}
            st.session_state.game_code_parts = {}
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# 7. GPT-4 Master Chat (Main Command Center)
# -----------------------
st.markdown('<div class="premium-banner">⚡ ALPHA CORE COMMAND CENTER</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

final_q = st.chat_input("Enter command to Alpha Core...")

if final_q:
    st.session_state.messages.append({"role":"user","content":final_q})
    with st.chat_message("user"): st.markdown(final_q)
    
    with st.chat_message("assistant"):
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role":"system","content": "You are Alpha AI Ultimate. Master Software & Game Developer. Respond clearly in Sinhala."}] + st.session_state.messages
            )
            ans = response.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role":"assistant","content":ans})
        except Exception as e:
            st.error(f"Alpha API Disconnected: {e}")
