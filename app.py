import streamlit as st
import os
from groq import Groq
from pydub import AudioSegment
import io

st.set_page_config(page_title="Vault Audio AI", page_icon="🎙️", layout="centered")
st.title("🎙️ Lightning Fast Audio-to-Text Converter")
st.caption("Created by Hasith | Powered by Groq Whisper Turbo")

with st.sidebar:
    st.header("⚙️ Settings")
    groq_api_key = st.text_input("Enter Groq API Key:", type="password")
    model_choice = st.selectbox(
        "Select Whisper Model:",
        ["whisper-large-v3-turbo", "whisper-large-v3"]
    )

uploaded_file = st.file_uploader(
    "Upload an Audio File (MP3, WAV, M4A, OGG, AMR)", 
    type=["mp3", "wav", "m4a", "ogg", "amr"]
)

if uploaded_file is not None:
    st.audio(uploaded_file)
    
    transcribe_btn = st.button("🚀 Transcribe Audio")
    
    if transcribe_btn:
        if not groq_api_key:
            st.error("Please enter your Groq API Key in the sidebar first!")
        else:
            with st.spinner("Converting & Transcribing..."):
                try:
                    client = Groq(api_key=groq_api_key)
                    
                    file_ext = uploaded_file.name.split(".")[-1].lower()
                    audio_bytes = uploaded_file.getbuffer()
                    
                    # AMR නම් MP3 එකට convert කරනවා
                    if file_ext == "amr":
                        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="amr")
                        converted = io.BytesIO()
                        audio.export(converted, format="mp3")
                        converted.seek(0)
                        send_bytes = converted.read()
                        send_name = "audio.mp3"
                    else:
                        send_bytes = bytes(audio_bytes)
                        send_name = uploaded_file.name
                    
                    transcription = client.audio.transcriptions.create(
                        file=(send_name, send_bytes),
                        model=model_choice,
                        response_format="text",
                        temperature=0.0
                    )
                    
                    st.success("⚡ Transcription Completed!")
                    st.text_area("📄 Transcribed Text:", value=transcription, height=300)
                    
                    st.download_button(
                        label="📥 Download Text File",
                        data=transcription,
                        file_name="transcription.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
