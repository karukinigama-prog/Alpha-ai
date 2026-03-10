import streamlit as st
from groq import Groq
from pathlib import Path
import os

# ---------------------------
# PAGE CONFIG
# ---------------------------

st.set_page_config(
    page_title="KITT AI SYSTEM",
    page_icon="🚗",
    layout="wide"
)

st.markdown(
"""
<style>
body {
background-color:black;
color:red;
}

.kitt-title{
text-align:center;
font-size:60px;
color:red;
font-weight:bold;
text-shadow:0px 0px 20px red;
}

</style>
""",
unsafe_allow_html=True
)

st.markdown('<div class="kitt-title">KITT AI SYSTEM</div>', unsafe_allow_html=True)

# ---------------------------
# GROQ CLIENT
# ---------------------------

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

# ---------------------------
# CHAT MEMORY
# ---------------------------

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role":"system","content":"You are KITT from Knight Rider. Speak smart and helpful."}
    ]

# ---------------------------
# USER INPUT
# ---------------------------

user_input = st.chat_input("Talk to KITT...")

if user_input:

    st.session_state.messages.append(
        {"role":"user","content":user_input}
    )

    # ---------------------------
    # GROQ AI RESPONSE
    # ---------------------------

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=st.session_state.messages
    )

    reply = completion.choices[0].message.content

    st.session_state.messages.append(
        {"role":"assistant","content":reply}
    )

    st.chat_message("assistant").write(reply)

    # ---------------------------
    # TEXT TO SPEECH
    # ---------------------------

    speech_path = Path("speech.wav")

    tts = client.audio.speech.create(
        model="elevenlabs-tts",
        voice="en_male_01",
        response_format="wav",
        input=reply
    )

    tts.stream_to_file(speech_path)

    audio_file = open(speech_path, "rb")
    st.audio(audio_file.read(), format="audio/wav")

# ---------------------------
# SHOW CHAT HISTORY
# ---------------------------

for msg in st.session_state.messages[1:]:
    st.chat_message(msg["role"]).write(msg["content"])

# ---------------------------
# SCANNER SOUND
# ---------------------------

scanner_path = "kitt_scanner.mp3"

if os.path.exists(scanner_path):
    audio_file = open(scanner_path, "rb")
    st.audio(audio_file.read(), format="audio/mp3")
