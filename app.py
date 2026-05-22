import streamlit as st
from groq import Groq
import os
import random
import time

# ─── 1. පද්ධති සැකසුම් සහ UI (Page Configuration) ────────────────────────
st.set_page_config(
    page_title="Alpha Cyber-RPG",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── 2. සුපිරි CSS නිර්මාණය (Cyberpunk & Sci-Fi Theme) ─────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap');

:root {
    --bg-color: #050505;
    --neon-blue: #00f0ff;
    --neon-red: #ff003c;
    --neon-green: #39ff14;
    --text-main: #e0e0e0;
}

.stApp {
    background-color: var(--bg-color);
    background-image: 
        radial-gradient(circle at 15% 50%, rgba(0, 240, 255, 0.05), transparent 25%),
        radial-gradient(circle at 85% 30%, rgba(255, 0, 60, 0.05), transparent 25%);
    font-family: 'Rajdhani', sans-serif;
    color: var(--text-main);
}

.main-header {
    font-size: 3.5rem;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(90deg, var(--neon-blue), var(--neon-red));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-transform: uppercase;
    letter-spacing: 4px;
    margin-bottom: 0px;
    text-shadow: 0px 0px 20px rgba(0, 240, 255, 0.3);
}

.creator-tag {
    text-align: center;
    font-family: 'Share Tech Mono', monospace;
    color: var(--neon-green);
    font-size: 1rem;
    letter-spacing: 2px;
    margin-bottom: 30px;
    border-bottom: 1px solid rgba(57, 255, 20, 0.2);
    padding-bottom: 10px;
}

/* Stats Cards */
.stat-box {
    background: rgba(10, 10, 10, 0.8);
    border-left: 3px solid var(--neon-blue);
    padding: 15px;
    border-radius: 5px;
    font-family: 'Share Tech Mono', monospace;
    box-shadow: 0 4px 6px rgba(0,0,0,0.5);
    margin-bottom: 10px;
}

/* AI Story Box */
.story-container {
    background: rgba(15, 15, 20, 0.9);
    border: 1px solid rgba(0, 240, 255, 0.2);
    border-radius: 10px;
    padding: 25px;
    font-size: 1.2rem;
    line-height: 1.8;
    margin-bottom: 20px;
    box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
}

/* Custom Buttons */
.stButton>button {
    background: transparent !important;
    color: var(--neon-blue) !important;
    border: 1px solid var(--neon-blue) !important;
    border-radius: 0px !important;
    font-family: 'Share Tech Mono', monospace !important;
    text-transform: uppercase;
    transition: 0.3s !important;
    width: 100%;
}
.stButton>button:hover {
    background: var(--neon-blue) !important;
    color: #000 !important;
    box-shadow: 0 0 15px var(--neon-blue) !important;
}

.chat-user {
    color: var(--neon-green);
    font-family: 'Share Tech Mono', monospace;
    margin-bottom: 10px;
}
.chat-ai {
    color: #fff;
    margin-bottom: 20px;
    border-left: 2px solid var(--neon-red);
    padding-left: 15px;
}
</style>
""", unsafe_allow_html=True)

# ─── 3. Groq API සහ Llama 4 Scout සම්බන්ධ කිරීම ─────────────────────────
@st.cache_resource
def get_groq_client():
    # Streamlit Secrets වලින් හෝ Environment Variable එකෙන් API Key එක ගනී
    api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
    return Groq(api_key=api_key) if api_key else None

client = get_groq_client()
# මෙතන තමයි ඔබ ඉල්ලපු සුපිරි මොඩල් එක තියෙන්නේ!
AI_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct" 

# ─── 4. ගේම් එකේ මතකය (Session State Management) ───────────────────────
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
    st.session_state.player_stats = {
        "Name": "",
        "Class": "",
        "HP": 100,
        "XP": 0,
        "Level": 1,
        "Credits": 500,
        "Inventory": ["ඩිජිටල් සිතියම", "ප්‍රාථමික තුවක්කුව"]
    }
    st.session_state.story_log = []
    st.session_state.system_prompt = ""

# ─── 5. AI System Prompt (බුද්ධිය පාලනය කිරීම) ──────────────────────────
def generate_system_prompt():
    stats = st.session_state.player_stats
    return f"""ඔබ 'Alpha AI' පද්ධතිය මගින් බලගන්වන ලද අති නවීන Role-Playing Game (RPG) එකක Game Master වේ. 
ක්‍රීඩකයාගේ තොරතුරු:
- නම: {stats['Name']}
- පන්තිය: {stats['Class']}
- සෞඛ්‍යය (HP): {stats['HP']}
- මට්ටම (Level): {stats['Level']}
- භාණ්ඩ: {', '.join(stats['Inventory'])}

නීති:
1. සිංහල භාෂාවෙන් පමණක් අතිශය රසවත්, ක්‍රියාදාම පිරුණු කතාන්දරයක් ගොඩනගන්න.
2. ක්‍රීඩකයා ගන්නා තීරණ මත පරිසරය සහ සතුරන් වෙනස් කරන්න.
3. සෑම පිළිතුරක් අවසානයේම ක්‍රීඩකයාට ගත හැකි තීරණ 3ක් (Choices) අංක කර ලබා දෙන්න.
4. කතාව Cyberpunk / අනාගත ලෝකයකට අදාළව නිර්මාණය කරන්න."""

def get_ai_response(user_input):
    if not client:
        return "කරුණාකර GROQ_API_KEY එක Secrets වලට ඇතුළත් කරන්න."
    
    messages = [{"role": "system", "content": st.session_state.system_prompt}]
    
    # පරණ කතා ටිකත් AI එකට දෙනවා (මතකය තබා ගැනීමට)
    for log in st.session_state.story_log[-5:]: 
        messages.append({"role": log["role"], "content": log["text"]})
        
    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=messages,
            temperature=0.8,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"පද්ධතියේ දෝෂයකි: {str(e)}"

# ─── 6. ගේම් එකේ ප්‍රධාන අතුරුමුහුණත (Main UI) ──────────────────────────

st.markdown('<div class="main-header">ALPHA AI RPG</div>', unsafe_allow_html=True)
st.markdown('<div class="creator-tag">POWERED BY LLAMA 4 SCOUT | CREATED BY HASITH</div>', unsafe_allow_html=True)

# ගේම් එක පටන් අරන් නැත්නම් මුල් පිටුව පෙන්වන්න
if not st.session_state.game_active:
    with st.container():
        st.markdown("""
        <div class="story-container" style="text-align: center;">
            <h3>වර්ෂය 2145. ලෝකය තාක්ෂණයෙන් පාලනය වේ.</h3>
            <p>ඔබේ ගමන ආරම්භ කිරීමට පෙර ඔබේ අනන්‍යතාවය තහවුරු කරන්න.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        p_name = col1.text_input("ඔබේ නාමය (Player Name):")
        p_class = col2.selectbox("ඔබේ කුසලතාවය (Class):", ["Cyber-Hacker 💻", "Mecha-Warrior 🦾", "Stealth-Assassin 🥷"])
        
        if st.button("ගමන ආරම්භ කරන්න 🚀"):
            if p_name:
                st.session_state.player_stats["Name"] = p_name
                st.session_state.player_stats["Class"] = p_class
                st.session_state.system_prompt = generate_system_prompt()
                
                with st.spinner("Alpha AI ලෝකය ගොඩනගමින් පවතී..."):
                    first_prompt = "ගේම් එක ආරම්භ කරන්න. ක්‍රීඩකයා අඳුරු අනාගත නගරයක අවදි වන තැනින් කතාව පටන් ගන්න. විකල්ප 3ක් දෙන්න."
                    ai_reply = get_ai_response(first_prompt)
                    
                    st.session_state.story_log.append({"role": "user", "text": "ගේම් එක ආරම්භ විය."})
                    st.session_state.story_log.append({"role": "assistant", "text": ai_reply})
                    st.session_state.game_active = True
                    st.rerun()
            else:
                st.warning("කරුණාකර නමක් ඇතුළත් කරන්න!")

# ගේම් එක පටන් ගත්තට පස්සේ පෙනෙන කොටස
else:
    # Sidebar (Stats & Inventory)
    with st.sidebar:
        st.markdown("<h2 style='color:#00f0ff; text-align:center;'>පාලන මැදිරිය</h2>", unsafe_allow_html=True)
        stats = st.session_state.player_stats
        
        st.markdown(f"""
        <div class="stat-box">
            👤 නම: {stats['Name']}<br>
            ⚔️ පන්තිය: {stats['Class']}<br>
            ❤️ HP: {stats['HP']}/100<br>
            ⭐ Level: {stats['Level']} (XP: {stats['XP']})<br>
            💰 ණය: {stats['Credits']} Cr
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🎒 භාණ්ඩ (Inventory)")
        for item in stats['Inventory']:
            st.markdown(f"- {item}")
            
        st.markdown("---")
        if st.button("⚠️ පද්ධතිය රීසෙට් කරන්න"):
            st.session_state.game_active = False
            st.session_state.story_log = []
            st.rerun()

    # Story Area
    st.markdown("<div class='story-container'>", unsafe_allow_html=True)
    for log in st.session_state.story_log[-6:]: # අවසාන මැසේජ් 6 විතරක් පෙන්වයි
        if log["role"] == "user":
            st.markdown(f"<div class='chat-user'>▶ ඔබ: {log['text']}</div>", unsafe_allow_html=True)
        elif log["role"] == "assistant":
            st.markdown(f"<div class='chat-ai'>{log['text']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Action Input Area
    st.markdown("### ⚡ ඔබේ මීළඟ තීරණය කුමක්ද?")
    
    # කෝඩ් එකේ Loop එක නවත්තන්න Form එකක් පාවිච්චි කිරීම
    with st.form(key='action_form', clear_on_submit=True):
        col_input, col_btn = st.columns([4, 1])
        user_action = col_input.text_input("ඔබේ ක්‍රියාව මෙහි ලියන්න (උදා: '1' යතුරුලියනය කරන්න හෝ 'සතුරාට වෙඩි තබන්න')...", label_visibility="collapsed")
        submit_action = col_btn.form_submit_button("ක්‍රියාත්මක කරන්න ↵")
        
        if submit_action and user_action:
            # Stats පොඩ්ඩක් වෙනස් වීම (Random Events)
            if "වෙඩි" in user_action or "ප්‍රහාර" in user_action:
                st.session_state.player_stats["XP"] += 15
            
            st.session_state.story_log.append({"role": "user", "text": user_action})
            st.session_state.system_prompt = generate_system_prompt() # Stats යාවත්කාලීන කිරීම
            
            with st.spinner("Alpha AI ප්‍රතිචාර දක්වමින්..."):
                ai_reply = get_ai_response(user_action)
                st.session_state.story_log.append({"role": "assistant", "text": ai_reply})
            st.rerun()
