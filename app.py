import streamlit as st
import google.generativeai as genai
import uuid

# Page Configuration
st.set_page_config(page_title="☯ Alpha AI", page_icon="☯", layout="centered")

# --- Initialize Session States ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}  # Store multiple chat sessions

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# Function to start a new chat session
def start_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.all_chats[new_id] = []
    st.session_state.current_chat_id = new_id

# Ensure there is always an active chat session
if st.session_state.current_chat_id is None:
    start_new_chat()

# --- Google Gemini API Setup ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Model configuration for Gemini 2.5 Flash
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", # 
        system_instruction=(
            "You are Alpha, a professional AI assistant created by Hasith. "
            "Your goal is to provide very meaningful and accurate responses "
            "ONLY in simple Sinhala. Ensure every single letter is in Sinhala. "
            "Do not mention image generation."
        )
    )
except Exception as e:
    st.error("Please add GEMINI_API_KEY to your Streamlit Secrets.")
    st.stop()

# --- Sidebar - Chat Management (Gemini-like Experience) ---
with st.sidebar:
    st.title("🤖 Alpha AI")
    st.write("**Creator:** Hasith")
    st.write("**Model:** Gemini 2.5 Flash")
    
    if st.button("➕ New Chat", use_container_width=True):
        start_new_chat()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🕒 Recent Chats")
    
    # 
    for chat_id, messages in st.session_state.all_chats.items():
        if messages:
            # 
            first_msg = next((m["content"] for m in messages if m["role"] == "user"), "New Chat")
            label = f"💬 {first_msg[:25]}..."
        else:
            label = "💬 New Chat"
        
        # (Active State)
        is_active = (chat_id == st.session_state.current_chat_id)
        if st.button(label, key=chat_id, use_container_width=True, type="secondary" if not is_active else "primary"):
            st.session_state.current_chat_id = chat_id
            st.rerun()

    st.markdown("---")
    if st.button("🗑 Clear All History", use_container_width=True):
        st.session_state.all_chats = {}
        st.session_state.current_chat_id = None
        start_new_chat()
        st.rerun()

# --- Main Interface ---
st.title("💥 Alpha AI")
st.info("Created by Hasith | Powered by Google Gemini 2.5")

# Get history of the currently selected chat session
current_chat_history = st.session_state.all_chats[st.session_state.current_chat_id]

# Display current chat's conversation
for message in current_chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Handle User Input ---
if prompt := st.chat_input("සිංහලෙන් ඕනෑම දෙයක් අහන්න..."):
    
    # Save user message to current session
    current_chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response using Gemini 2.5 Flash
    try:
        with st.chat_message("assistant"):
            with st.spinner("Alpha සිතමින් පවතී..."):
                
                # Format current history for Gemini API
                gemini_history = [
                    {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                    for m in current_chat_history
                ]
                
                # Start chat with history (excluding the latest prompt)
                chat_session = model.start_chat(history=gemini_history[:-1])
                response = chat_session.send_message(prompt)
                
                response_text = response.text
                st.markdown(response_text)
            
        # Save response to current session history
        current_chat_history.append({"role": "assistant", "content": response_text})
        
        # Refresh to update sidebar labels instantly
        st.rerun()
        
    except Exception as e:
        st.error(f"Error: {e}")
