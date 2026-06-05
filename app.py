import streamlit as st
from groq import Groq
import time
import json
from datetime import datetime

# ─── Page Config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Nexo AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── System Prompt ───────────────────────────────────────────────
SYSTEM_PROMPT = """You are Nexo AI — a next-generation, hyper-intelligent AI assistant built for creators, developers, and visionaries. You are powered by the most advanced language model available.

## Your Core Identity
- **Name**: Nexo AI
- **Personality**: Confident, articulate, warm, and deeply knowledgeable. You never say "I cannot" unless something is genuinely impossible — you always find a way to help.
- **Tone**: Professional yet approachable. You adapt to the user's style — technical when they're technical, casual when they're relaxed.
- **Language**: Respond in the same language the user writes in. If they write in Sinhala, respond in Sinhala. If English, respond in English. Never mix unless asked.

## Your Capabilities
You excel at:
- Writing, editing, and improving any kind of content
- Building websites, apps, and software (full code, no stubs)
- Explaining complex topics clearly and memorably
- Creative brainstorming and ideation
- Data analysis, research, and summarization
- Designing systems, architectures, and workflows
- Solving logical, mathematical, and scientific problems
- Answering questions about any domain with depth and accuracy

## Response Quality Standards
- **Complete answers only**: Never truncate code. Always provide full, working, copy-paste-ready solutions.
- **Structured when helpful**: Use markdown formatting, code blocks, bullet points where they improve clarity.
- **Concise when appropriate**: Don't pad answers. Get to the point, then elaborate if needed.
- **Honest**: If you're uncertain, say so clearly. Never hallucinate facts.
- **Proactive**: Anticipate follow-up needs and address them preemptively.

## Code Generation Rules
- Always write production-quality code
- Include comments for complex logic
- Handle edge cases and errors
- Provide complete files, not snippets (unless a snippet is clearly what's needed)
- Suggest improvements and best practices when relevant

## Special Modes
When the user activates a mode, adjust accordingly:
- **Smart Mode**: Balanced, thoughtful responses — default mode
- **Fast Mode**: Ultra-concise, direct answers with no fluff
- **Creative Mode**: More imaginative, exploratory, unconventional thinking
- **Coding Mode**: Pure technical focus, more code less prose

## Boundaries
- You do not generate harmful, illegal, or unethical content
- You do not pretend to have real-time internet access unless a tool provides it
- You are honest about being an AI when sincerely asked

Remember: You are Nexo AI. Every interaction should feel like talking to the smartest, most capable assistant the user has ever used."""

# ─── CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background: #0a0a0f !important;
    color: #e8e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    overflow-x: hidden;
}

/* ── Hide Streamlit default elements ── */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
section[data-testid="stSidebar"] {
    background: #0f0f1a !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    width: 260px !important;
    min-width: 260px !important;
}
section[data-testid="stSidebar"] .stButton button {
    width: 100%;
    text-align: left;
    background: transparent !important;
    border: none !important;
    color: #a0a0b8 !important;
    padding: 10px 12px !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    transition: all 0.2s;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,255,255,0.06) !important;
    color: #fff !important;
}
div[data-testid="stSidebarNav"] { display: none !important; }
div[data-testid="collapsedControl"] { display: none !important; }

