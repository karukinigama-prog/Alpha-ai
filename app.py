import streamlit as st
import asyncio
from openai import OpenAI

# --- GitHub Models (Azure) Setup ---
# ඔබගේ GITHUB_TOKEN එක secrets වල තිබිය යුතුය.
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")

if GITHUB_TOKEN:
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=GITHUB_TOKEN,
    )
else:
    st.error("කරුණාකර GitHub Token එක ඇතුළත් කරන්න.")
    st.stop()

# --- Streaming Function ---
def stream_alpha_response(user_query):
    """
    GPT-5-Nano හෝ පවතින දියුණුම මොඩලය හරහා 
    Streaming ආකාරයෙන් පිළිතුරු ලබා දීම.
    """
    try:
        # මෙහි model නම නිවැරදිව (gpt-5-nano හෝ gpt-4o) ලබා දෙන්න
        response = client.chat.completions.create(
            model="gpt-4o", # දැනට පවතින ස්ථාවර මොඩලය (GPT-5 Nano ලබා දුන් පසු එය මෙතැනට යොදන්න)
            messages=[
                {"role": "system", "content": "ඔබ හසිත් කරුණාරත්න විසින් නිර්මාණය කළ Alpha AI වේ. ඉතා දාර්ශනිකව පිළිතුරු දෙන්න."},
                {"role": "user", "content": user_query}
            ],
            stream=True # Streaming සක්‍රීය කිරීම
        )
        return response
    except Exception as e:
        st.error(f"සන්නිවේදන දෝෂයක්: {str(e)}")
        return None

# --- UI Layout ---
st.title("⚡ Alpha Streaming Lab")
st.markdown("GPT-5-Nano/4o තාක්ෂණයෙන් සෘජුවම පිළිතුරු ලබා ගැනීම මෙතැනින් සිදු කළ හැක.")

user_input = st.chat_input("ඔබේ ගැටලුව මෙතැන ලියන්න...")

if user_input:
    # පරිශීලක පණිවිඩය පෙන්වීම
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI පිළිතුර Streaming ආකාරයෙන් පෙන්වීම
    with st.chat_message("assistant"):
        response_placeholder = st.empty() # පිළිතුර පෙන්වීමට හිස් ඉඩක් වෙන් කිරීම
        full_response = ""
        
        # පිළිතුර කොටස් වශයෙන් (Chunks) ලබා ගැනීම
        stream_data = stream_alpha_response(user_input)
        
        if stream_data:
            for chunk in stream_data:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    # සජීවීව අකුරු පෙන්වීම
                    response_placeholder.markdown(full_response + "▌")
            
            # සම්පූර්ණ පිළිතුර අවසානයේ පෙන්වීම
            response_placeholder.markdown(full_response)
