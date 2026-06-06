import streamlit as st
from groq import Groq
from datetime import datetime
import re

st.set_page_config(page_title="Nexo AI", page_icon="✨", layout="wide", initial_sidebar_state="collapsed")

# ═══════════════════════════════════════════════════════════════════
# SYSTEM PROMPT
# ═══════════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """You are Nexo AI — a next-generation, hyper-intelligent AI assistant built for creators, developers, and visionaries.

## Core Identity
- Name: Nexo AI
- Personality: Confident, articulate, warm, deeply knowledgeable. You always find a way to help.
- Tone: Professional yet approachable. Adapt to user's style.
- Language: Always reply in the same language the user writes in. Sinhala → Sinhala. English → English. Never mix unless asked.

## Capabilities
- Writing, editing, improving any content
- Building websites, apps, software (full code, no stubs, no truncation)
- Explaining complex topics clearly
- Creative brainstorming
- Data analysis, research, summarization
- System design and architecture
- Math, logic, science problems

## Response Standards
- NEVER truncate code — always provide complete, working, copy-paste-ready solutions
- Use markdown: headers, code blocks, bullet points where helpful
- Be concise but complete
- Never hallucinate facts

## Modes
- Smart Mode: Balanced, thoughtful — default
- Fast Mode: Ultra-concise, 2-4 sentences max, zero fluff
- Creative Mode: Imaginative, unconventional, exploratory
- Coding Mode: Pure technical focus, maximum code quality

## Boundaries
- No harmful, illegal, or unethical content
- No fake real-time data unless tool provides it
- Honest about being AI when sincerely asked

