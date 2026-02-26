import streamlit as st
from groq import Groq

# Page Configuration
st.set_page_config(page_title="Alpha AI", page_icon="🤖", layout="centered")

# Sidebar for Creator Info and API Settings
with st.sidebar:
    st.title("Alpha AI")
    st.markdown("---")
    st.write("**Creator:** Hasith")
    st.write("**Powered by:** Groq LPU™")
    
    # Input for Groq API Key
    groq_api_key = st.text_input("Enter your Groq API Key:", type="password")
    
    # Button to clear history
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

st.title("🤖 Alpha AI")
st.info("Created by Hasith")

# 1. Initialize Chat History in Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Display existing Chat History (Old Messages)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Handle User Input
if prompt := st.chat_input("Ask Alpha anything..."):
    
    # Add user message to chat history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 4. Generate Response using Groq API
    if groq_api_key:
        try:
            client = Groq(api_key=groq_api_key)
            
            with st.chat_message("assistant"):
                # Sending full history so Alpha remembers previous context
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are Alpha, a professional AI assistant created by Hasith. You must be helpful and maintain the context of the conversation."
                        },
                        *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    ],
                    model="llama3-8b-8192",
                )
                
                full_response = chat_completion.choices[0].message.content
                st.markdown(full_response)
            
            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter your Groq API Key in the sidebar to start.")