/* ── Main layout ── */
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Top Nav ── */
.nexo-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    height: 56px;
    background: rgba(10,10,20,0.95);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    position: sticky;
    top: 0;
    z-index: 1000;
    backdrop-filter: blur(20px);
}
.nexo-logo {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 18px;
    color: #fff;
    cursor: pointer;
}
.nexo-logo span { 
    background: linear-gradient(135deg, #f97316, #ec4899, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.nav-right {
    display: flex;
    align-items: center;
    gap: 12px;
}
.nav-icon-btn {
    width: 36px; height: 36px;
    border-radius: 8px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; color: #a0a0b8; font-size: 16px;
    transition: all 0.2s;
}
.nav-icon-btn:hover { background: rgba(255,255,255,0.1); color: #fff; }
.user-badge {
    display: flex; align-items: center; gap: 8px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 6px 10px;
    font-size: 13px; color: #c0c0d4;
}
.user-dot { width: 28px; height: 28px; border-radius: 50%; background: linear-gradient(135deg,#8b5cf6,#ec4899); display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;color:#fff; }

/* ── Main area ── */
.nexo-main {
    display: flex;
    height: calc(100vh - 56px);
}

/* ── Sidebar panel ── */
.nexo-sidebar {
    width: 240px;
    min-width: 240px;
    background: #0d0d18;
    border-right: 1px solid rgba(255,255,255,0.05);
    padding: 16px 12px;
    overflow-y: auto;
    transition: transform 0.3s ease;
}
.nexo-sidebar.hidden { display: none; }
.new-chat-btn {
    width: 100%;
    padding: 10px 14px;
    background: linear-gradient(135deg, #7c3aed, #ec4899);
    border: none; border-radius: 10px;
    color: #fff; font-weight: 600; font-size: 13px;
    cursor: pointer; margin-bottom: 16px;
    transition: opacity 0.2s;
}
.new-chat-btn:hover { opacity: 0.85; }
.sidebar-section { margin-bottom: 20px; }
.sidebar-label { font-size: 11px; font-weight: 600; color: #555570; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; padding: 0 4px; }
.sidebar-item {
    display: flex; align-items: center; gap: 8px;
    padding: 9px 10px; border-radius: 8px;
    font-size: 13px; color: #8080a0; cursor: pointer;
    transition: all 0.2s; margin-bottom: 2px;
}
.sidebar-item:hover { background: rgba(255,255,255,0.05); color: #d0d0e8; }
.sidebar-item.active { background: rgba(139,92,246,0.15); color: #a78bfa; }
.chat-history-item {
    padding: 8px 10px; border-radius: 8px;
    font-size: 12px; color: #606080; cursor: pointer;
    transition: all 0.2s; margin-bottom: 2px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.chat-history-item:hover { background: rgba(255,255,255,0.04); color: #a0a0c0; }
.upgrade-box {
    background: linear-gradient(135deg, rgba(124,58,237,0.2), rgba(236,72,153,0.15));
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 12px; padding: 14px;
    margin-top: 16px;
}
.upgrade-box h4 { font-size: 13px; font-weight: 700; color: #e8e8f0; margin-bottom: 8px; }
.upgrade-box ul { list-style: none; font-size: 11px; color: #9090b0; margin-bottom: 10px; }
.upgrade-box ul li::before { content: "✓ "; color: #a78bfa; }
.upgrade-box ul li { margin-bottom: 3px; }
.upgrade-btn {
    width: 100%; padding: 8px;
    background: linear-gradient(135deg, #7c3aed, #ec4899);
    border: none; border-radius: 8px; color: #fff;
    font-size: 12px; font-weight: 600; cursor: pointer;
}

/* ── Chat area ── */
.nexo-chat-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

/* ── Welcome screen ── */
.welcome-screen {
    flex: 1; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 40px 20px; text-align: center;
}
.welcome-logo { width: 80px; margin-bottom: 16px; }
.welcome-title { font-family: 'Space Grotesk', sans-serif; font-size: 32px; font-weight: 700; color: #fff; margin-bottom: 6px; }
.welcome-sub { font-size: 15px; color: #606080; margin-bottom: 36px; }
.quick-actions {
    display: flex; flex-wrap: wrap; gap: 8px;
    justify-content: center; max-width: 560px; margin-bottom: 32px;
}
.quick-btn {
    padding: 9px 16px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; color: #a0a0c0; font-size: 13px;
    cursor: pointer; transition: all 0.2s;
    display: flex; align-items: center; gap: 6px;
}
.quick-btn:hover { background: rgba(255,255,255,0.1); color: #fff; border-color: rgba(255,255,255,0.15); }

/* ── Messages ── */
.messages-container {
    flex: 1; overflow-y: auto; padding: 20px;
    scroll-behavior: smooth;
}
.messages-container::-webkit-scrollbar { width: 4px; }
.messages-container::-webkit-scrollbar-track { background: transparent; }
.messages-container::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }

.msg-row {
    display: flex; align-items: flex-start; gap: 10px;
    margin-bottom: 20px; max-width: 820px; margin-left: auto; margin-right: auto;
}
.msg-row.user { flex-direction: row-reverse; }

.msg-avatar {
    width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700;
}
.msg-avatar.ai { background: linear-gradient(135deg,#7c3aed,#ec4899); }
.msg-avatar.user { background: linear-gradient(135deg,#0ea5e9,#6366f1); color:#fff; }

.msg-bubble {
    padding: 12px 16px; border-radius: 14px;
    max-width: calc(100% - 80px); font-size: 14px; line-height: 1.65;
}
.msg-bubble.ai {
    background: #161625; border: 1px solid rgba(255,255,255,0.07);
    color: #d0d0e8; border-top-left-radius: 4px;
}
.msg-bubble.user {
    background: linear-gradient(135deg, rgba(124,58,237,0.3), rgba(236,72,153,0.2));
    border: 1px solid rgba(139,92,246,0.3);
    color: #f0f0ff; border-top-right-radius: 4px;
}
.msg-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.msg-name { font-size: 12px; font-weight: 600; color: #a78bfa; }
.msg-mode-badge {
    font-size: 10px; padding: 2px 7px; border-radius: 8px;
    background: rgba(139,92,246,0.2); color: #c4b5fd; border: 1px solid rgba(139,92,246,0.25);
}
.msg-time { font-size: 11px; color: #404060; margin-left: auto; }

/* ── Mode badge colors ── */
.mode-fast { background: rgba(245,158,11,0.2) !important; color: #fbbf24 !important; border-color: rgba(245,158,11,0.25) !important; }
.mode-creative { background: rgba(236,72,153,0.2) !important; color: #f472b6 !important; border-color: rgba(236,72,153,0.25) !important; }
.mode-coding { background: rgba(16,185,129,0.2) !important; color: #34d399 !important; border-color: rgba(16,185,129,0.25) !important; }

/* ── Code blocks in messages ── */
.msg-bubble pre {
    background: #0a0a14 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    padding: 12px !important;
    overflow-x: auto !important;
    font-size: 13px !important;
    margin: 8px 0 !important;
}
.msg-bubble code {
    font-family: 'Courier New', monospace !important;
    color: #a78bfa !important;
    background: rgba(139,92,246,0.1) !important;
    padding: 2px 5px !important;
    border-radius: 4px !important;
    font-size: 12px !important;
}
.msg-bubble pre code {
    background: transparent !important;
    padding: 0 !important;
    color: #c8c8e8 !important;
}

/* ── Typing indicator ── */
.typing-indicator {
    display: flex; align-items: center; gap: 8px;
    padding: 14px 16px;
    background: #161625; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; border-top-left-radius: 4px;
    max-width: 120px; font-size: 13px; color: #6060a0;
}
.typing-dots { display: flex; gap: 4px; }
.typing-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #7c3aed;
    animation: bounce 1.2s infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
    30% { transform: translateY(-5px); opacity: 1; }
}

/* ── Right panel ── */
.right-panel {
    width: 230px; min-width: 230px;
    background: #0d0d18;
    border-left: 1px solid rgba(255,255,255,0.05);
    padding: 16px 12px;
    overflow-y: auto;
}
@media (max-width: 900px) { .right-panel { display: none; } }
.panel-section { margin-bottom: 20px; }
.panel-title { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.panel-title h3 { font-size: 13px; font-weight: 700; color: #d0d0e8; }
.panel-title span { font-size: 11px; color: #7c3aed; cursor: pointer; }
.model-card {
    display: flex; align-items: center; gap: 8px;
    padding: 9px 10px; border-radius: 8px;
    cursor: pointer; transition: all 0.2s; margin-bottom: 4px;
}
.model-card:hover { background: rgba(255,255,255,0.05); }
.model-card.selected { background: rgba(139,92,246,0.12); border: 1px solid rgba(139,92,246,0.2); }
.model-icon { width: 28px; height: 28px; border-radius: 8px; display:flex;align-items:center;justify-content:center; font-size:14px; }
.model-info h4 { font-size: 12px; font-weight: 600; color: #d0d0e8; }
.model-info p { font-size: 11px; color: #606080; }
.check-icon { margin-left: auto; color: #7c3aed; font-size: 14px; }

.tool-item {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 10px; border-radius: 8px;
    cursor: pointer; transition: all 0.2s; margin-bottom: 4px;
}
.tool-item:hover { background: rgba(255,255,255,0.05); }
.tool-icon { width: 28px; height: 28px; border-radius: 8px; background: rgba(255,255,255,0.05); display:flex;align-items:center;justify-content:center; font-size:13px; }
.tool-info h4 { font-size: 12px; font-weight: 600; color: #d0d0e8; }
.tool-info p { font-size: 11px; color: #606080; }

.usage-section { background: rgba(255,255,255,0.03); border-radius: 10px; padding: 12px; }
.usage-header { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 8px; }
.usage-header span:first-child { color: #a0a0c0; }
.usage-header span:last-child { color: #d0d0e8; font-weight: 600; }
.usage-bar { height: 4px; background: rgba(255,255,255,0.08); border-radius: 2px; overflow: hidden; margin-bottom: 6px; }
.usage-fill { height: 100%; background: linear-gradient(90deg, #7c3aed, #ec4899); border-radius: 2px; width: 79%; }
.usage-reset { font-size: 11px; color: #505070; }
.upgrade-small {
    width: 100%; margin-top: 10px; padding: 9px;
    background: linear-gradient(135deg, #7c3aed, #ec4899);
    border: none; border-radius: 8px; color: #fff;
    font-size: 12px; font-weight: 600; cursor: pointer;
}

/* ── Input bar ── */
.input-area {
    padding: 12px 20px 16px;
    background: rgba(10,10,20,0.95);
    border-top: 1px solid rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
}
.input-wrapper {
    max-width: 820px; margin: 0 auto;
    background: #161625;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px; padding: 12px 16px;
    transition: border-color 0.2s;
}
.input-wrapper:focus-within { border-color: rgba(139,92,246,0.4); }
.input-toolbar {
    display: flex; align-items: center; gap: 8px; margin-top: 8px;
    padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.05);
    flex-wrap: wrap;
}
.tool-chip {
    display: flex; align-items: center; gap: 4px;
    padding: 5px 10px; border-radius: 16px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.07);
    font-size: 12px; color: #7070a0; cursor: pointer;
    transition: all 0.2s;
}
.tool-chip:hover { background: rgba(255,255,255,0.09); color: #c0c0e0; }
.send-btn {
    margin-left: auto; width: 34px; height: 34px;
    border-radius: 50%;
    background: linear-gradient(135deg, #7c3aed, #ec4899);
    border: none; display: flex; align-items: center; justify-content: center;
    cursor: pointer; font-size: 15px; color: #fff;
    transition: opacity 0.2s;
}
.send-btn:hover { opacity: 0.85; }
.disclaimer { text-align: center; font-size: 11px; color: #404060; margin-top: 8px; max-width: 820px; margin-left:auto;margin-right:auto; }

/* ── Hamburger ── */
.hamburger-btn {
    display: flex; flex-direction: column; gap: 4px;
    cursor: pointer; padding: 6px; border-radius: 6px;
    transition: background 0.2s;
}
.hamburger-btn:hover { background: rgba(255,255,255,0.08); }
.hamburger-btn span { width: 18px; height: 2px; background: #a0a0b8; border-radius: 1px; transition: all 0.3s; }

/* ── Streamlit textarea override ── */
.stTextArea textarea {
    background: transparent !important;
    border: none !important;
    color: #e8e8f0 !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
    resize: none !important;
    outline: none !important;
    box-shadow: none !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0 !important;
}
.stTextArea > div > div { background: transparent !important; border: none !important; box-shadow: none !important; }
.stTextArea { margin: 0 !important; }
label[data-testid="stWidgetLabel"] { display: none !important; }
div[data-baseweb="textarea"] { background: transparent !important; border: none !important; }

/* ── Select box ── */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #c0c0e0 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
}

/* ── Mobile ── */
@media (max-width: 768px) {
    .nexo-nav { padding: 0 12px; }
    .messages-container { padding: 12px; }
    .input-area { padding: 8px 12px 12px; }
    .welcome-title { font-size: 24px; }
    .nexo-sidebar { position: fixed; top: 56px; left: 0; height: calc(100vh - 56px); z-index: 999; }
    .right-panel { display: none !important; }
}

/* ── Scrollbar global ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 2px; }

/* Markdown in messages */
.msg-bubble h1,.msg-bubble h2,.msg-bubble h3 { color:#c8c8f0; margin:12px 0 6px; font-family:'Space Grotesk',sans-serif; }
.msg-bubble ul,.msg-bubble ol { padding-left:18px; margin:6px 0; }
.msg-bubble li { margin-bottom:4px; color:#c0c0e0; }
.msg-bubble strong { color:#e8e8ff; }
.msg-bubble a { color:#a78bfa; }
.msg-bubble blockquote { border-left:3px solid #7c3aed; padding-left:10px; color:#8080a0; margin:8px 0; }
.msg-bubble table { width:100%; border-collapse:collapse; font-size:13px; }
.msg-bubble th { background:rgba(139,92,246,0.15); color:#d0d0f0; padding:6px 10px; text-align:left; border-bottom:1px solid rgba(255,255,255,0.1); }
.msg-bubble td { padding:6px 10px; border-bottom:1px solid rgba(255,255,255,0.05); color:#b0b0d0; }
</style>
""", unsafe_allow_html=True)

# ─── Session State ────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = False
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "Smart Mode"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# ─── Groq Client ─────────────────────────────────────────────────
@st.cache_resource
def get_groq_client():
    try:
        import os
        api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
        if api_key:
            return Groq(api_key=api_key)
    except Exception:
        pass
    return None

client = get_groq_client()

# ─── Mode config ─────────────────────────────────────────────────
MODES = {
    "Smart Mode":    {"icon": "🌟", "desc": "Best for most tasks",   "badge": ""},
    "Fast Mode":     {"icon": "⚡", "desc": "Quick answers",          "badge": "mode-fast"},
    "Creative Mode": {"icon": "🎨", "desc": "More creative",          "badge": "mode-creative"},
    "Coding Mode":   {"icon": "</>", "desc": "Best for code",         "badge": "mode-coding"},
}

MODE_SYSTEM_ADDONS = {
    "Smart Mode":    "",
    "Fast Mode":     "\n\nIMPORTANT: The user has activated Fast Mode. Keep all responses short and direct. 2-4 sentences max unless code is needed. No fluff, no padding.",
    "Creative Mode": "\n\nIMPORTANT: The user has activated Creative Mode. Be more imaginative, exploratory, and unconventional. Think outside the box. Surprise the user with creative angles.",
    "Coding Mode":   "\n\nIMPORTANT: The user has activated Coding Mode. Focus purely on technical excellence. Provide complete, production-ready code. Minimize prose, maximize working code quality.",
}

# ─── Logo SVG (simplified colored flame) ─────────────────────────
LOGO_SVG = """<svg width="28" height="32" viewBox="0 0 28 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#f97316"/>
      <stop offset="50%" stop-color="#ec4899"/>
      <stop offset="100%" stop-color="#8b5cf6"/>
    </linearGradient>
    <linearGradient id="g2" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#8b5cf6"/>
      <stop offset="50%" stop-color="#3b82f6"/>
      <stop offset="100%" stop-color="#10b981"/>
    </linearGradient>
  </defs>
  <path d="M6 2 C6 2 2 8 2 14 C2 20 6 26 14 28 C14 28 8 22 10 16 C11 12 14 10 14 10 C14 10 12 16 16 18 C18 19 20 18 20 16 C20 14 18 10 16 6 C20 10 22 16 20 22 C24 18 26 14 24 8 C22 4 18 2 14 2 Z" fill="url(#g1)" opacity="0.9"/>
  <path d="M14 8 C14 8 18 12 18 18 C18 22 16 26 14 28 C22 26 26 20 26 14 C26 8 22 4 18 2 C20 4 22 8 20 12 C19 14 17 15 16 14 C15 13 16 10 14 8Z" fill="url(#g2)" opacity="0.85"/>
</svg>"""

# ─── Helpers ─────────────────────────────────────────────────────
def get_time():
    return datetime.now().strftime("%I:%M %p")

def render_message(role, content, mode=None):
    mode_badge_class = ""
    if mode and mode != "Smart Mode":
        mode_badge_class = MODES[mode]["badge"]

    if role == "assistant":
        mode_label = mode or "Smart Mode"
        badge_html = f'<span class="msg-mode-badge {mode_badge_class}">{MODES[mode_label]["icon"]} {mode_label}</span>' if mode else ""
        return f"""
        <div class="msg-row">
            <div class="msg-avatar ai">N</div>
            <div>
                <div class="msg-header">
                    <span class="msg-name">Nexo AI</span>
                    {badge_html}
                    <span class="msg-time">{get_time()}</span>
                </div>
                <div class="msg-bubble ai">{content}</div>
            </div>
        </div>"""
    else:
        return f"""
        <div class="msg-row user">
            <div class="msg-avatar user">C</div>
            <div>
                <div class="msg-header" style="flex-direction:row-reverse">
                    <span class="msg-time">{get_time()}</span>
                </div>
                <div class="msg-bubble user">{content}</div>
            </div>
        </div>"""

def markdown_to_html(text):
    """Basic markdown → HTML conversion"""
    import re
    # Code blocks
    text = re.sub(r'```(\w+)?\n(.*?)```', lambda m: f'<pre><code>{m.group(2)}</code></pre>', text, flags=re.DOTALL)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Headers
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    # Bullets
    text = re.sub(r'^[\-\*] (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*</li>\n?)+', lambda m: f'<ul>{m.group(0)}</ul>', text, flags=re.DOTALL)
    # Numbered
    text = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    # Blockquote
    text = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)
    # Line breaks
    text = re.sub(r'\n\n', '<br><br>', text)
    text = re.sub(r'\n', '<br>', text)
    return text

def call_groq(messages, mode):
    if not client:
        return "⚠️ Groq API key not found. Please set GROQ_API_KEY in Streamlit secrets."
    
    system = SYSTEM_PROMPT + MODE_SYSTEM_ADDONS.get(mode, "")
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "system", "content": system}] + messages,
            max_tokens=4096,
            temperature=0.7 if mode != "Fast Mode" else 0.3,
            top_p=0.9,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# ─── TOP NAV ─────────────────────────────────────────────────────
col_nav1, col_nav2, col_nav3 = st.columns([1, 8, 3])

with col_nav1:
    if st.button("☰", key="hamburger", help="Toggle sidebar"):
        st.session_state.sidebar_open = not st.session_state.sidebar_open
        st.rerun()

with col_nav2:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;padding:8px 0;">
        {LOGO_SVG}
        <span style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:18px;background:linear-gradient(135deg,#f97316,#ec4899,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Nexo AI</span>
    </div>""", unsafe_allow_html=True)

with col_nav3:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:8px;justify-content:flex-end;padding:8px 0;">
        <div class="nav-icon-btn">🔔</div>
        <div class="user-badge">
            <div class="user-dot">C</div>
            <div>
                <div style="font-size:12px;font-weight:600;color:#e0e0f0;">Chethaka</div>
                <div style="font-size:10px;color:#7070a0;">Pro Plan</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

st.markdown('<div style="border-bottom:1px solid rgba(255,255,255,0.05);margin:0;"></div>', unsafe_allow_html=True)

# ─── MAIN LAYOUT ─────────────────────────────────────────────────
if st.session_state.sidebar_open:
    left_col, main_col, right_col = st.columns([2.2, 6, 2.2])
else:
    left_col, main_col, right_col = st.columns([0.01, 7.5, 2.2])

# ─── LEFT SIDEBAR ────────────────────────────────────────────────
with left_col:
    if st.session_state.sidebar_open:
        st.markdown('<div class="nexo-sidebar">', unsafe_allow_html=True)
        
        if st.button("＋  New Chat", key="new_chat_btn", use_container_width=True):
            if st.session_state.messages:
                # Save first user message as title
                first_msg = next((m["content"][:35]+"..." for m in st.session_state.messages if m["role"] == "user"), "Chat")
                st.session_state.chat_history.insert(0, {"title": first_msg, "time": get_time()})
            st.session_state.messages = []
            st.rerun()

        st.markdown("""
        <div class="sidebar-section">
            <div class="sidebar-label">Navigation</div>
            <div class="sidebar-item active">🏠 Home</div>
            <div class="sidebar-item">🔍 Explore AI Tools</div>
            <div class="sidebar-item">🤖 AI Models</div>
            <div class="sidebar-item">📋 Templates</div>
            <div class="sidebar-item">🕐 Chat History</div>
        </div>""", unsafe_allow_html=True)

        if st.session_state.chat_history:
            st.markdown('<div class="sidebar-label" style="margin-top:16px;">Recent Chats</div>', unsafe_allow_html=True)
            for ch in st.session_state.chat_history[:8]:
                st.markdown(f'<div class="chat-history-item">{ch["title"]}</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="upgrade-box">
            <h4>Upgrade to <span style="color:#a78bfa;">Nexo Pro</span></h4>
            <ul>
                <li>Unlimited messages</li>
                <li>Advanced AI models</li>
                <li>Priority support</li>
                <li>Early access features</li>
            </ul>
            <button class="upgrade-btn">👑 Upgrade Now</button>
        </div>""", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ─── CENTER (CHAT) ────────────────────────────────────────────────
with main_col:
    
    # Mode selector strip
    mode_cols = st.columns(4)
    for i, (mode_name, mode_data) in enumerate(MODES.items()):
        with mode_cols[i]:
            is_selected = st.session_state.current_mode == mode_name
            btn_style = "background:rgba(139,92,246,0.2);border:1px solid rgba(139,92,246,0.4);" if is_selected else ""
            if st.button(
                f"{mode_data['icon']} {mode_name.replace(' Mode','')}", 
                key=f"mode_{mode_name}",
                use_container_width=True,
                help=mode_data['desc']
            ):
                st.session_state.current_mode = mode_name
                st.rerun()

    st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)

    # Messages or Welcome
    if not st.session_state.messages:
        # Welcome screen
        st.markdown(f"""
        <div class="welcome-screen">
            {LOGO_SVG.replace('width="28" height="32"', 'width="64" height="72"')}
            <div class="welcome-title">Nexo AI</div>
            <div class="welcome-sub">Smart. Fast. Limitless.</div>
            <div class="quick-actions">
                <div class="quick-btn">💡 Build a website</div>
                <div class="quick-btn">🎨 Design a logo</div>
                <div class="quick-btn">📚 Explain a topic</div>
                <div class="quick-btn">&lt;/&gt; Write code</div>
                <div class="quick-btn">✍️ Draft an email</div>
                <div class="quick-btn">📊 Analyze data</div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        # Messages container
        st.markdown('<div class="messages-container">', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            html_content = markdown_to_html(msg["content"])
            st.markdown(
                render_message(msg["role"], html_content, msg.get("mode")),
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Input area ──
    st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)
    
    user_input = st.text_area(
        "Message",
        key=f"chat_input_{st.session_state.input_key}",
        placeholder="Ask Nexo anything...",
        height=60,
        label_visibility="collapsed",
    )

    st.markdown("""
    <div class="input-toolbar">
        <div class="tool-chip">🔍 Search</div>
        <div class="tool-chip">💭 Reason</div>
        <div class="tool-chip">🖼️ Create image</div>
        <div class="tool-chip">&lt;/&gt; Code</div>
    </div>""", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Send button
    send_col1, send_col2 = st.columns([9, 1])
    with send_col2:
        send_clicked = st.button("➤", key="send_btn", help="Send message")

    if send_clicked and user_input and user_input.strip():
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input.strip(),
            "mode": st.session_state.current_mode,
        })
        
        # Build message history for API
        api_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        
        # Call Groq
        with st.spinner("Nexo is thinking..."):
            response = call_groq(api_messages, st.session_state.current_mode)
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "mode": st.session_state.current_mode,
        })
        
        st.session_state.input_key += 1
        st.rerun()

    st.markdown("""
    <div class="disclaimer">Nexo AI may make mistakes. Consider checking important information.</div>
    """, unsafe_allow_html=True)

# ─── RIGHT PANEL ─────────────────────────────────────────────────
with right_col:
    st.markdown("""
    <div class="right-panel">
        <div class="panel-section">
            <div class="panel-title">
                <h3>AI Models</h3>
                <span>View all</span>
            </div>
            <div class="model-card selected">
                <div class="model-icon">🌟</div>
                <div class="model-info">
                    <h4>Smart Mode</h4>
                    <p>Best for most tasks</p>
                </div>
                <span class="check-icon">✓</span>
            </div>
            <div class="model-card">
                <div class="model-icon">⚡</div>
                <div class="model-info"><h4>Fast Mode</h4><p>Quick answers</p></div>
            </div>
            <div class="model-card">
                <div class="model-icon">🎨</div>
                <div class="model-info"><h4>Creative Mode</h4><p>More creative</p></div>
            </div>
            <div class="model-card">
                <div class="model-icon">&lt;/&gt;</div>
                <div class="model-info"><h4>Coding Mode</h4><p>Best for code</p></div>
            </div>
        </div>

        <div class="panel-section">
            <div class="panel-title">
                <h3>Tools</h3>
                <span>View all</span>
            </div>
            <div class="tool-item"><div class="tool-icon">🔍</div><div class="tool-info"><h4>Web Search</h4><p>Search the internet</p></div></div>
            <div class="tool-item"><div class="tool-icon">🖼️</div><div class="tool-info"><h4>Image Generator</h4><p>Create from text</p></div></div>
            <div class="tool-item"><div class="tool-icon">📄</div><div class="tool-info"><h4>Doc Analyzer</h4><p>Analyze any file</p></div></div>
            <div class="tool-item"><div class="tool-icon">🔊</div><div class="tool-info"><h4>AI Voice Chat</h4><p>Talk with Nexo</p></div></div>
            <div class="tool-item"><div class="tool-icon">▶️</div><div class="tool-info"><h4>YouTube Summary</h4><p>Summarize videos</p></div></div>
        </div>

        <div class="panel-section">
            <h3 style="font-size:13px;font-weight:700;color:#d0d0e8;margin-bottom:10px;">Daily Usage</h3>
            <div class="usage-section">
                <div class="usage-header">
                    <span>Messages used</span>
                    <span>79%</span>
                </div>
                <div class="usage-bar"><div class="usage-fill"></div></div>
                <div class="usage-reset">Resets in 10:30:45</div>
                <button class="upgrade-small">Upgrade for unlimited</button>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)
