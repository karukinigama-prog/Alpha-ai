import streamlit as st
import os
from groq import Groq

# 1. UI සැකසුම (Modern Dark/Metallic Theme)
st.set_page_config(page_title="Vault Audio AI", page_icon="🎙️", layout="centered")
st.title("🎙️ Lightning Fast Audio-to-Text Converter")
st.caption("Created by Hasith | Powered by Groq Whisper Turbo")

# Sidebar එකේ API Key එක ඇතුළත් කිරීමට
with st.sidebar:
    st.header("⚙️ Settings")
    groq_api_key = st.text_input("Enter Groq API Key:", type="password")
    
    # Whisper වල හොඳම Models දෙක තෝරාගැනීමට
    model_choice = st.selectbox(
        "Select Whisper Model:",
        ["whisper-large-v3-turbo", "whisper-large-v3"]
    )
    st.info("💡 'Turbo' model එක වේගයෙන්ම වැඩ කරන අතර, 'Large V3' එක සංකීර්ණ වචන වඩාත් නිවැරදිව හඳුනාගනී.")

# 2. File Upload Area
uploaded_file = st.file_uploader(
    "Upload an Audio File (MP3, WAV, M4A, OGG, AMR)", 
    type=["mp3", "wav", "m4a", "ogg", "amr"]
)


# 3. Processing Core Logic
if uploaded_file is not None:
    # පරිශීලකයාට ඕඩියෝ එක Play කරලා බලන්න දෙනවා
    st.audio(uploaded_file, format="audio/mp3")
    
    transcribe_btn = st.button("🚀 Transcribe Audio")
    
    if transcribe_btn:
        if not groq_api_key:
            st.error("Please enter your Groq API Key in the sidebar first!")
        else:
            with st.spinner("Groq LPU Engine is transcribing at extreme speed..."):
                try:
                    # Groq Client එක Initialize කිරීම
                    client = Groq(api_key=groq_api_key)
                    
                    # Upload කරපු file එක තාවකාලිකව save කරගැනීම (Groq API එකට File Object එකක් දීමට)
                    with open("temp_audio.mp3", "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # ඇත්තම Audio File එක open කරලා Groq API එකට යැවීම
                    with open("temp_audio.mp3", "rb") as audio_file:
                        transcription = client.audio.transcriptions.create(
                            file=("temp_audio.mp3", audio_file.read()),
                            model=model_choice,
                            response_format="text", # Text විදිහට කෙලින්ම ගන්නවා
                            temperature=0.0         # 0.0 දුන්නම නිවැරදිභාවය වැඩියි
                        )
                    
                    # සාර්ථක වුණොත් ප්‍රතිඵලය පෙන්වීම
                    st.success("⚡ Transcription Completed in Seconds!")
                    
                    # Text Box එකක් ඇතුලේ Text එක ලස්සනට පෙන්වීම
                    st.text_area("📄 Transcribed Text:", value=transcription, height=300)
                    
                    # 4. Export Feature (Download Button)
                    st.download_button(
                        label="📥 Download Text File",
                        data=transcription,
                        file_name="vault_transcription.txt",
                        mime="text/plain"
                    )
                    
                    # වැඩේ ඉවර වුණාම තාවකාලික File එක Delete කිරීම
                    if os.path.exists("temp_audio.mp3"):
                        os.remove("temp_audio.mp3")
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
