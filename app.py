import streamlit as st
from groq import Groq
import time
import base64
import asyncio
import edge_tts
import webbrowser
import speech_recognition as sr
import requests
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup

# ======================================
# PAGE CONFIG
# ======================================

st.set_page_config(
page_title="Alpha AI | Next-Gen",
page_icon="⚡",
layout="wide"
)

# ======================================
# UI STYLE
# ======================================

st.markdown("""
<style>

.stApp{
background:#02050a;
color:white;
}

.alpha-title{
font-size:60px;
text-align:center;
font-weight:900;
letter-spacing:10px;
text-shadow:0 0 25px #00d4ff;
}

[data-testid="stSidebar"]{
background:#020913;
border-right:1px solid rgba(0,212,255,0.3);
}

.stButton>button{
border-radius:10px;
background:rgba(0,212,255,0.08);
border:1px solid rgba(0,212,255,0.2);
color:white;
}

.stButton>button:hover{
background:#00d4ff;
color:black;
box-shadow:0 0 15px #00d4ff;
}

.chat-box{
background:rgba(0,212,255,0.05);
padding:20px;
border-radius:20px;
border:1px solid rgba(0,212,255,0.2);
}

</style>
""", unsafe_allow_html=True)

# ======================================
# SESSION STATE
# ======================================

if "messages" not in st.session_state:
    st.session_state.messages=[]

if "memory" not in st.session_state:
    st.session_state.memory=[]

if "logged_in" not in st.session_state:
    st.session_state.logged_in=False

# ======================================
# LOADING SCREEN
# ======================================

if "loaded" not in st.session_state:

    loader=st.empty()

    for i in range(101):

        loader.markdown(
        f"<h3 style='text-align:center;color:#00d4ff'>Initializing Alpha Core {i}%</h3>",
        unsafe_allow_html=True
        )

        time.sleep(0.03)

    st.session_state.loaded=True
    st.rerun()

# ======================================
# LOGIN SYSTEM
# ======================================

if not st.session_state.logged_in:

    st.markdown("<h1 class='alpha-title'>ALPHA CORE</h1>",unsafe_allow_html=True)

    username=st.text_input("Operator")
    password=st.text_input("Master Key",type="password")

    if st.button("LOGIN"):

        if password=="Hasith12378":

            st.session_state.logged_in=True
            st.rerun()

        else:
            st.error("Access Denied")

    st.stop()

# ======================================
# VOICE SYSTEM
# ======================================

async def speak_alpha(text):

    voice="en-US-SteffanNeural"

    communicate=edge_tts.Communicate(text,voice)

    audio=b""

    async for chunk in communicate.stream():

        if chunk["type"]=="audio":

            audio+=chunk["data"]

    b64=base64.b64encode(audio).decode()

    st.markdown(
    f'<audio autoplay src="data:audio/mp3;base64,{b64}">',
    unsafe_allow_html=True
    )

# ======================================
# VOICE INPUT
# ======================================

def listen_voice():

    r=sr.Recognizer()

    with sr.Microphone() as source:

        st.info("Listening...")

        audio=r.listen(source)

    try:

        text=r.recognize_google(audio)

        return text

    except:

        return None

# ======================================
# FILE READER
# ======================================

def read_file(upload):

    if upload.name.endswith(".pdf"):

        reader=PdfReader(upload)

        text=""

        for page in reader.pages:

            text+=page.extract_text()

        return text[:4000]

    else:

        return upload.read().decode()

# ======================================
# INTERNET SEARCH
# ======================================

def internet_search(query):

    url=f"https://www.google.com/search?q={query}"

    headers={"User-Agent":"Mozilla/5.0"}

    r=requests.get(url,headers=headers)

    soup=BeautifulSoup(r.text,"html.parser")

    results=[]

    for g in soup.select("div.BNeawe")[:5]:

        results.append(g.text)

    return "\n".join(results)

# ======================================
# PLUGIN COMMANDS
# ======================================

def system_command(cmd):

    c=cmd.lower()

    if "youtube" in c:

        webbrowser.open("https://youtube.com")

        return "Opening YouTube"

    if "maps" in c:

        webbrowser.open("https://maps.google.com")

        return "Opening Google Maps"

    if "google" in c:

        webbrowser.open("https://google.com")

        return "Opening Google"

    return None

# ======================================
# GROQ AI
# ======================================

client=Groq(api_key=st.secrets["GROQ_API_KEY"])

def ask_ai(prompt,mode):

    memory="\n".join(st.session_state.memory[-5:])

    model="llama-3.3-70b-versatile"

    if mode=="GPT OSS 120B (Pro)":

        model="openai/gpt-oss-120b"

    messages=[
    {"role":"system","content":"You are Alpha AI created by Hasith."},
    {"role":"system","content":memory},
    {"role":"user","content":prompt}
    ]

    res=client.chat.completions.create(
    model=model,
    messages=messages
    )

    return res.choices[0].message.content

# ======================================
# SIDEBAR
# ======================================

with st.sidebar:

    st.markdown("## HASITH HESHAN")
    st.caption("System Architect")

    st.divider()

    mode=st.radio(
    "Intelligence Unit",
    ["Llama 3.3 (Normal)","GPT OSS 120B (Pro)"]
    )

    st.divider()

    st.subheader("AI Tools")

    voice_mode=st.toggle("🎤 Voice Chat")

    internet_mode=st.toggle("🌐 Internet Search")

    memory_mode=st.toggle("🧠 Memory")

    st.divider()

    uploaded=st.file_uploader("📂 Upload File")

    if uploaded:

        text=read_file(uploaded)

        st.session_state.memory.append(text)

        st.success("File loaded into memory")

    st.divider()

    if st.button("Clear Memory"):

        st.session_state.memory=[]

    if st.button("Log Out"):

        st.session_state.logged_in=False

        st.rerun()

# ======================================
# MAIN UI
# ======================================

st.markdown("<h1 class='alpha-title'>ALPHA AI</h1>",unsafe_allow_html=True)

st.markdown("<div class='chat-box'>",unsafe_allow_html=True)

# SHOW CHAT

for m in st.session_state.messages:

    with st.chat_message(m["role"]):

        st.markdown(m["content"])

# INPUT

user_input=None

if voice_mode:

    if st.button("🎤 Speak"):

        user_input=listen_voice()

else:

    user_input=st.chat_input("State command, Hasith...")

# PROCESS

if user_input:

    st.session_state.messages.append({"role":"user","content":user_input})

    with st.chat_message("user"):

        st.markdown(user_input)

    with st.chat_message("assistant"):

        plugin=system_command(user_input)

        if plugin:

            answer=plugin

        else:

            if internet_mode:

                web=internet_search(user_input)

                prompt=f"{user_input}\n\nInternet Data:\n{web}"

            else:

                prompt=user_input

            with st.spinner("Thinking..."):

                answer=ask_ai(prompt,mode)

        st.markdown(answer)

        asyncio.run(speak_alpha(answer))

        st.session_state.messages.append(
        {"role":"assistant","content":answer}
        )

        if memory_mode:

            st.session_state.memory.append(user_input)

st.markdown("</div>",unsafe_allow_html=True)
