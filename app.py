import streamlit as st
from openai import OpenAI
import asyncio

# --- 1. GitHub Models (Azure) Setup ---
# ඔබ ලබා දුන් ලින්ක් එකට අනුව gpt-5-nano මාදිලිය ක්‍රියාත්මක කිරීම සඳහා
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")

if GITHUB_TOKEN:
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=GITHUB_TOKEN,
    )
else:
    st.error("කරුණාකර ඔබගේ GITHUB_TOKEN එක Secrets වලට ඇතුළත් කරන්න.")
    st.stop()

# --- 2. UI Styling ---
st.set_page_config(page_title="Alpha AI | GPT-5 Nano", page_icon="⚡")
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    .chat-container { border: 1px solid #FFD700; padding: 20px; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Alpha Core: GPT-5-Nano Testing Lab")
st.info("Https://github.com/marketplace/models/azure-openai/gpt-5-nano හරහා සෘජුවම සම්බන්ධ වේ.")

# --- 3. Chat Logic with Streaming ---
if "nano_messages" not in st.session_state:
    st.session_state.nano_messages = []

# පවතින පණිවිඩ පෙන්වීම
for msg in st.session_state.nano_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Command Alpha (GPT-5 Nano)...")

if user_input:
    # පරිශීලක පණිවිඩය එකතු කිරීම
    st.session_state.nano_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # GPT-5 Nano හරහා Streaming පිළිතුර ලබා ගැනීම
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # ඔබ ඉල්ලූ gpt-5-nano මාදිලිය මෙතැනට යොදා ඇත
            stream = client.chat.completions.create(
                model="gpt-5-nano", 
                messages=[
                    {"role": "system", "content": "ඔබ හසිත් කරුණාරත්න විසින් නිර්මාණය කළ Alpha AI වේ. සරලව පිළිතුරු දෙන්න."},
                    {"role": "user", "content": user_input}
                ],
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_response += token
                    # සජීවීව පෙන්වීම (Streaming Effect)
                    response_placeholder.markdown(full_response + "▌")
            
            # අවසාන පණිවිඩය ස්ථාවරව පෙන්වීම
            response_placeholder.markdown(full_response)
            st.session_state.nano_messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"දෝෂයක් පවතී: {str(e)}")
            st.warning("සටහන: gpt-5-nano මාදිලියට ඔබගේ GitHub ගිණුමට තවමත් අවසර (Access) ලැබී නොමැති නම් මෙය ක්‍රියා නොකරනු ඇත.")

st.write("---")
st.caption("Created by Hasith | Alpha AI v2.8 (Experimental)")