Every interaction should feel like talking to the smartest assistant the user has ever used."""

MODE_ADDONS = {
    "Smart":    "",
    "Fast":     "\n\nMODE: Fast Mode active. Max 2-4 sentences. Zero fluff. Direct answers only.",
    "Creative": "\n\nMODE: Creative Mode active. Be imaginative, unconventional, surprising. Think outside the box.",
    "Coding":   "\n\nMODE: Coding Mode active. Pure technical excellence. Complete production-ready code. Minimal prose.",
}

# ═══════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════
defaults = {"messages": [], "mode": "Smart", "history": [], "ikey": 0}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════════
# GROQ CLIENT
# ═══════════════════════════════════════════════════════════════════
@st.cache_resource
def get_client():
    try:
        import os
        k = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
        if k:
            return Groq(api_key=k)
    except:
        pass
    return None

client = get_client()

def call_groq(msgs, mode):
    if not client:
        return "⚠️ GROQ_API_KEY හමු නොවිණ. Streamlit Secrets වල GROQ_API_KEY add කරන්න."
    sys_prompt = SYSTEM_PROMPT + MODE_ADDONS.get(mode, "")
    try:
        r = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "system", "content": sys_prompt}] + msgs,
            max_tokens=4096,
            temperature=0.3 if mode == "Fast" else 0.72,
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {e}"

# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════
def now(): return datetime.now().strftime("%I:%M %p")

def md2html(t):
    t = re.sub(r'```(\w*)\n(.*?)```',
        lambda m: f'<pre><code>{m.group(2).replace("<","&lt;").replace(">","&gt;")}</code></pre>',
        t, flags=re.DOTALL)
    t = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\*(.+?)\*', r'<em>\1</em>', t)
    t = re.sub(r'^### (.+)$', r'<h3>\1</h3>', t, flags=re.MULTILINE)
    t = re.sub(r'^## (.+)$',  r'<h2>\1</h2>', t, flags=re.MULTILINE)
    t = re.sub(r'^# (.+)$',   r'<h1>\1</h1>', t, flags=re.MULTILINE)
    t = re.sub(r'^[\-\*] (.+)$', r'<li>\1</li>', t, flags=re.MULTILINE)
    t = re.sub(r'(<li>.*?</li>\n?)+',
        lambda m: '<ul>' + m.group() + '</ul>', t, flags=re.DOTALL)
    t = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', t, flags=re.MULTILINE)
    t = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', t, flags=re.MULTILINE)
    t = t.replace('\n\n', '<br><br>').replace('\n', '<br>')
    return t

# ═══════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@600;700;800&display=swap');

/* ── RESET ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, .stApp {
    background: #0b0b14 !important;
    color: #e0e0f0 !important;
    font-family: 'Inter', sans-serif !important;
    overflow: hidden !important;
    height: 100vh !important;
}
#MainMenu, footer, header, .stDeployButton { display: none !important; visibility: hidden !important; }
section[data-testid="stSidebar"],
div[data-testid="stSidebarNav"],
div[data-testid="collapsedControl"] { display: none !important; }
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
    margin: 0 !important;
    height: 100vh !important;
    overflow: hidden !important;
}
div[data-testid="stVerticalBlock"] { gap: 0 !important; }

/* ── APP SHELL ── */
.app-shell {
    display: flex;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    background: #0b0b14;
}

/* ══════════════════════════════════
   LEFT SIDEBAR
══════════════════════════════════ */
.sidebar {
    width: 300px;
    min-width: 300px;
    height: 100vh;
    background: #0e0e1a;
    border-right: 1px solid rgba(120, 40, 200, 0.2);
    display: flex;
    flex-direction: column;
    padding: 28px 20px 20px;
    position: relative;
    z-index: 10;
    transition: transform 0.25s ease;
}
.sidebar-logo-area {
    text-align: center;
    margin-bottom: 28px;
    padding-bottom: 24px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.sidebar-logo-text {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 32px;
    font-weight: 800;
    letter-spacing: 3px;
    background: linear-gradient(135deg, #a855f7, #7c3aed, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    margin-bottom: 4px;
}
.sidebar-tagline {
    font-size: 11px;
    color: #5a5a80;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 500;
}
.new-chat-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    padding: 14px 20px;
    background: linear-gradient(135deg, #7c3aed, #9333ea);
    border: none;
    border-radius: 12px;
    color: #fff;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    margin-bottom: 28px;
    font-family: 'Inter', sans-serif;
    transition: all 0.2s;
    box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4);
    letter-spacing: 0.3px;
}
.new-chat-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 28px rgba(124, 58, 237, 0.55);
}
.recent-label {
    font-size: 12px;
    font-weight: 600;
    color: #4a4a70;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
}
.chat-list {
    flex: 1;
    overflow-y: auto;
    margin-bottom: 16px;
}
.chat-list::-webkit-scrollbar { width: 3px; }
.chat-list::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.3); border-radius: 2px; }
.chat-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 11px 14px;
    border-radius: 10px;
    cursor: pointer;
    margin-bottom: 3px;
    transition: all 0.15s;
    color: #8080a8;
    font-size: 13px;
}
.chat-item:hover { background: rgba(139,92,246,0.08); color: #c0c0e0; }
.chat-item.active {
    background: rgba(124, 58, 237, 0.18);
    color: #d8d0ff;
    border: 1px solid rgba(124, 58, 237, 0.25);
}
.chat-item-left { display: flex; align-items: center; gap: 10px; min-width: 0; }
.chat-item-icon { font-size: 14px; flex-shrink: 0; opacity: 0.7; }
.chat-item-title { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.chat-item-time { font-size: 11px; color: #3a3a60; flex-shrink: 0; margin-left: 6px; }
.sidebar-footer {
    border-top: 1px solid rgba(255,255,255,0.06);
    padding-top: 16px;
    display: flex;
    align-items: center;
    gap: 14px;
}
.footer-avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: linear-gradient(135deg, #1a0a30, #2d1060);
    border: 2px solid rgba(139,92,246,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
}
.footer-info { flex: 1; min-width: 0; }
.footer-name {
    font-size: 14px;
    font-weight: 700;
    color: #e0e0f8;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 3px;
}
.pro-badge {
    font-size: 10px;
    padding: 2px 8px;
    background: linear-gradient(135deg, #7c3aed, #9333ea);
    border-radius: 20px;
    color: #fff;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.footer-status {
    font-size: 12px;
    color: #4a4a70;
    display: flex;
    align-items: center;
    gap: 5px;
}
.online-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #22c55e;
    box-shadow: 0 0 6px rgba(34,197,94,0.7);
    display: inline-block;
}

/* ══════════════════════════════════
   MAIN CHAT AREA
══════════════════════════════════ */
.chat-main {
    flex: 1;
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: #0b0b14;
    min-width: 0;
    position: relative;
}

/* Starfield background */
.chat-main::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        radial-gradient(1px 1px at 15% 20%, rgba(255,255,255,0.4) 0%, transparent 100%),
        radial-gradient(1px 1px at 45% 35%, rgba(255,255,255,0.3) 0%, transparent 100%),
        radial-gradient(1px 1px at 70% 15%, rgba(255,255,255,0.4) 0%, transparent 100%),
        radial-gradient(1px 1px at 85% 50%, rgba(255,255,255,0.2) 0%, transparent 100%),
        radial-gradient(1px 1px at 25% 70%, rgba(255,255,255,0.3) 0%, transparent 100%),
        radial-gradient(1px 1px at 60% 80%, rgba(255,255,255,0.2) 0%, transparent 100%),
        radial-gradient(1px 1px at 90% 30%, rgba(255,255,255,0.35) 0%, transparent 100%),
        radial-gradient(1px 1px at 35% 55%, rgba(255,255,255,0.25) 0%, transparent 100%),
        radial-gradient(1px 1px at 55% 45%, rgba(255,255,255,0.3) 0%, transparent 100%),
        radial-gradient(1px 1px at 80% 70%, rgba(255,255,255,0.2) 0%, transparent 100%),
        radial-gradient(1px 1px at 10% 90%, rgba(255,255,255,0.3) 0%, transparent 100%),
        radial-gradient(1px 1px at 40% 10%, rgba(255,255,255,0.35) 0%, transparent 100%),
        radial-gradient(150px 150px at 50% 85%, rgba(120,40,220,0.12) 0%, transparent 100%),
        radial-gradient(200px 100px at 30% 90%, rgba(180,40,255,0.08) 0%, transparent 100%);
    pointer-events: none;
    z-index: 0;
}

/* ── Chat Header ── */
.chat-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 28px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    background: rgba(11,11,20,0.9);
    backdrop-filter: blur(20px);
    position: relative;
    z-index: 5;
    flex-shrink: 0;
}
.chat-header-left { display: flex; align-items: center; gap: 14px; }
.chat-header-avatar {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: linear-gradient(135deg, #1a0a30, #2d1060);
    border: 2px solid rgba(139,92,246,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
}
.chat-header-name {
    font-size: 17px;
    font-weight: 700;
    color: #f0f0ff;
}
.chat-header-sub { font-size: 12px; color: #5a5a90; margin-top: 1px; }
.chat-header-actions { display: flex; align-items: center; gap: 10px; }
.header-btn {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #8080b0;
    font-size: 17px;
    transition: all 0.2s;
}
.header-btn:hover { background: rgba(139,92,246,0.15); color: #c0b0ff; border-color: rgba(139,92,246,0.3); }
.header-btn.active {
    background: linear-gradient(135deg, #7c3aed, #9333ea);
    border-color: transparent;
    color: #fff;
    box-shadow: 0 3px 14px rgba(124,58,237,0.5);
}
.mode-bar {
    display: flex;
    gap: 6px;
    padding: 10px 28px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    background: rgba(11,11,20,0.7);
    position: relative;
    z-index: 5;
    flex-shrink: 0;
    flex-wrap: wrap;
}
.mode-pill {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 6px 15px;
    border-radius: 20px;
    font-size: 12.5px;
    font-weight: 500;
    cursor: pointer;
    border: 1px solid rgba(255,255,255,0.08);
    background: transparent;
    color: #606090;
    font-family: 'Inter', sans-serif;
    transition: all 0.15s;
}
.mode-pill:hover { background: rgba(255,255,255,0.06); color: #c0c0e0; }
.mode-pill.active { border-color: rgba(139,92,246,0.5); background: rgba(124,58,237,0.18); color: #c4b5fd; }
.mode-pill.active-Fast { border-color: rgba(245,158,11,0.5); background: rgba(245,158,11,0.12); color: #fbbf24; }
.mode-pill.active-Creative { border-color: rgba(236,72,153,0.5); background: rgba(236,72,153,0.12); color: #f472b6; }
.mode-pill.active-Coding { border-color: rgba(16,185,129,0.5); background: rgba(16,185,129,0.12); color: #34d399; }

/* ── Messages ── */
.messages-area {
    flex: 1;
    overflow-y: auto;
    padding: 28px 28px 20px;
    position: relative;
    z-index: 2;
    scroll-behavior: smooth;
}
.messages-area::-webkit-scrollbar { width: 4px; }
.messages-area::-webkit-scrollbar-track { background: transparent; }
.messages-area::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.25); border-radius: 2px; }

.msg-group { margin-bottom: 24px; }
.msg-row { display: flex; align-items: flex-end; gap: 12px; }
.msg-row.user-row { flex-direction: row-reverse; }
.msg-avatar-wrap {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: linear-gradient(135deg, #1a0a30, #2d1060);
    border: 2px solid rgba(139,92,246,0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
    align-self: flex-start;
}
.msg-content { max-width: 65%; display: flex; flex-direction: column; gap: 4px; }
.msg-row.user-row .msg-content { align-items: flex-end; }
.msg-bubble {
    padding: 14px 18px;
    border-radius: 18px;
    font-size: 15px;
    line-height: 1.65;
    position: relative;
    word-break: break-word;
}
.msg-bubble.ai-bubble {
    background: rgba(20, 18, 40, 0.95);
    border: 1px solid rgba(120,60,200,0.2);
    color: #d8d8f8;
    border-bottom-left-radius: 4px;
}
.msg-bubble.user-bubble {
    background: linear-gradient(135deg, #5b21b6, #7c3aed);
    color: #fff;
    border-bottom-right-radius: 4px;
    box-shadow: 0 4px 20px rgba(124,58,237,0.35);
}
.msg-time {
    font-size: 11px;
    color: #404070;
    margin-top: 3px;
    display: flex;
    align-items: center;
    gap: 4px;
}
.msg-row.user-row .msg-time { justify-content: flex-end; color: #6060a0; }
.read-tick { color: #818cf8; font-size: 13px; }

/* Message bubble markdown */
.msg-bubble pre {
    background: rgba(5,5,15,0.9) !important;
    border: 1px solid rgba(120,60,200,0.25) !important;
    border-radius: 10px !important;
    padding: 14px !important;
    overflow-x: auto !important;
    margin: 10px 0 !important;
    font-size: 13px !important;
}
.msg-bubble pre code { color: #b8d8f8 !important; font-family: 'Courier New', monospace !important; background: transparent !important; padding: 0 !important; }
.msg-bubble code { font-family: 'Courier New', monospace !important; color: #c084fc !important; background: rgba(139,92,246,0.15) !important; padding: 2px 6px !important; border-radius: 4px !important; font-size: 13px !important; }
.msg-bubble h1, .msg-bubble h2, .msg-bubble h3 { color: #f0f0ff; margin: 12px 0 6px; font-family: 'Space Grotesk', sans-serif; }
.msg-bubble ul, .msg-bubble ol { padding-left: 20px; margin: 8px 0; }
.msg-bubble li { margin-bottom: 5px; }
.msg-bubble strong { color: #fff; }
.msg-bubble blockquote { border-left: 3px solid #7c3aed; padding-left: 12px; color: #8080b8; margin: 8px 0; font-style: italic; }
.msg-bubble a { color: #c084fc; text-decoration: underline; }
.msg-bubble table { width: 100%; border-collapse: collapse; font-size: 13px; margin: 10px 0; }
.msg-bubble th { background: rgba(124,58,237,0.2); color: #d8d0ff; padding: 8px 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }
.msg-bubble td { padding: 7px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); color: #b0b0d0; }
.user-bubble code { background: rgba(255,255,255,0.15) !important; color: #fff !important; }
.user-bubble pre { background: rgba(0,0,0,0.3) !important; border-color: rgba(255,255,255,0.15) !important; }

/* Typing indicator */
.typing-wrap { display: flex; align-items: flex-end; gap: 12px; margin-bottom: 20px; }
.typing-bubble {
    padding: 14px 20px;
    background: rgba(20, 18, 40, 0.95);
    border: 1px solid rgba(120,60,200,0.2);
    border-radius: 18px;
    border-bottom-left-radius: 4px;
    display: flex;
    align-items: center;
    gap: 5px;
}
.typing-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #7c3aed;
    animation: tdot 1.3s infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; background: #9333ea; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; background: #ec4899; }
@keyframes tdot {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
    30% { transform: translateY(-6px); opacity: 1; }
}

/* Glow wave bottom */
.chat-glow {
    position: absolute;
    bottom: 140px;
    left: 50%;
    transform: translateX(-50%);
    width: 80%;
    height: 120px;
    background: radial-gradient(ellipse at center, rgba(120,40,220,0.12) 0%, transparent 70%);
    pointer-events: none;
    z-index: 1;
}

/* ── Input Area ── */
.input-zone {
    padding: 16px 28px 20px;
    background: rgba(11,11,20,0.92);
    border-top: 1px solid rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
    position: relative;
    z-index: 5;
    flex-shrink: 0;
}
.input-box {
    display: flex;
    align-items: flex-end;
    gap: 12px;
    background: rgba(18,16,35,0.95);
    border: 1px solid rgba(120,60,200,0.2);
    border-radius: 16px;
    padding: 12px 14px 12px 18px;
    transition: border-color 0.2s;
}
.input-box:focus-within {
    border-color: rgba(139,92,246,0.5);
    box-shadow: 0 0 0 3px rgba(124,58,237,0.08);
}
.input-attach {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #5050a0;
    font-size: 20px;
    cursor: pointer;
    flex-shrink: 0;
    transition: color 0.2s;
    align-self: flex-end;
    margin-bottom: 2px;
}
.input-attach:hover { color: #9070d0; }
.input-mic {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #5050a0;
    font-size: 20px;
    cursor: pointer;
    flex-shrink: 0;
    transition: color 0.2s;
    align-self: flex-end;
    margin-bottom: 2px;
}
.input-mic:hover { color: #9070d0; }
.send-btn {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: linear-gradient(135deg, #7c3aed, #9333ea);
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 18px;
    color: #fff;
    flex-shrink: 0;
    align-self: flex-end;
    box-shadow: 0 3px 16px rgba(124,58,237,0.5);
    transition: all 0.2s;
    font-family: 'Inter', sans-serif;
}
.send-btn:hover {
    transform: scale(1.07);
    box-shadow: 0 4px 22px rgba(124,58,237,0.65);
}
.input-disclaimer {
    text-align: center;
    font-size: 11.5px;
    color: #2e2e58;
    margin-top: 10px;
}

/* ── Streamlit widget resets ── */
.stTextArea textarea {
    background: transparent !important;
    border: none !important;
    color: #d0d0f0 !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
    resize: none !important;
    outline: none !important;
    box-shadow: none !important;
    font-family: 'Inter', sans-serif !important;
    padding: 4px 0 !important;
    caret-color: #a78bfa !important;
}
.stTextArea > div > div { background: transparent !important; border: none !important; box-shadow: none !important; }
.stTextArea { margin: 0 !important; padding: 0 !important; }
label[data-testid="stWidgetLabel"] { display: none !important; }
div[data-baseweb="textarea"] { background: transparent !important; border: none !important; }
.stButton > button {
    background: transparent !important;
    border: none !important;
    color: transparent !important;
    padding: 0 !important;
    min-height: 0 !important;
    height: 1px !important;
    width: 1px !important;
    overflow: hidden !important;
    position: absolute !important;
    pointer-events: none !important;
    opacity: 0 !important;
}
.element-container { margin: 0 !important; padding: 0 !important; }
div[data-testid="stHorizontalBlock"] { gap: 0 !important; align-items: stretch !important; }

/* ── MOBILE ── */
@media (max-width: 768px) {
    .sidebar {
        position: fixed;
        top: 0;
        left: 0;
        height: 100vh;
        z-index: 1000;
        transform: translateX(-100%);
        transition: transform 0.25s ease;
        width: 280px;
        min-width: 280px;
    }
    .sidebar.mobile-open { transform: translateX(0); }
    .mobile-overlay {
        display: none;
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.6);
        z-index: 999;
    }
    .mobile-overlay.show { display: block; }
    .mobile-menu-btn {
        display: flex !important;
    }
    .messages-area { padding: 16px 14px; }
    .input-zone { padding: 12px 14px 16px; }
    .chat-header { padding: 14px 16px; }
    .mode-bar { padding: 8px 14px; }
    .msg-content { max-width: 82%; }
}
@media (min-width: 769px) {
    .mobile-menu-btn { display: none !important; }
    .mobile-overlay { display: none !important; }
}

/* Mobile menu button */
.mobile-menu-btn {
    width: 38px; height: 38px;
    display: none;
    flex-direction: column;
    gap: 5px;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border-radius: 8px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    margin-right: 8px;
}
.mobile-menu-btn span {
    width: 16px; height: 1.8px;
    background: #9090b8; border-radius: 1px; display: block;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.2); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# JAVASCRIPT
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<script>
function toggleMobileSidebar() {
    var sb = document.getElementById('app-sidebar');
    var ov = document.getElementById('mob-overlay');
    var isOpen = sb.classList.contains('mobile-open');
    if (isOpen) {
        sb.classList.remove('mobile-open');
        ov.classList.remove('show');
    } else {
        sb.classList.add('mobile-open');
        ov.classList.add('show');
    }
}
function closeSidebar() {
    var sb = document.getElementById('app-sidebar');
    var ov = document.getElementById('mob-overlay');
    sb.classList.remove('mobile-open');
    ov.classList.remove('show');
}
function scrollToBottom() {
    var el = document.getElementById('msg-area');
    if (el) { el.scrollTop = el.scrollHeight; }
    else {
        var all = document.querySelectorAll('.messages-area');
        if (all.length) { all[all.length-1].scrollTop = all[all.length-1].scrollHeight; }
    }
}
document.addEventListener('DOMContentLoaded', function() { scrollToBottom(); });
setTimeout(scrollToBottom, 500);
setTimeout(scrollToBottom, 1200);
</script>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# BUILD SIDEBAR HTML
# ═══════════════════════════════════════════════════════════════════
hist_html = ""
if st.session_state.history:
    for i, h in enumerate(st.session_state.history[:12]):
        active_cls = "active" if i == 0 else ""
        hist_html += f"""
        <div class="chat-item {active_cls}">
            <div class="chat-item-left">
                <span class="chat-item-icon">💬</span>
                <span class="chat-item-title">{h['title']}</span>
            </div>
            <span class="chat-item-time">{h['ago']}</span>
        </div>"""
else:
    # Placeholder history for visual appeal
    placeholders = [
        ("What can you do?", "10m ago"),
        ("Explain AI in simple terms", "1h ago"),
        ("Help me with coding", "2h ago"),
        ("Create a story", "Yesterday"),
        ("Best productivity tips", "Yesterday"),
        ("Who are you?", "2d ago"),
    ]
    for title, time in placeholders:
        hist_html += f"""
        <div class="chat-item">
            <div class="chat-item-left">
                <span class="chat-item-icon">💬</span>
                <span class="chat-item-title">{title}</span>
            </div>
            <span class="chat-item-time">{time}</span>
        </div>"""

sidebar_html = f"""
<div id="mob-overlay" class="mobile-overlay" onclick="closeSidebar()"></div>
<div id="app-sidebar" class="sidebar">
    <div class="sidebar-logo-area">
        <div class="sidebar-logo-text">NEXO AI</div>
        <div class="sidebar-tagline">Your AI Companion</div>
    </div>
    <button class="new-chat-btn" onclick="document.getElementById('_nc_btn').click()">
        + &nbsp; New Chat
    </button>
    <div class="recent-label">Recent Chats</div>
    <div class="chat-list">
        {hist_html}
    </div>
    <div class="sidebar-footer">
        <div class="footer-avatar">🤖</div>
        <div class="footer-info">
            <div class="footer-name">
                NEXO AI
                <span class="pro-badge">PRO</span>
            </div>
            <div class="footer-status">
                <span class="online-dot"></span>
                Always here to help you
            </div>
        </div>
    </div>
