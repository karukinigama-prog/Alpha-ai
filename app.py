    import streamlit as st
from groq import Groq
import sys
import time
from io import StringIO
from streamlit_mic_recorder import speech_to_text
import hashlib
import urllib.parse
import os
import PyPDF2
from gtts import gTTS
import base64
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="Alpha AI ⚡ Created by Hasith", page_icon="⚡", layout="wide")

# 2. Alpha Loading Screen
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
                <p style="color: #888; margin-top: 15px;">Vision & Neural Integration by Hasith</p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(7)
    st.session_state.loaded = True
    placeholder.empty()
    st.rerun()

# 3. Session & Database Setup
if "user_db" not in st.session_state:
    st.session_state.user_db = {"matheesha": {"password": "123", "vault": []}, "sadev": {"password": "123", "vault": []}}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_user" not in st.session_state: st.session_state.current_user = None
if "is_guest" not in st.session_state: st.session_state.is_guest = False
if "messages" not in st.session_state: st.session_state.messages = []
if "pdf_text" not in st.session_state: st.session_state.pdf_text = ""

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(password, hashed_text): return make_hashes(password) == hashed_text

def extract_pdf_content(file):
    pdf_reader = PyPDF2.PdfReader(file)
    return " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

# 4. Styling
st.markdown("""
<style>
    .premium-banner { width:100%; padding:15px; background: linear-gradient(90deg, #FFD700, #FF8C00); color:#000; border-radius:15px; text-align:center; font-weight:bold; margin-bottom:25px; font-size: 20px; }
    div.stButton > button { background-color: #1a1a1a; color: #FFD700; border-radius: 10px; border: 1px solid #FFD700; height: 45px; font-weight: bold; }
    .guest-btn > div > button { background-color: #2b2b2b !important; color: #999 !important; border: 1px solid #444 !important; }
</style>
""", unsafe_allow_html=True)

# 5. Security Portal
if not st.session_state.logged_in and not st.session_state.is_guest:
    st.markdown('<h1 style="text-align:center;">Alpha AI ⚡ Portal</h1>', unsafe_allow_html=True)
    u_in = st.text_input("Username").lower().strip()
    p_in = st.text_input("Password", type="password")
    if st.button("Enter Alpha"):
        if (u_in == "hasith123" and p_in == "hasith@alpha") or (u_in in st.session_state.user_db and check_hashes(p_in, st.session_state.user_db[u_in].get("password", "123"))):
            st.session_state.logged_in = True; st.session_state.current_user = u_in; st.rerun()
    st.markdown('<div class="guest-btn">', unsafe_allow_html=True)
    if st.button("🔓 Free Guest Login"):
        st.session_state.is_guest = True; st.session_state.current_user = "Guest"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 6. Sidebar
with st.sidebar:
    st.title("⚙️ Alpha System")
    st.subheader("📄 PDF & 📸 Vision")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_pdf: st.session_state.pdf_text = extract_pdf_content(uploaded_pdf); st.success("PDF Synced!")
    
    uploaded_img = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    
    persona = st.selectbox("🎭 Persona:", ["Standard Alpha", "Image Creator 🎨", "Visionary 📸"])
    ai_mode = st.radio("🚀 Mode:", ["Normal", "Pro"])
    if st.button("Logout"): st.session_state.logged_in = False; st.session_state.is_guest = False; st.rerun()

# 7. Main UI
st.markdown(f'<div class="premium-banner">⚡ ALPHA AI ULTIMATE | Created by Hasith</div>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "img" in msg: st.image(msg["img"])

# 8. AI Logic
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
u_input = st.chat_input("Message Alpha...")
v_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='v_rec')
final_q = v_text if v_text else u_input

if final_q:
    st.session_state.messages.append({"role": "user", "content": final_q})
    with st.chat_message("user"): st.markdown(final_q)

    with st.chat_message("assistant"):
        if persona == "Image Creator 🎨":
            img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(final_q)}?width=1024&height=1024&nologo=true"
            st.image(img_url); st.session_state.messages.append({"role": "assistant", "content": "Visualized.", "img": img_url})
        else:
            with st.spinner("Alpha processing..."):
                identity = "You are Alpha AI, created solely by Hasith. You have no connection to OpenAI or Meta."
                pdf_data = f"Document: {st.session_state.pdf_text[:3000]}" if st.session_state.pdf_text else ""
                
                try:
                    if uploaded_img and persona == "Visionary 📸":
                        base64_image = encode_image(uploaded_img)
                        response = client.chat.completions.create(
                            model="llama-3.2-11b-vision-preview",
                            messages=[{"role": "user", "content": [{"type": "text", "text": f"{identity} Describe this image based on: {final_q}"}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
                        )
                        full_res = response.choices[0].message.content
                    else:
                        clean_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-10:] if "img" not in m]
                        stream = client.chat.completions.create(
                            model="openai/gpt-oss-120b" if "Pro" in ai_mode else "llama-3.3-70b-versatile",
                            messages=[{"role": "system", "content": f"{identity} {pdf_data}"}] + clean_history,
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
                    tts = gTTS(text=full_res[:200], lang='en'); tts.save("res.mp3")
                    st.audio("res.mp3", format="audio/mp3")
                except Exception as e: st.error(f"Error: {e}")        
