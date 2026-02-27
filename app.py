import streamlit as st
from groq import Groq
import uuid

# Page Configuration
st.set_page_config(page_title="☯ Alpha AI", page_icon="☯", layout="centered")

# --- Initialize Session States ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}  # Store all chat sessions {id: messages}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# Function to start a new chat
def start_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.all_chats[new_id] = []
    st.session_state.current_chat_id = new_id

# Start a default chat if none exists
if st.session_state.current_chat_id is None:
    start_new_chat()

# --- Sidebar - Chat Management ---
with st.sidebar:
    st.title("🤖 Alpha AI")
    st.write("**Creator:** Hasith")
    
    if st.button("➕ New Chat", use_container_width=True):
        start_new_chat()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🕒 Recent Chats")
    
    # Display chat history labels in sidebar
    for chat_id, messages in st.session_state.all_chats.items():
        # Label is the first user message or "New Chat"
        if messages:
            first_user_msg = next((m["content"] for m in messages if m["role"] == "user"), "Empty Chat")
            label = f"💬 {first_user_msg[:20]}..."
        else:
            label = "💬 New Chat"
        
        # If clicked, switch to that chat ID
        if st.button(label, key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

    st.markdown("---")
    if st.button("🗑 Clear All Chats", use_container_width=True):
        st.session_state.all_chats = {}
        st.session_state.current_chat_id = None
        start_new_chat()
        st.rerun()

# --- Main Interface ---
st.title("💥 Alpha AI")
st.info("Created by Hasith | Powered by Groq LPU™")

# Get current messages
current_messages = st.session_state.all_chats[st.session_state.current_chat_id]

# Display current chat history
for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Securely Access API Key
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_API_KEY)
except Exception:
    st.error("Please add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

# Handle Text Input
if prompt := st.chat_input("Ask Alpha anything..."):
    
    # Add user prompt to current session
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    try:
        with st.chat_message("assistant"):
            with st.spinner("Alpha is thinking..."):
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "You are Alpha, a professional AI assistant created by Hasith. "
                                "Your goal is to provide very meaningful and accurate responses "
                                "ONLY in simple Sinhala. Ensure every single letter is in Sinhala. "
                                "Do not mention image generation."
                            )
                        },
                        *[{"role": m["role"], "content": m["content"]} for m in current_messages]
                    ],
                    model="llama-3.3-70b-versatile",
                )
                
                response_text = chat_completion.choices[0].message.content
                st.markdown(response_text)
            
        # Save response to current history
        current_messages.append({"role": "assistant", "content": response_text})
        st.rerun()
        
    except Exception as e:
        st.error(f"Error: {e}")