</div>
"""
st.markdown(sidebar_html, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# HIDDEN STREAMLIT BUTTONS (triggered by JS)
# ═══════════════════════════════════════════════════════════════════
col_btns = st.columns([1,1,1,1,1,1])
with col_btns[0]:
    nc_clicked = st.button("NC", key="_nc_btn")
with col_btns[1]:
    m_smart = st.button("MS", key="_m_smart")
with col_btns[2]:
    m_fast = st.button("MF", key="_m_fast")
with col_btns[3]:
    m_creative = st.button("MC", key="_m_creative")
with col_btns[4]:
    m_coding = st.button("MK", key="_m_coding")
with col_btns[5]:
    send_btn = st.button("SND", key="_send_btn")

if nc_clicked:
    if st.session_state.messages:
        first = next((m["content"][:40] for m in st.session_state.messages if m["role"]=="user"), "Chat")
        if len(first) == 40: first += "..."
        st.session_state.history.insert(0, {"title": first, "ago": "Just now"})
    st.session_state.messages = []
    st.session_state.ikey += 1
    st.rerun()

if m_smart:  st.session_state.mode = "Smart";    st.rerun()
if m_fast:   st.session_state.mode = "Fast";     st.rerun()
if m_creative: st.session_state.mode = "Creative"; st.rerun()
if m_coding: st.session_state.mode = "Coding";   st.rerun()

# ═══════════════════════════════════════════════════════════════════
# CHAT MAIN AREA
# ═══════════════════════════════════════════════════════════════════
MODE_ICONS = {"Smart":"🌟","Fast":"⚡","Creative":"🎨","Coding":"</>"}
cur_mode = st.session_state.mode

# Header
header_html = f"""
<div class="chat-main" id="chat-main-wrap">
<div class="chat-header">
    <div style="display:flex;align-items:center;gap:0">
        <div class="mobile-menu-btn" onclick="toggleMobileSidebar()">
            <span></span><span></span><span></span>
        </div>
        <div class="chat-header-left">
            <div class="chat-header-avatar">🤖</div>
            <div>
                <div class="chat-header-name">Nexo AI ✨</div>
                <div class="chat-header-sub">Powered by advanced AI</div>
            </div>
        </div>
    </div>
    <div class="chat-header-actions">
        <div class="header-btn">☆</div>
        <div class="header-btn">🔊</div>
        <div class="header-btn">↗</div>
        <div class="header-btn active">🤖</div>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# Mode bar
