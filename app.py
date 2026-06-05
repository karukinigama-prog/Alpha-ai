import streamlit as st
from groq import Groq
from datetime import datetime
import re

# ── Page Config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Nexo AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── System Prompt ─────────────────────────────────────────────────
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

MODE_ADDONS = {
    "Smart":    "",
    "Fast":     "\n\nIMPORTANT: Fast Mode active. Keep all responses short and direct — 2-4 sentences max unless code is needed. Zero fluff.",
    "Creative": "\n\nIMPORTANT: Creative Mode active. Be imaginative, exploratory, unconventional. Surprise the user with creative angles.",
    "Coding":   "\n\nIMPORTANT: Coding Mode active. Pure technical focus. Provide complete, production-ready code. Minimize prose.",
}

# ── Session State ─────────────────────────────────────────────────
for k, v in {
    "messages": [],
    "mode": "Smart",
    "sidebar": False,
    "history": [],
    "ikey": 0,
    "thinking": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Groq ──────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    try:
        import os
        k = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY",""))
        if k: return Groq(api_key=k)
    except: pass
    return None

client = get_client()

def call_groq(msgs, mode):
    if not client:
        return "⚠️ GROQ_API_KEY not found. Please add it in Streamlit secrets."
    sys = SYSTEM_PROMPT + MODE_ADDONS.get(mode, "")
    try:
        r = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role":"system","content":sys}] + msgs,
            max_tokens=4096,
            temperature=0.3 if mode=="Fast" else 0.7,
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {e}"

# ── Helpers ───────────────────────────────────────────────────────
def ts(): return datetime.now().strftime("%I:%M %p")

def md2html(t):
    t = re.sub(r'```(\w*)\n(.*?)```', lambda m: f'<pre><code class="lang-{m.group(1)}">{m.group(2).replace("<","&lt;").replace(">","&gt;")}</code></pre>', t, flags=re.DOTALL)
    t = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\*(.+?)\*', r'<em>\1</em>', t)
    t = re.sub(r'^### (.+)$', r'<h3>\1</h3>', t, flags=re.MULTILINE)
    t = re.sub(r'^## (.+)$',  r'<h2>\1</h2>', t, flags=re.MULTILINE)
    t = re.sub(r'^# (.+)$',   r'<h1>\1</h1>', t, flags=re.MULTILINE)
    t = re.sub(r'^[\-\*] (.+)$', r'<li>\1</li>', t, flags=re.MULTILINE)
    t = re.sub(r'(<li>.*?</li>\n?)+', lambda m: f'<ul>{m.group()}</ul>', t, flags=re.DOTALL)
    t = re.sub(r'^\d+\. (.+)$', r'<oli>\1</oli>', t, flags=re.MULTILINE)
    t = re.sub(r'(<oli>.*?</oli>\n?)+', lambda m: f'<ol>{"".join("<li>"+x+"</li>" for x in re.findall(r"<oli>(.*?)</oli>", m.group()))}</ol>', t, flags=re.DOTALL)
    t = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', t, flags=re.MULTILINE)
    t = re.sub(r'\n\n', '<br><br>', t)
    t = re.sub(r'\n(?!<)', '<br>', t)
    return t

MODE_CFG = {
    "Smart":    {"icon":"🌟","desc":"Best for most tasks",  "color":"#8b5cf6"},
    "Fast":     {"icon":"⚡","desc":"Quick answers",         "color":"#f59e0b"},
    "Creative": {"icon":"🎨","desc":"More creative",         "color":"#ec4899"},
    "Coding":   {"icon":"</>","desc":"Best for code",        "color":"#10b981"},
}

LOGO = """<svg width="W" height="H" viewBox="0 0 28 34" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="lg1" x1="0" y1="0" x2="0.6" y2="1"><stop offset="0%" stop-color="#fb923c"/><stop offset="45%" stop-color="#f43f5e"/><stop offset="100%" stop-color="#a855f7"/></linearGradient>
    <linearGradient id="lg2" x1="0.4" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#a855f7"/><stop offset="50%" stop-color="#3b82f6"/><stop offset="100%" stop-color="#22d3ee"/></linearGradient>
  </defs>
  <path d="M5 3C5 3 1 10 1 16C1 22 5 28 13 31C13 31 7 24 9 17C10.5 12 14 10 14 10C14 10 11 17 15.5 19.5C18 21 21 19 21 16.5C21 14 18.5 9 16 5C21 10 23 17 20.5 23.5C25 19 27 14.5 24.5 8C22 3 18 1 14 1Z" fill="url(#lg1)"/>
  <path d="M14 7C14 7 18.5 12 18.5 18.5C18.5 23 16 27.5 13 31C22 28.5 27 22 27 15C27 8 22 3.5 17.5 1.5C20 4 21.5 8.5 19.5 13C18.5 15.5 16.5 16.5 15.5 15.5C14.5 14.5 15.5 11 14 7Z" fill="url(#lg2)"/>
</svg>"""

def logo(w=28, h=34):
    return LOGO.replace("W", str(w)).replace("H", str(h))

# ── CSS ───────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body,.stApp{{background:#0a0a0f!important;color:#e2e2f0!important;font-family:'Inter',sans-serif!important;overflow-x:hidden!important}}
#MainMenu,footer,header,.stDeployButton{{visibility:hidden!important;display:none!important}}
section[data-testid="stSidebar"],div[data-testid="stSidebarNav"],div[data-testid="collapsedControl"]{{display:none!important}}
.main .block-container{{padding:0!important;max-width:100%!important;margin:0!important}}
div[data-testid="stVerticalBlock"]{{gap:0!important}}
div[data-testid="stHorizontalBlock"]{{gap:0!important}}

/* ── Layout Shell ── */
.nx-shell{{display:flex;flex-direction:column;height:100vh;overflow:hidden}}

/* ── Topbar ── */
.nx-top{{
  display:flex;align-items:center;justify-content:space-between;
  height:56px;padding:0 18px;
  background:rgba(8,8,16,0.97);
  border-bottom:1px solid rgba(255,255,255,0.07);
  position:fixed;top:0;left:0;right:0;z-index:2000;
  backdrop-filter:blur(24px);
}}
.nx-top-left{{display:flex;align-items:center;gap:12px}}
.nx-hamburger{{display:flex;flex-direction:column;gap:4.5px;cursor:pointer;padding:7px 6px;border-radius:7px;transition:background .15s}}
.nx-hamburger:hover{{background:rgba(255,255,255,0.08)}}
.nx-hamburger span{{width:18px;height:1.8px;background:#9090b8;border-radius:1px;display:block;transition:all .25s}}
.nx-logo-wrap{{display:flex;align-items:center;gap:8px;text-decoration:none}}
.nx-logo-text{{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:19px;background:linear-gradient(135deg,#fb923c,#ec4899,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.nx-search{{
  display:flex;align-items:center;gap:8px;
  background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
  border-radius:10px;padding:7px 14px;color:#6060a0;font-size:13px;cursor:pointer;
  min-width:200px;transition:border-color .2s;
}}
.nx-search:hover{{border-color:rgba(139,92,246,0.3)}}
.nx-search span{{margin-left:auto;font-size:11px;background:rgba(255,255,255,0.07);padding:2px 6px;border-radius:5px}}
.nx-top-right{{display:flex;align-items:center;gap:10px}}
.nx-icon-btn{{width:34px;height:34px;border-radius:8px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.07);display:flex;align-items:center;justify-content:center;cursor:pointer;color:#8080a8;font-size:15px;transition:all .2s}}
.nx-icon-btn:hover{{background:rgba(255,255,255,0.1);color:#c0c0e8}}
.nx-user{{display:flex;align-items:center;gap:9px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:5px 12px 5px 7px;cursor:pointer;transition:border-color .2s}}
.nx-user:hover{{border-color:rgba(139,92,246,0.3)}}
.nx-avatar{{width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#8b5cf6,#ec4899);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;color:#fff;flex-shrink:0}}
.nx-uname{{font-size:12px;font-weight:600;color:#d8d8f0}}
.nx-uplan{{font-size:10px;color:#6060a0}}

/* ── Sidebar Overlay ── */
.nx-overlay{{position:fixed;top:56px;left:0;right:0;bottom:0;background:rgba(0,0,0,0.55);z-index:1500;display:none}}
.nx-overlay.open{{display:block}}
.nx-sidebar{{
  position:fixed;top:56px;left:0;bottom:0;width:260px;
  background:#0d0d1a;border-right:1px solid rgba(255,255,255,0.06);
  z-index:1600;padding:14px 12px;overflow-y:auto;
  transform:translateX(-100%);transition:transform .18s ease;
}}
.nx-sidebar.open{{transform:translateX(0)}}
.nx-sidebar::-webkit-scrollbar{{width:3px}}
.nx-sidebar::-webkit-scrollbar-thumb{{background:rgba(255,255,255,0.08);border-radius:2px}}
.nx-new-chat{{
  display:flex;align-items:center;justify-content:center;gap:7px;
  width:100%;padding:10px 14px;margin-bottom:18px;
  background:linear-gradient(135deg,#7c3aed,#ec4899);
  border:none;border-radius:10px;color:#fff;font-weight:600;font-size:13px;cursor:pointer;
  transition:opacity .2s;font-family:'Inter',sans-serif;
}}
.nx-new-chat:hover{{opacity:.85}}
.nx-sec-lbl{{font-size:10.5px;font-weight:600;color:#44445a;text-transform:uppercase;letter-spacing:.08em;margin-bottom:5px;padding:0 4px}}
.nx-nav-item{{display:flex;align-items:center;gap:9px;padding:9px 10px;border-radius:8px;font-size:13px;color:#7070a0;cursor:pointer;transition:all .15s;margin-bottom:2px}}
.nx-nav-item:hover{{background:rgba(255,255,255,0.05);color:#c8c8e8}}
.nx-nav-item.active{{background:rgba(139,92,246,0.14);color:#a78bfa}}
.nx-hist-item{{padding:8px 10px;border-radius:8px;font-size:12px;color:#545470;cursor:pointer;transition:all .15s;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.nx-hist-item:hover{{background:rgba(255,255,255,0.04);color:#9090b8}}
.nx-hist-time{{font-size:10px;color:#363650;float:right}}
.nx-upgrade-box{{background:linear-gradient(135deg,rgba(124,58,237,.18),rgba(236,72,153,.12));border:1px solid rgba(139,92,246,.25);border-radius:12px;padding:14px;margin-top:18px}}
.nx-upgrade-box h4{{font-size:13px;font-weight:700;color:#e0e0f8;margin-bottom:8px}}
.nx-upgrade-box ul{{list-style:none;font-size:11.5px;color:#8080a8;margin-bottom:10px;line-height:1.8}}
.nx-upgrade-box ul li::before{{content:"✓ ";color:#a78bfa}}
.nx-upgrade-btn{{width:100%;padding:9px;background:linear-gradient(135deg,#7c3aed,#ec4899);border:none;border-radius:8px;color:#fff;font-size:12.5px;font-weight:600;cursor:pointer;font-family:'Inter',sans-serif}}

/* ── Body ── */
.nx-body{{display:flex;height:calc(100vh - 56px);margin-top:56px;overflow:hidden}}

/* ── Chat Column ── */
.nx-chat{{flex:1;display:flex;flex-direction:column;overflow:hidden;min-width:0}}

/* ── Welcome ── */
.nx-welcome{{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px 20px;text-align:center;overflow-y:auto}}
.nx-welcome-logo{{margin-bottom:18px}}
.nx-welcome-title{{font-family:'Space Grotesk',sans-serif;font-size:36px;font-weight:700;color:#fff;margin-bottom:6px;letter-spacing:-.5px}}
.nx-welcome-sub{{font-size:15px;color:#50507a;margin-bottom:40px}}
.nx-hero-card{{
  background:linear-gradient(135deg,rgba(124,58,237,.12),rgba(236,72,153,.08));
  border:1px solid rgba(139,92,246,.2);border-radius:18px;
  padding:28px 32px;max-width:580px;width:100%;margin-bottom:30px;position:relative;overflow:hidden;
}}
.nx-hero-card::before{{content:'';position:absolute;top:-40px;right:-40px;width:150px;height:150px;border-radius:50%;background:radial-gradient(circle,rgba(139,92,246,.15),transparent);}}
.nx-hero-greeting{{font-size:22px;font-weight:700;color:#fff;margin-bottom:6px}}
.nx-hero-greeting span{{font-size:22px}}
.nx-hero-sub{{font-size:14px;color:#6868a0}}
.nx-quick-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;max-width:560px;width:100%;margin-bottom:20px}}
.nx-quick-btn{{display:flex;align-items:center;gap:8px;padding:11px 16px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);border-radius:12px;color:#9090b8;font-size:13px;cursor:pointer;transition:all .2s;text-align:left}}
.nx-quick-btn:hover{{background:rgba(255,255,255,0.08);color:#d0d0f0;border-color:rgba(255,255,255,.13)}}
.nx-quick-btn .qi{{font-size:16px;flex-shrink:0}}

/* ── Messages ── */
.nx-messages{{flex:1;overflow-y:auto;padding:20px 20px 8px}}
.nx-messages::-webkit-scrollbar{{width:4px}}
.nx-messages::-webkit-scrollbar-thumb{{background:rgba(255,255,255,0.08);border-radius:2px}}
.nx-msg-wrap{{max-width:860px;margin:0 auto 20px}}
.nx-msg-row{{display:flex;align-items:flex-start;gap:10px}}
.nx-msg-row.user{{flex-direction:row-reverse}}
.nx-msg-av{{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;flex-shrink:0}}
.nx-msg-av.ai{{background:linear-gradient(135deg,#7c3aed,#ec4899)}}
.nx-msg-av.user{{background:linear-gradient(135deg,#0ea5e9,#6366f1);color:#fff}}
.nx-msg-meta{{display:flex;align-items:center;gap:7px;margin-bottom:5px}}
.nx-msg-row.user .nx-msg-meta{{flex-direction:row-reverse}}
.nx-msg-name{{font-size:12px;font-weight:600;color:#a78bfa}}
.nx-mode-badge{{font-size:10px;padding:2px 8px;border-radius:8px;border:1px solid;font-weight:500}}
.nx-mode-badge.Smart{{background:rgba(139,92,246,.15);color:#c4b5fd;border-color:rgba(139,92,246,.25)}}
.nx-mode-badge.Fast{{background:rgba(245,158,11,.15);color:#fbbf24;border-color:rgba(245,158,11,.25)}}
.nx-mode-badge.Creative{{background:rgba(236,72,153,.15);color:#f472b6;border-color:rgba(236,72,153,.25)}}
.nx-mode-badge.Coding{{background:rgba(16,185,129,.15);color:#34d399;border-color:rgba(16,185,129,.25)}}
.nx-msg-time{{font-size:11px;color:#363650;margin-left:auto}}
.nx-msg-row.user .nx-msg-time{{margin-left:0;margin-right:auto}}
.nx-bubble{{padding:13px 16px;border-radius:14px;font-size:14px;line-height:1.7;max-width:calc(100% - 90px)}}
.nx-bubble.ai{{background:#131320;border:1px solid rgba(255,255,255,0.07);color:#d0d0e8;border-top-left-radius:4px}}
.nx-bubble.user{{background:linear-gradient(135deg,rgba(124,58,237,.28),rgba(236,72,153,.18));border:1px solid rgba(139,92,246,.28);color:#f0f0ff;border-top-right-radius:4px}}
.nx-bubble pre{{background:#09090f!important;border:1px solid rgba(255,255,255,.08)!important;border-radius:9px!important;padding:14px!important;overflow-x:auto!important;margin:10px 0!important}}
.nx-bubble pre code{{font-family:'Courier New',monospace!important;font-size:12.5px!important;color:#c8d8f8!important;background:transparent!important;padding:0!important}}
.nx-bubble code{{font-family:'Courier New',monospace!important;color:#a78bfa!important;background:rgba(139,92,246,.12)!important;padding:2px 6px!important;border-radius:4px!important;font-size:12.5px!important}}
.nx-bubble h1,.nx-bubble h2,.nx-bubble h3{{color:#e0e0f8;margin:14px 0 6px;font-family:'Space Grotesk',sans-serif}}
.nx-bubble ul,.nx-bubble ol{{padding-left:20px;margin:8px 0}}
.nx-bubble li{{margin-bottom:4px;color:#c0c0e0}}
.nx-bubble strong{{color:#f0f0ff}}
.nx-bubble blockquote{{border-left:3px solid #7c3aed;padding-left:12px;color:#7070a0;margin:8px 0}}
.nx-bubble table{{width:100%;border-collapse:collapse;font-size:13px;margin:10px 0}}
.nx-bubble th{{background:rgba(139,92,246,.14);color:#d0d0f0;padding:7px 12px;text-align:left;border-bottom:1px solid rgba(255,255,255,.1)}}
.nx-bubble td{{padding:7px 12px;border-bottom:1px solid rgba(255,255,255,.05);color:#b0b0d0}}
.nx-bubble a{{color:#a78bfa;text-decoration:underline}}

/* ── Typing ── */
.nx-typing{{display:flex;align-items:center;gap:5px;padding:14px 16px;background:#131320;border:1px solid rgba(255,255,255,.07);border-radius:14px;border-top-left-radius:4px;width:fit-content}}
.nx-typing-text{{font-size:13px;color:#505078;margin-right:4px}}
.dot{{width:6px;height:6px;border-radius:50%;background:#7c3aed;animation:pulse 1.2s infinite}}
.dot:nth-child(2){{animation-delay:.2s}}.dot:nth-child(3){{animation-delay:.4s}}
@keyframes pulse{{0%,80%,100%{{transform:scale(.7);opacity:.4}}40%{{transform:scale(1);opacity:1}}}}

/* ── Mode Bar ── */
.nx-modebar{{display:flex;gap:6px;padding:10px 20px;border-bottom:1px solid rgba(255,255,255,.04);background:rgba(8,8,16,.8);flex-wrap:wrap}}
.nx-mode-btn{{display:flex;align-items:center;gap:5px;padding:6px 14px;border-radius:20px;font-size:12.5px;font-weight:500;cursor:pointer;border:1px solid rgba(255,255,255,.08);background:transparent;color:#7070a0;transition:all .15s;font-family:'Inter',sans-serif}}
.nx-mode-btn:hover{{background:rgba(255,255,255,.06);color:#c0c0e0}}
.nx-mode-btn.active-Smart{{background:rgba(139,92,246,.18);border-color:rgba(139,92,246,.4);color:#c4b5fd}}
.nx-mode-btn.active-Fast{{background:rgba(245,158,11,.15);border-color:rgba(245,158,11,.35);color:#fbbf24}}
.nx-mode-btn.active-Creative{{background:rgba(236,72,153,.15);border-color:rgba(236,72,153,.35);color:#f472b6}}
.nx-mode-btn.active-Coding{{background:rgba(16,185,129,.15);border-color:rgba(16,185,129,.35);color:#34d399}}

/* ── Input ── */
.nx-input-wrap{{padding:12px 20px 14px;background:rgba(8,8,16,.95);border-top:1px solid rgba(255,255,255,.05);backdrop-filter:blur(20px)}}
.nx-input-box{{max-width:860px;margin:0 auto;background:#111122;border:1px solid rgba(255,255,255,.09);border-radius:14px;padding:12px 16px;transition:border-color .2s}}
.nx-input-box:focus-within{{border-color:rgba(139,92,246,.45)}}
.nx-input-toolbar{{display:flex;align-items:center;gap:6px;margin-top:8px;padding-top:8px;border-top:1px solid rgba(255,255,255,.05);flex-wrap:wrap}}
.nx-chip{{display:flex;align-items:center;gap:4px;padding:5px 10px;border-radius:16px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);font-size:12px;color:#606080;cursor:pointer;transition:all .15s;font-family:'Inter',sans-serif}}
.nx-chip:hover{{background:rgba(255,255,255,.08);color:#b0b0d0}}
.nx-send{{width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#7c3aed,#ec4899);border:none;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:16px;color:#fff;transition:opacity .2s;margin-left:auto;flex-shrink:0}}
.nx-send:hover{{opacity:.82}}
.nx-disclaimer{{text-align:center;font-size:11px;color:#2e2e50;margin-top:8px;max-width:860px;margin-left:auto;margin-right:auto}}

/* ── Right Panel ── */
.nx-right{{width:238px;min-width:238px;background:#0d0d1a;border-left:1px solid rgba(255,255,255,.05);padding:16px 13px;overflow-y:auto}}
.nx-right::-webkit-scrollbar{{width:3px}}
.nx-right::-webkit-scrollbar-thumb{{background:rgba(255,255,255,.07);border-radius:2px}}
.nx-panel-hdr{{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}}
.nx-panel-hdr h3{{font-size:13px;font-weight:700;color:#d0d0f0}}
.nx-panel-hdr span{{font-size:11px;color:#7c3aed;cursor:pointer}}
.nx-panel-hdr span:hover{{color:#a78bfa}}
.nx-model-card{{display:flex;align-items:center;gap:8px;padding:9px 10px;border-radius:9px;cursor:pointer;transition:all .15s;margin-bottom:4px}}
.nx-model-card:hover{{background:rgba(255,255,255,.05)}}
.nx-model-card.sel{{background:rgba(139,92,246,.12);border:1px solid rgba(139,92,246,.22)}}
.nx-model-ic{{width:30px;height:30px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:15px;background:rgba(255,255,255,.05)}}
.nx-model-info h4{{font-size:12px;font-weight:600;color:#d0d0f0}}
.nx-model-info p{{font-size:11px;color:#505070}}
.nx-check{{margin-left:auto;color:#8b5cf6;font-size:14px}}
.nx-tool-row{{display:flex;align-items:center;gap:8px;padding:8px 10px;border-radius:9px;cursor:pointer;transition:all .15s;margin-bottom:4px}}
.nx-tool-row:hover{{background:rgba(255,255,255,.04)}}
.nx-tool-ic{{width:30px;height:30px;border-radius:8px;background:rgba(255,255,255,.05);display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0}}
.nx-tool-info h4{{font-size:12px;font-weight:600;color:#c8c8e8}}
.nx-tool-info p{{font-size:11px;color:#484868}}
.nx-usage-card{{background:rgba(255,255,255,.03);border-radius:10px;padding:13px}}
.nx-usage-hdr{{display:flex;justify-content:space-between;font-size:12px;margin-bottom:8px}}
.nx-usage-hdr span:first-child{{color:#909090}}
.nx-usage-hdr span:last-child{{color:#d8d8f0;font-weight:600}}
.nx-bar{{height:4px;background:rgba(255,255,255,.07);border-radius:2px;overflow:hidden;margin-bottom:6px}}
.nx-bar-fill{{height:100%;background:linear-gradient(90deg,#7c3aed,#ec4899);border-radius:2px;width:79%}}
.nx-reset{{font-size:11px;color:#404060;margin-bottom:10px}}
.nx-upg-btn{{width:100%;padding:9px;background:linear-gradient(135deg,#7c3aed,#ec4899);border:none;border-radius:8px;color:#fff;font-size:12.5px;font-weight:600;cursor:pointer;font-family:'Inter',sans-serif}}
.nx-panel-sec{{margin-bottom:20px}}

/* ── Streamlit widget hacks ── */
.stTextArea textarea{{background:transparent!important;border:none!important;color:#e0e0f8!important;font-size:14px!important;line-height:1.65!important;resize:none!important;outline:none!important;box-shadow:none!important;font-family:'Inter',sans-serif!important;padding:0!important}}
.stTextArea>div>div{{background:transparent!important;border:none!important;box-shadow:none!important}}
.stTextArea{{margin:0!important;padding:0!important}}
label[data-testid="stWidgetLabel"]{{display:none!important}}
div[data-baseweb="textarea"]{{background:transparent!important;border:none!important}}
.stButton>button{{background:transparent!important;border:none!important;color:transparent!important;padding:0!important;min-height:0!important;height:0!important;overflow:hidden!important;position:absolute!important;pointer-events:none!important}}
div[data-testid="stForm"]{{border:none!important;padding:0!important}}
.element-container{{margin:0!important;padding:0!important}}

/* ── Mobile ── */
@media(max-width:900px){{
  .nx-right{{display:none!important}}
  .nx-search{{display:none}}
  .nx-welcome-title{{font-size:26px}}
  .nx-quick-grid{{grid-template-columns:1fr 1fr}}
}}
@media(max-width:520px){{
  .nx-top{{padding:0 10px}}
  .nx-quick-grid{{grid-template-columns:1fr}}
  .nx-messages,.nx-input-wrap{{padding-left:12px;padding-right:12px}}
  .nx-modebar{{padding:8px 12px}}
}}

::-webkit-scrollbar{{width:4px;height:4px}}
::-webkit-scrollbar-track{{background:transparent}}
::-webkit-scrollbar-thumb{{background:rgba(255,255,255,.08);border-radius:2px}}
</style>
""", unsafe_allow_html=True)

# ── Sidebar toggle JS ─────────────────────────────────────────────
sidebar_js = """
<script>
function toggleSidebar() {
    var sb = document.getElementById('nx-sb');
    var ov = document.getElementById('nx-ov');
    var isOpen = sb.classList.contains('open');
    if (isOpen) {
        sb.classList.remove('open');
        ov.classList.remove('open');
    } else {
        sb.classList.add('open');
        ov.classList.add('open');
    }
}
document.addEventListener('click', function(e) {
    var sb = document.getElementById('nx-sb');
    var ov = document.getElementById('nx-ov');
    if (ov && ov.contains(e.target)) {
        sb.classList.remove('open');
        ov.classList.remove('open');
    }
});
</script>
"""

# ── TOP BAR ───────────────────────────────────────────────────────
history_items_html = ""
for h in st.session_state.history[:10]:
    history_items_html += f'<div class="nx-hist-item">{h["title"]}<span class="nx-hist-time">{h["time"]}</span></div>'

sidebar_html = f"""
{sidebar_js}
<div id="nx-ov" class="nx-overlay" onclick="this.classList.remove('open');document.getElementById('nx-sb').classList.remove('open')"></div>
<div id="nx-sb" class="nx-sidebar">
  <button class="nx-new-chat" onclick="document.getElementById('nx-new-chat-trigger').click()">＋ &nbsp;New Chat</button>
  <div class="nx-sec-lbl">Navigation</div>
  <div class="nx-nav-item active">🏠 Home</div>
  <div class="nx-nav-item">🔍 Explore AI Tools</div>
  <div class="nx-nav-item">🤖 AI Models</div>
  <div class="nx-nav-item">📋 Templates</div>
  <div class="nx-nav-item">🕐 Chat History</div>
  {"<div style='margin-top:16px'><div class='nx-sec-lbl'>Recent Chats</div>" + history_items_html + "</div>" if history_items_html else ""}
  <div class="nx-upgrade-box">
    <h4>Upgrade to <span style="color:#a78bfa">Nexo Pro</span></h4>
    <ul>
      <li>Unlimited messages</li>
      <li>Advanced AI models</li>
      <li>Priority support</li>
      <li>Early access features</li>
    </ul>
    <button class="nx-upgrade-btn">👑 Upgrade Now</button>
  </div>
</div>

<div class="nx-top">
  <div class="nx-top-left">
    <div class="nx-hamburger" onclick="toggleSidebar()">
      <span></span><span></span><span></span>
    </div>
    <div class="nx-logo-wrap">
      {logo(26,32)}
      <span class="nx-logo-text">Nexo AI</span>
    </div>
  </div>
  <div class="nx-search">
    <span style="color:#4a4a7a">🔍</span>
    <span>Search anything...</span>
    <span>Ctrl K</span>
  </div>
  <div class="nx-top-right">
    <div class="nx-icon-btn">🌐</div>
    <div class="nx-icon-btn">☀️</div>
    <div class="nx-icon-btn">🔔</div>
    <div class="nx-user">
      <div class="nx-avatar">C</div>
      <div>
        <div class="nx-uname">Chethaka</div>
        <div class="nx-uplan">Pro Plan</div>
      </div>
    </div>
  </div>
</div>
"""
st.markdown(sidebar_html, unsafe_allow_html=True)

# Hidden new chat trigger
col_hidden = st.columns([1])[0]
with col_hidden:
    new_chat = st.button("NEW", key="nx-new-chat-trigger")
    if new_chat:
        if st.session_state.messages:
            first = next((m["content"][:38]+"..." for m in st.session_state.messages if m["role"]=="user"), "Untitled")
            st.session_state.history.insert(0, {"title": first, "time": ts()})
        st.session_state.messages = []
        st.session_state.ikey += 1
        st.rerun()

# ── BODY ──────────────────────────────────────────────────────────
st.markdown('<div class="nx-body">', unsafe_allow_html=True)

# ── Mode bar ──────────────────────────────────────────────────────
mode_cols = st.columns([1,1,1,1,8])
mode_keys = list(MODE_CFG.keys())
for i, mk in enumerate(mode_keys):
    with mode_cols[i]:
        if st.button(
            f"{MODE_CFG[mk]['icon']} {mk}",
            key=f"mb_{mk}",
            use_container_width=True,
        ):
            st.session_state.mode = mk
            st.rerun()

# Render modebar HTML (visual)
modebar_html = '<div class="nx-modebar">'
for mk, mc in MODE_CFG.items():
    active = "active-"+mk if st.session_state.mode == mk else ""
    modebar_html += f'<button class="nx-mode-btn {active}" onclick="document.getElementById(\'mb_{mk}\').click()">{mc["icon"]} {mk}</button>'
modebar_html += '</div>'
st.markdown(modebar_html, unsafe_allow_html=True)

# ── Chat + Right Panel wrapper ─────────────────────────────────────
left_c, right_c = st.columns([1, 0.28])

with left_c:
    st.markdown('<div class="nx-chat">', unsafe_allow_html=True)

    if not st.session_state.messages:
        # Welcome
        st.markdown(f"""
        <div class="nx-welcome">
          <div class="nx-welcome-logo">{logo(72,88)}</div>
          <div class="nx-welcome-title">Nexo AI</div>
          <div class="nx-welcome-sub">Smart. Fast. Limitless.</div>
          <div class="nx-hero-card">
            <div class="nx-hero-greeting"><span>👋</span> Hello, I'm Nexo AI</div>
            <div class="nx-hero-sub">What can I help you create today?</div>
          </div>
          <div class="nx-quick-grid">
            <div class="nx-quick-btn"><span class="qi">💡</span> Build a website</div>
            <div class="nx-quick-btn"><span class="qi">🎨</span> Design a logo</div>
            <div class="nx-quick-btn"><span class="qi">📚</span> Explain a topic</div>
            <div class="nx-quick-btn"><span class="qi">&lt;/&gt;</span> Write code</div>
            <div class="nx-quick-btn"><span class="qi">✍️</span> Draft an email</div>
            <div class="nx-quick-btn"><span class="qi">📊</span> Analyze data</div>
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        # Messages
        st.markdown('<div class="nx-messages">', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            content_html = md2html(msg["content"])
            m = msg.get("mode", "Smart")
            if msg["role"] == "assistant":
                icon = MODE_CFG.get(m, MODE_CFG["Smart"])["icon"]
                st.markdown(f"""
                <div class="nx-msg-wrap">
                  <div class="nx-msg-row">
                    <div class="nx-msg-av ai">{logo(18,22)}</div>
                    <div style="flex:1;min-width:0">
                      <div class="nx-msg-meta">
                        <span class="nx-msg-name">Nexo AI</span>
                        <span class="nx-mode-badge {m}">{icon} {m} Mode</span>
                        <span class="nx-msg-time">{msg.get('ts','')}</span>
                      </div>
                      <div class="nx-bubble ai">{content_html}</div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="nx-msg-wrap">
                  <div class="nx-msg-row user">
                    <div class="nx-msg-av user">C</div>
                    <div style="flex:1;min-width:0">
                      <div class="nx-msg-meta">
                        <span class="nx-msg-time">{msg.get('ts','')}</span>
                      </div>
                      <div class="nx-bubble user">{msg['content']}</div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Input ──
    st.markdown('<div class="nx-input-wrap"><div class="nx-input-box">', unsafe_allow_html=True)
    user_input = st.text_area(
        "msg",
        key=f"inp_{st.session_state.ikey}",
        placeholder="Ask Nexo anything...",
        height=56,
        label_visibility="collapsed",
    )
    st.markdown("""
    <div class="nx-input-toolbar">
      <button class="nx-chip">🔍 Search</button>
      <button class="nx-chip">💭 Reason</button>
      <button class="nx-chip">🖼️ Create image</button>
      <button class="nx-chip">&lt;/&gt; Code</button>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # input-box

    send_c1, send_c2 = st.columns([11, 1])
    with send_c2:
        send = st.button("➤", key="send_btn")

    if send and user_input and user_input.strip():
        txt = user_input.strip()
        st.session_state.messages.append({"role":"user","content":txt,"mode":st.session_state.mode,"ts":ts()})
        api_msgs = [{"role":m["role"],"content":m["content"]} for m in st.session_state.messages]
        with st.spinner(""):
            st.markdown("""<div class="nx-msg-wrap"><div class="nx-msg-row"><div class="nx-msg-av ai">N</div>
            <div class="nx-typing"><span class="nx-typing-text">Nexo is thinking</span>
            <div class="dot"></div><div class="dot"></div><div class="dot"></div></div></div></div>""", unsafe_allow_html=True)
            reply = call_groq(api_msgs, st.session_state.mode)
        st.session_state.messages.append({"role":"assistant","content":reply,"mode":st.session_state.mode,"ts":ts()})
        st.session_state.ikey += 1
        st.rerun()

    st.markdown('<div class="nx-disclaimer">Nexo AI may make mistakes. Consider checking important information.</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)  # input-wrap, nx-chat

# ── RIGHT PANEL ───────────────────────────────────────────────────
with right_c:
    cur_mode = st.session_state.mode
    models_html = ""
    for mk, mc in MODE_CFG.items():
        sel = "sel" if mk == cur_mode else ""
        chk = '<span class="nx-check">✓</span>' if mk == cur_mode else ""
        models_html += f"""
        <div class="nx-model-card {sel}">
          <div class="nx-model-ic">{mc['icon']}</div>
          <div class="nx-model-info"><h4>{mk} Mode</h4><p>{mc['desc']}</p></div>
          {chk}
        </div>"""

    st.markdown(f"""
    <div class="nx-right">
      <div class="nx-panel-sec">
        <div class="nx-panel-hdr"><h3>AI Models</h3><span>View all</span></div>
        {models_html}
      </div>
      <div class="nx-panel-sec">
        <div class="nx-panel-hdr"><h3>Tools</h3><span>View all</span></div>
        <div class="nx-tool-row"><div class="nx-tool-ic">🔍</div><div class="nx-tool-info"><h4>Web Search</h4><p>Search the internet</p></div></div>
        <div class="nx-tool-row"><div class="nx-tool-ic">🖼️</div><div class="nx-tool-info"><h4>Image Generator</h4><p>Create from text</p></div></div>
        <div class="nx-tool-row"><div class="nx-tool-ic">📄</div><div class="nx-tool-info"><h4>Document Analyzer</h4><p>Analyze any file</p></div></div>
        <div class="nx-tool-row"><div class="nx-tool-ic">🔊</div><div class="nx-tool-info"><h4>AI Voice Chat</h4><p>Talk with Nexo</p></div></div>
        <div class="nx-tool-row"><div class="nx-tool-ic">▶️</div><div class="nx-tool-info"><h4>YouTube Summarizer</h4><p>Summarize videos</p></div></div>
        <div class="nx-tool-row"><div class="nx-tool-ic">&lt;/&gt;</div><div class="nx-tool-info"><h4>Code Interpreter</h4><p>Run &amp; analyze code</p></div></div>
      </div>
      <div class="nx-panel-sec">
        <div class="nx-panel-hdr"><h3>Daily Usage</h3></div>
        <div class="nx-usage-card">
          <div class="nx-usage-hdr"><span>79% used</span></div>
          <div class="nx-bar"><div class="nx-bar-fill"></div></div>
          <div class="nx-reset">Resets in 10:30:45</div>
          <button class="nx-upg-btn">Upgrade for unlimited</button>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # nx-body
