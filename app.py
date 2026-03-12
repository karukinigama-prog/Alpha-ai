from streamlit_mic_recorder import mic_recorder
import base64
import requests

def browser_voice_input():

    audio = mic_recorder(
        start_prompt="🎤 Start Recording",
        stop_prompt="⏹ Stop",
        just_once=True,
        key="recorder"
    )

    if audio:
        st.audio(audio["bytes"])

        # speech to text using whisper API
        headers = {
            "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"
        }

        files = {
            "file": ("audio.wav", audio["bytes"], "audio/wav")
        }

        data = {
            "model": "whisper-large-v3"
        }

        response = requests.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers=headers,
            files=files,
            data=data
        )

        text = response.json()["text"]

        return text

    return None
