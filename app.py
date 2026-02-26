import streamlit as st
from groq import Groq

# Page Configuration
st.set_page_config(page_title="Alpha AI", page_icon="🚀", layout="wide")

# Sidebar Configuration
with st.sidebar:
    st.title("🤖 Alpha AI")
    st.markdown("---")
    st.write("**Creator:** Hasith")
    st.write("**Model:** Llama 3.3 70B (Versatile)")
    st.write("**Provider:** Groq LPU™")
    
    # Clear Chat History Button
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

st.title("Alpha AI")
st.caption("Developed by Hasith | Powered by Llama 3.3")

# 1. Initialize Chat History in Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Display Chat History (Shows previous messages)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Securely Access API Key from Streamlit Secrets
try:
    # Ensure you add GROQ_API_KEY to your Streamlit Cloud Secrets settings
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error("Missing API Key. Please add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

# 4. Handle Chat Input
if prompt := st.chat_input("How can Alpha help you today?"):
    
    # Append user prompt to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 5. Generate Response using Llama 3.3 70B
    try:
        with st.chat_message("assistant"):
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are Alpha, a highly intelligent AI assistant created by Hasith. You are powered by Llama 3.3 70B. Always respond in English and keep track of the conversation history."
                    },
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ],
                model="llama-3.3-70b-versatile", # The specific ID for Llama 3.3 on Groq
            )
            
            response_text = chat_completion.choices[0].message.content
            st.markdown(response_text)
            
        # Append Alpha's response to history
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
    except Exception as e:
        st.error(f"Groq API Error: {e}")
