import streamlit as st
from groq import Groq
import time
import base64
import asyncio
import edge_tts
from PyPDF2 import PdfReader

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="KITT AI",
    page_icon="🏎️",
    layout="wide"
)

# ---------------- STYLE ----------------

st.markdown("""
<style>

.stApp{
background: radial-gradient(circle at center,#050505,#000000);
color:white;
font-family:Courier New;
}

.glass-banner{
background:rgba(255,0,0,0.08);
backdrop-filter:blur(12px);
border:1px solid rgba(255,0,0,0.4);
padding:18px;
border-radius:12px;
text-align:center;
margin-bottom:15px;
}

.status-bar{
background:#0a0a0a;
padding:10px;
border-left:4px solid red;
color:#888;
margin-bottom:20px;
}

.loader{
display:flex;
flex-direction:column;
align-items:center;
justify-content:center;
height:90vh;
}

.kitt{
font-size:70px;
color:red;
text-shadow:0 0 25px red;
font-weight:bold;
letter-spacing:6px;
}

.scan{
width:350px;
height:12px;
background:#111;
border-radius:8px;
overflow:hidden;
margin-top:25px;
}

.light{
width:120px;
height:100%;
background:linear-gradient(90deg,transparent,red,transparent);
box-shadow:0 0 25px red;
position:relative;
animation:scan 1.2s infinite alternate;
}

@keyframes scan{
0%{left:-10%;}
100%{left:85%;}
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOADER ----------------

if "loaded" not in st.session_state:

    loader = st.empty()

    with loader.container():

        st.markdown("""
        <div class="loader">

        <div class="kitt">KITT INITIALIZING</div>

        <div class="scan">
        <div class="light"></div>
        </div>

        <br>

        MEMORY CHECK : OK <br>
        CPU STATUS : STABLE <br>
        SAT COM : CONNECTED

        </div>
        """, unsafe_allow_html=True)

        time.sleep(4)

    st.session_state.loaded=True
    st.rerun()

# ---------------- USER DATABASE ----------------

if "user_db" not in st.session_state:
    st.session_state.user_db={
        "matheesha":"123",
        "sadev":"123"
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in=False

# ---------------- LOGIN PAGE ----------------

if not st.session_state.logged_in:

    st.markdown('<div class="glass-banner"><h1>KITT SECURITY PORTAL</h1></div>',unsafe_allow_html=True)

    tab1,tab2,tab3 = st.tabs(["LOGIN","REGISTER","CREATOR"])

    with tab1:

        u=st.text_input("USER ID").lower()
        p=st.text_input("PASSWORD",type="password")

        if st.button("LOGIN"):

            if u in st.session_state.user_db and st.session_state.user_db[u]==p:

                st.session_state.logged_in=True
                st.session_state.user=u
                st.rerun()

            else:
                st.error("ACCESS DENIED")

    with tab2:

        newu=st.text_input("NEW USER")
        newp=st.text_input("NEW PASSWORD",type="password")

        if st.button("CREATE ACCOUNT"):

            st.session_state.user_db[newu]=newp
            st.success("ACCOUNT CREATED")

    with tab3:

        key=st.text_input("MASTER KEY",type="password")

        if st.button("OVERRIDE"):

            if key=="Hasith12378":

                st.session_state.logged_in=True
                st.session_state.user="Hasith"
                st.rerun()

            else:
                st.error("INVALID KEY")

    st.stop()

# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.title("DIAGNOSTICS")

    mode=st.radio("AI CORE",[
        "Normal Mode",
        "Pro Mode"
    ])

    doc=st.file_uploader("UPLOAD DATA",type=["pdf","txt"])

    extracted=""

    if doc:

        if doc.type=="application/pdf":

            reader=PdfReader(doc)

            for p in reader.pages:
                extracted+=p.extract_text()

        else:
            extracted=doc.getvalue().decode()

    if st.button("SHUTDOWN"):

        st.session_state.logged_in=False
        st.rerun()

# ---------------- DASHBOARD ----------------

st.markdown(f"""
<div class="glass-banner">

KITT SYSTEM ONLINE

AUTHORIZED USER : {st.session_state.user}

</div>
""",unsafe_allow_html=True)

st.markdown("""
<div class="status-bar">

AI CORE : ACTIVE <br>
POWER : 98% <br>
NETWORK : CONNECTED

</div>
""",unsafe_allow_html=True)

# ---------------- GROQ CLIENT ----------------

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

# ---------------- CHAT MEMORY ----------------

if "messages" not in st.session_state:

    st.session_state.messages=[{
        "role":"assistant",
        "content":"Hello there, I'm KITT. How can I help you today?"
    }]

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

    try:

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=st.session_state.messages
        )

        reply = completion.choices[0].message.content

    except Exception:

        reply="KITT AI CORE ERROR"

    st.session_state.messages.append({
        "role":"assistant",
        "content":reply
    })

    st.chat_message("assistant").write(reply)

# ---------------- VOICE ----------------

async def speak(text):

    voice="en-IE-ConnorNeural"

    communicate=edge_tts.Communicate(text,voice)

    audio=b""

    async for chunk in communicate.stream():

        if chunk["type"]=="audio":
            audio+=chunk["data"]

    return audio

if prompt:

    audio_data=asyncio.run(speak(reply))

    b64=base64.b64encode(audio_data).decode()

    st.markdown(
        f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>',
        unsafe_allow_html=True
    )
