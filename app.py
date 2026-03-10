import streamlit as st
from groq import Groq
from elevenlabs.client import ElevenLabs
import base64
import time

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="KITT AI",
    page_icon="🚗",
    layout="wide"
)

# ---------------- KITT STYLE ----------------

st.markdown("""
<style>

.stApp{
background:black;
color:white;
font-family:Courier New;
}

.title{
text-align:center;
font-size:60px;
color:red;
text-shadow:0 0 20px red;
margin-bottom:20px;
}

.scanner{
width:420px;
height:14px;
background:#111;
margin:auto;
border-radius:10px;
overflow:hidden;
margin-bottom:30px;
}

.scan-light{
width:120px;
height:100%;
background:linear-gradient(90deg,transparent,red,transparent);
box-shadow:0 0 25px red;
position:relative;
animation:scan 1.2s infinite alternate;
}

@keyframes scan{
0%{left:-10%;}
100%{left:90%;}
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------

st.markdown('<div class="title">KITT AI SYSTEM</div>', unsafe_allow_html=True)

# ---------------- SCANNER ----------------

st.markdown("""
<div class="scanner">
<div class="scan-light"></div>
</div>
""", unsafe_allow_html=True)

# ---------------- PLAY SCANNER SOUND ----------------

def play_scan_sound():
    with open("kitt_scanner.mp3", "rb") as f:
        audio = f.read()

    b64 = base64.b64encode(audio).decode()

    st.markdown(
        f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>',
        unsafe_allow_html=True
    )

play_scan_sound()

# ---------------- GROQ AI ----------------

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

# ---------------- ELEVENLABS VOICE ----------------

eleven = ElevenLabs(
    api_key=st.secrets["ELEVEN_API_KEY"]
)

# ---------------- CHAT MEMORY ----------------

if "messages" not in st.session_state:

    st.session_state.messages = [
        {
        "role":"assistant",
        "content":"Hello there, I'm KITT. මම KITT AI. How can I help you today?"
        }
    ]

# ---------------- SHOW CHAT ----------------

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

prompt = st.chat_input("Talk with KITT...")

# ---------------- AI RESPONSE ----------------

if prompt:

    st.session_state.messages.append({
        "role":"user",
        "content":prompt
    })

    st.chat_message("user").write(prompt)

    completion = client.chat.completions.create(
        model="gpt-oss-120b",
        messages=st.session_state.messages
    )

    reply = completion.choices[0].message.content

    st.session_state.messages.append({
        "role":"assistant",
        "content":reply
    })

    st.chat_message("assistant").write(reply)

# ---------------- VOICE OUTPUT ----------------

    audio = eleven.generate(
        text=reply,
        voice="Adam"
    )

    st.audio(audio)
