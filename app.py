import streamlit as st
from groq import Groq

# Page Configuration
st.set_page_config(page_title="☯ Alpha AI", page_icon="☯", layout="centered")

# Sidebar - Creator Info
with st.sidebar:
    st.title("🤖 Alpha AI")
    st.markdown("---")
    st.write("**Creator:** Hasith")
    st.write("**Model:** Llama 3.3 70B")
    st.write("**Type:** Text Assistant")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

st.title("💥Alpha AI")
st.info("Created by Hasith | Powered by Groq LPU™")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Securely Access API Key
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error("Please add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

# Handle Text Input
if prompt := st.chat_input("Ask Alpha anything..."):
    
    # Add user prompt to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Text Response
    try:
        with st.chat_message("assistant"):
            # Added a loading spinner for a better UI experience
            with st.spinner("Alpha is thinking..."):
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are Alpha, a professional text-based AI assistant created by Hasith. You are powered by Llama 3.3 70B. Your goal is to provide accurate text responses in English. Do not mention image generation."
                        },
                        *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    ],
                    model="llama-3.3-70b-versatile",
                )
                
                response_text = chat_completion.choices[0].message.content
                st.markdown(response_text)
            
        # Save response to history
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
    except Exception as e:
        st.error(f"Error: {e}")