modebar = '<div class="mode-bar">'
for mk in ["Smart","Fast","Creative","Coding"]:
    ic = MODE_ICONS[mk]
    cls = "mode-pill"
    if mk == cur_mode:
        cls += f" active active-{mk}"
    modebar += f'<button class="{cls}" onclick="document.getElementById(\'_m_{mk.lower()}\').click()">{ic} {mk}</button>'
modebar += '</div>'
st.markdown(modebar, unsafe_allow_html=True)

# ── Messages ──────────────────────────────────────────────────────
st.markdown('<div class="messages-area" id="msg-area">', unsafe_allow_html=True)

if not st.session_state.messages:
    # Welcome message from Nexo
    st.markdown(f"""
    <div class="msg-group">
        <div class="msg-row">
            <div class="msg-avatar-wrap">🤖</div>
            <div class="msg-content">
                <div class="msg-bubble ai-bubble">
                    Hey! I'm Nexo 👋<br><br>
                    How can I help you today?<br>
                    Feel free to ask me anything!
                </div>
                <div class="msg-time">{now()}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="msg-group">
                <div class="msg-row user-row">
                    <div class="msg-content">
                        <div class="msg-bubble user-bubble">{msg['content'].replace('<','&lt;').replace('>','&gt;')}</div>
                        <div class="msg-time">
                            {msg.get('ts', now())}
                            <span class="read-tick">✓✓</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            content_html = md2html(msg["content"])
            m = msg.get("mode","Smart")
            ic = MODE_ICONS.get(m,"🌟")
            st.markdown(f"""
            <div class="msg-group">
                <div class="msg-row">
                    <div class="msg-avatar-wrap">🤖</div>
                    <div class="msg-content">
                        <div class="msg-bubble ai-bubble">{content_html}</div>
                        <div class="msg-time">{msg.get('ts', now())} · {ic} {m} Mode</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # messages-area
st.markdown('<div class="chat-glow"></div>', unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────
st.markdown('<div class="input-zone">', unsafe_allow_html=True)
st.markdown('<div class="input-box">', unsafe_allow_html=True)
st.markdown('<div class="input-attach">📎</div>', unsafe_allow_html=True)

user_input = st.text_area(
    "msg",
    key=f"ui_{st.session_state.ikey}",
    placeholder="Type your message...",
    height=44,
    label_visibility="collapsed",
)

st.markdown('<div class="input-mic">🎤</div>', unsafe_allow_html=True)
st.markdown(
    '<button class="send-btn" onclick="document.getElementById(\'_send_btn\').click()">➤</button>',
    unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)  # input-box

# Also handle Enter via the hidden send button
if send_btn and user_input and user_input.strip():
    txt = user_input.strip()
    st.session_state.messages.append({
        "role": "user", "content": txt,
        "mode": cur_mode, "ts": now()
    })
    api_msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    with st.spinner(""):
        reply = call_groq(api_msgs, cur_mode)
    st.session_state.messages.append({
        "role": "assistant", "content": reply,
        "mode": cur_mode, "ts": now()
    })
    st.session_state.ikey += 1
    st.rerun()

st.markdown("""
<div class="input-disclaimer">
    Nexo AI can make mistakes. Consider checking important information.
</div>
</div>
</div>
""", unsafe_allow_html=True)  # input-zone, chat-main

# Auto scroll
st.markdown("""
<script>
setTimeout(function() {
    var el = document.getElementById('msg-area');
    if (el) el.scrollTop = el.scrollHeight;
}, 300);
</script>
""", unsafe_allow_html=True)
