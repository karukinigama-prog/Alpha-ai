import streamlit as st
from openai import OpenAI
import asyncio

# --- 1. GitHub Models (Azure) Setup ---
# GPT-4 මාදිලිය සඳහා සබඳතාවය සැකසීම
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")

if GITHUB_TOKEN:
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=GITHUB_TOKEN,
    )
else:
    st.error("කරුණාකර ඔබගේ GITHUB_TOKEN එක Secrets වලට ඇතුළත් කරන්න.")
    st.stop()

# --- 2. UI Layout & Custom CSS ---
st.set_page_config(page_title="Alpha AI | GPT-4 Core", page_icon="⚡")
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    .status-msg { color: #FFD700; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Alpha Core: GPT-4 Intelligence")
st.markdown("---")

# --- 3. Chat Logic with Streaming ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# පෙර සංවාද පෙන්වීම
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Command Alpha (GPT-4 Active)...")

if user_input:
    # පරිශීලක පණිවිඩය ගබඩා කිරීම
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # GPT-4 හරහා Streaming පිළිතුර ලබා ගැනීම
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # මෙහිදී gpt-5-nano ඉවත් කර gpt-4 මාදිලිය ඇතුළත් කර ඇත
            stream = client.chat.completions.create(
                model="DeepSeek-R1", 
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
                    # සජීවීව අකුරු පෙන්වීම (Typing Effect)
                    response_placeholder.markdown(full_response + "▌")
            
            # සම්පූර්ණ පිළිතුර ස්ථාවරව පෙන්වීම
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("සටහන: ඔබගේ GitHub Marketplace අවසරයන් (Permissions) අනුව model name එක gpt-4o හෝ වෙනත් අනුමත නමකට වෙනස් විය හැක.")

st.write("---")
st.caption("Alpha AI v2.8 | Created by Hasith")
