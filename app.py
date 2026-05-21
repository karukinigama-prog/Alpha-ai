import streamlit as st
import groq
import base64
import json
import time
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import io
from datetime import datetime

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Groq Vision · AI Analysis Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",  # mobile වලට collapsed
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');

  html, body, [data-testid="stAppViewContainer"] {
      background: #020408 !important;
      color: #c8d8e8 !important;
  }
  [data-testid="stAppViewContainer"]::before {
      content: '';
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background:
          repeating-linear-gradient(0deg, transparent, transparent 60px,
              rgba(0,255,200,0.015) 60px, rgba(0,255,200,0.015) 61px),
          repeating-linear-gradient(90deg, transparent, transparent 60px,
              rgba(0,255,200,0.015) 60px, rgba(0,255,200,0.015) 61px);
      pointer-events: none;
      z-index: 0;
  }

  /* ── Sidebar (desktop only) ── */
  [data-testid="stSidebar"] {
      background: linear-gradient(180deg, #050d14 0%, #0a1628 50%, #050d14 100%) !important;
      border-right: 1px solid rgba(0,200,255,0.2) !important;
  }

  /* ── Typography ── */
  h1, h2, h3 {
      font-family: 'Orbitron', monospace !important;
      letter-spacing: 0.08em;
  }
  p, div, span, label {
      font-family: 'Rajdhani', sans-serif !important;
      font-size: 15px;
  }
  code, pre {
      font-family: 'Share Tech Mono', monospace !important;
  }

  /* ── Metric Cards ── */
  [data-testid="metric-container"] {
      background: linear-gradient(135deg, #0a1628 0%, #0d1f35 100%);
      border: 1px solid rgba(0,200,255,0.25);
      border-radius: 8px;
      padding: 12px !important;
      box-shadow: 0 0 20px rgba(0,200,255,0.08);
  }
  [data-testid="stMetricValue"] {
      font-family: 'Orbitron', monospace !important;
      color: #00ff9d !important;
      font-size: 1.4rem !important;
  }
  [data-testid="stMetricLabel"] {
      font-family: 'Rajdhani', sans-serif !important;
      color: #6a9ab0 !important;
      font-size: 11px !important;
      letter-spacing: 0.1em;
  }

  /* ── Buttons ── */
  .stButton > button {
      background: linear-gradient(135deg, #003d5c 0%, #00263d 100%) !important;
      color: #00c8ff !important;
      border: 1px solid rgba(0,200,255,0.4) !important;
      border-radius: 6px !important;
      font-family: 'Orbitron', monospace !important;
      font-size: 11px !important;
      letter-spacing: 0.1em !important;
      text-transform: uppercase;
      transition: all 0.3s ease !important;
      width: 100%;
  }
  .stButton > button:hover {
      border-color: #00ff9d !important;
      color: #00ff9d !important;
      box-shadow: 0 0 20px rgba(0,255,157,0.3) !important;
  }

  /* ── Inputs ── */
  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea {
      background: #040c16 !important;
      border: 1px solid rgba(0,200,255,0.25) !important;
      border-radius: 6px !important;
      color: #c8d8e8 !important;
      font-family: 'Share Tech Mono', monospace !important;
      font-size: 13px !important;
  }
  .stTextInput > div > div > input:focus {
      border-color: #00c8ff !important;
      box-shadow: 0 0 10px rgba(0,200,255,0.2) !important;
  }

  /* ── Selectbox ── */
  .stSelectbox > div > div {
      background: #040c16 !important;
      border: 1px solid rgba(0,200,255,0.25) !important;
      color: #c8d8e8 !important;
      border-radius: 6px !important;
  }

  /* ── File uploader ── */
  [data-testid="stFileUploaderDropzone"] {
      background: #040c16 !important;
      border: 2px dashed rgba(0,200,255,0.3) !important;
      border-radius: 8px !important;
  }

  /* ── Expander ── */
  .streamlit-expanderHeader {
      background: #0a1628 !important;
      border: 1px solid rgba(0,200,255,0.2) !important;
      border-radius: 6px !important;
      font-family: 'Orbitron', monospace !important;
      font-size: 11px !important;
      color: #00c8ff !important;
  }
  .streamlit-expanderContent {
      background: #050d18 !important;
      border: 1px solid rgba(0,200,255,0.1) !important;
      border-top: none !important;
  }

  /* ── Tab styling ── */
  .stTabs [data-baseweb="tab-list"] {
      background: #040c16;
      border-bottom: 1px solid rgba(0,200,255,0.2);
      gap: 4px;
  }
  .stTabs [data-baseweb="tab"] {
      font-family: 'Orbitron', monospace !important;
      font-size: 10px !important;
      letter-spacing: 0.1em;
      color: #3a6a80 !important;
      background: transparent !important;
      border: 1px solid transparent !important;
      border-radius: 4px 4px 0 0 !important;
      padding: 8px 16px !important;
  }
  .stTabs [aria-selected="true"] {
      color: #00c8ff !important;
      border-color: rgba(0,200,255,0.3) !important;
      background: #0a1628 !important;
  }

  /* ── Custom panel cards ── */
  .panel-card {
      background: linear-gradient(135deg, #080f1a 0%, #0d1f35 100%);
      border: 1px solid rgba(0,200,255,0.2);
      border-radius: 10px;
      padding: 16px;
      margin-bottom: 16px;
  }
  .panel-title {
      font-family: 'Orbitron', monospace;
      font-size: 10px;
      letter-spacing: 0.2em;
      color: #00c8ff;
      text-transform: uppercase;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid rgba(0,200,255,0.15);
  }
  .status-dot-green {
      display: inline-block;
      width: 8px; height: 8px;
      background: #00ff9d;
      border-radius: 50%;
      box-shadow: 0 0 8px #00ff9d;
      margin-right: 6px;
      animation: pulse 2s infinite;
  }
  .status-dot-red {
      display: inline-block;
      width: 8px; height: 8px;
      background: #ff4444;
      border-radius: 50%;
      box-shadow: 0 0 8px #ff4444;
      margin-right: 6px;
  }
  @keyframes pulse {
      0%,100%{opacity:1} 50%{opacity:0.3}
  }
  .log-entry {
      font-family: 'Share Tech Mono', monospace;
      font-size: 11px;
      color: #00ff9d;
      background: #020810;
      border-left: 3px solid #00c8ff;
      padding: 8px 12px;
      margin: 4px 0;
      border-radius: 0 4px 4px 0;
  }
  .header-glow {
      font-family: 'Orbitron', monospace;
      font-weight: 900;
      background: linear-gradient(90deg, #00c8ff, #00ff9d, #00c8ff);
      background-size: 200%;
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      animation: shimmer 3s linear infinite;
  }
  @keyframes shimmer {
      0%{background-position:0% 50%} 100%{background-position:200% 50%}
  }

  /* ── Mobile responsive ── */
  @media (max-width: 768px) {
      .header-glow { font-size: 20px !important; }
      [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
      .panel-card { padding: 12px; }
      .panel-title { font-size: 9px; }
      .block-container { padding: 0.5rem 0.8rem !important; }
  }

  /* ── Config panel box ── */
  .config-box {
      background: #040c16;
      border: 1px solid rgba(0,200,255,0.2);
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 12px;
  }

  /* hide default header/footer */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1rem !important; }

  /* scrollbar */
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: #020408; }
  ::-webkit-scrollbar-thumb { background: #003d5c; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "analysis_log":    [],
        "latency_history": [],
        "token_history":   [],
        "timestamps":      [],
        "total_requests":  0,
        "total_tokens":    0,
        "last_result":     None,
        "api_key_valid":   False,
        "processing":      False,
        "saved_api_key":   "",
        "saved_model":     "meta-llama/llama-4-scout-17b-16e-instruct",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ── Helpers ───────────────────────────────────────────────────────────────────
def encode_image(image: Image.Image, max_size: int = 1024) -> tuple:
    w, h = image.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        image = image.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=90)
    b64 = base64.standard_b64encode(buf.getvalue()).decode("utf-8")
    return b64, "image/jpeg"


def validate_api_key(key: str) -> bool:
    if not key or len(key) < 20:
        return False
    try:
        client = groq.Groq(api_key=key)
        client.models.list()
        return True
    except Exception:
        return False


SYSTEM_PROMPT = """You are an advanced AI Vision Analysis Engine. Respond ONLY with a valid JSON object — no markdown, no code fences, no text outside JSON.

Required structure:
{
  "environment_status": {
    "scene_type": "<indoor/outdoor/abstract/document/screenshot/other>",
    "dominant_elements": ["<element1>", "<element2>"],
    "spatial_layout": "<how elements are arranged>",
    "color_palette": ["<color1>", "<color2>"],
    "lighting_conditions": "<lighting description>",
    "notable_objects": [
      {"object": "<name>", "location": "<position>", "confidence": <0.0-1.0>}
    ],
    "text_detected": "<visible text or none>",
    "image_quality": "<excellent/good/fair/poor>"
  },
  "analytical_reasoning": {
    "primary_subject": "<main focus>",
    "context_inference": "<what situation this represents>",
    "key_observations": ["<obs1>", "<obs2>", "<obs3>"],
    "anomalies_or_highlights": "<anything unusual>",
    "confidence_score": <0.0-1.0>
  },
  "strategic_actions": [
    {"priority": 1, "action": "<recommended action>", "rationale": "<why>"},
    {"priority": 2, "action": "<recommended action>", "rationale": "<why>"},
    {"priority": 3, "action": "<recommended action>", "rationale": "<why>"}
  ]
}"""


def run_analysis(api_key, model, image, custom_prompt=""):
    client = groq.Groq(api_key=api_key)
    b64, media_type = encode_image(image)
    user_text = custom_prompt.strip() or "Analyze this image and return the structured JSON."

    t0 = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "image_url",
                 "image_url": {"url": f"data:{media_type};base64,{b64}"}},
                {"type": "text", "text": user_text},
            ]},
        ],
        max_tokens=1500,
        temperature=0.2,
    )
    elapsed = round((time.time() - t0) * 1000, 1)
    raw = response.choices[0].message.content.strip()

    try:
        clean = raw
        if "```" in clean:
            parts = clean.split("```")
            clean = parts[1].lstrip("json").strip() if len(parts) > 1 else clean
        parsed = json.loads(clean)
    except json.JSONDecodeError:
        parsed = {"raw_response": raw, "parse_error": "Non-JSON output from model"}

    u = response.usage
    return {
        "result": parsed, "latency_ms": elapsed,
        "prompt_tokens": u.prompt_tokens,
        "completion_tokens": u.completion_tokens,
        "total_tokens": u.total_tokens,
        "model": model,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "raw": raw,
    }


# ── Plotly Charts ─────────────────────────────────────────────────────────────
BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(5,15,25,0.8)",
    font=dict(family="Share Tech Mono", color="#6a9ab0", size=10),
    margin=dict(l=36, r=10, t=28, b=36),
    xaxis=dict(gridcolor="rgba(0,200,255,0.06)", linecolor="rgba(0,200,255,0.1)"),
    yaxis=dict(gridcolor="rgba(0,200,255,0.06)", linecolor="rgba(0,200,255,0.1)"),
)

def latency_chart():
    lh = st.session_state.latency_history
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(lh))), y=lh,
        mode="lines+markers",
        line=dict(color="#00c8ff", width=2),
        marker=dict(color="#00ff9d", size=5),
        fill="tozeroy", fillcolor="rgba(0,200,255,0.05)",
        hovertemplate="<b>%{y:.0f} ms</b><extra></extra>",
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="LATENCY (ms)", font=dict(family="Orbitron", color="#00c8ff", size=10)),
        height=200, showlegend=False,
    )
    return fig

def token_chart():
    th = st.session_state.token_history
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(range(len(th))),
        y=[t["prompt"] for t in th],
        name="Prompt", marker_color="rgba(0,200,255,0.6)",
    ))
    fig.add_trace(go.Bar(
        x=list(range(len(th))),
        y=[t["completion"] for t in th],
        name="Completion", marker_color="rgba(0,255,157,0.6)",
    ))
    fig.update_layout(
        **BASE_LAYOUT, barmode="stack",
        title=dict(text="TOKENS / REQUEST", font=dict(family="Orbitron", color="#00c8ff", size=10)),
        height=200,
        legend=dict(orientation="h", y=1.1, font=dict(size=9, color="#6a9ab0")),
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE LAYOUT STARTS HERE
# ══════════════════════════════════════════════════════════════════════════════

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='border-bottom:1px solid rgba(0,200,255,0.15);
            padding-bottom:12px; margin-bottom:16px;
            display:flex; justify-content:space-between; align-items:flex-start;'>
  <div>
    <div class='header-glow' style='font-size:clamp(16px,5vw,28px);'>
      GROQ VISION ANALYSIS
    </div>
    <div style='font-family:Rajdhani,sans-serif; font-size:11px;
                color:#3a6a80; letter-spacing:0.2em; margin-top:2px;'>
      REAL-TIME AI IMAGE UNDERSTANDING · GROQ LPU™
    </div>
  </div>
  <div style='text-align:right;'>
    <div style='font-family:Share Tech Mono,monospace; font-size:9px; color:#3a6a80;'>
      SYSTEM READY
    </div>
    <div style='font-family:Orbitron,monospace; font-size:14px; color:#00ff9d;'>
      ◉ ONLINE
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── KPI Row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Analyses", st.session_state.total_requests)
k2.metric("Last ms",
    f"{st.session_state.latency_history[-1]:.0f}" if st.session_state.latency_history else "—")
k3.metric("Peak ms",
    f"{max(st.session_state.latency_history):.0f}" if st.session_state.latency_history else "—")
k4.metric("Tokens", f"{st.session_state.total_tokens:,}")

st.markdown("<br>", unsafe_allow_html=True)


# ── TABS — Config / Analyze / Logs / Analytics ────────────────────────────────
tab_cfg, tab_analyze, tab_logs, tab_analytics = st.tabs([
    "⚙  CONFIG",
    "🔬  ANALYZE",
    "📋  LOG",
    "📈  ANALYTICS",
])


# ═══════════════════════════ TAB 1 — CONFIG ═══════════════════════════════════
with tab_cfg:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🔑 API CONFIGURATION</div>', unsafe_allow_html=True)

    api_key_input = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_••••••••••••••••••••••",
        value=st.session_state.saved_api_key,
        help="Get your free key at console.groq.com",
        key="api_key_field",
    )

    col_validate, col_clear = st.columns(2)
    with col_validate:
        if st.button("✓  VALIDATE KEY", use_container_width=True):
            if api_key_input:
                with st.spinner("Connecting to Groq…"):
                    valid = validate_api_key(api_key_input)
                st.session_state.api_key_valid = valid
                st.session_state.saved_api_key = api_key_input if valid else ""
                if valid:
                    st.success("✓ API key valid — connected!")
                else:
                    st.error("✗ Invalid key. Check and retry.")
            else:
                st.warning("Enter your API key first.")
    with col_clear:
        if st.button("✗  CLEAR KEY", use_container_width=True):
            st.session_state.api_key_valid = False
            st.session_state.saved_api_key = ""
            st.rerun()

    # Status indicator
    if st.session_state.api_key_valid:
        st.markdown('<div style="margin-top:10px;"><span class="status-dot-green"></span>'
                    '<span style="color:#00ff9d;font-size:13px;font-family:Rajdhani,sans-serif;">'
                    'API CONNECTED &amp; READY</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="margin-top:10px;"><span class="status-dot-red"></span>'
                    '<span style="color:#ff4444;font-size:13px;font-family:Rajdhani,sans-serif;">'
                    'NOT CONNECTED</span></div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Model selection ──
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🤖 MODEL SELECTION</div>', unsafe_allow_html=True)

    MODELS = {
        "meta-llama/llama-4-scout-17b-16e-instruct": "★  Llama 4 Scout 17B · 16E Instruct",
        "meta-llama/llama-4-maverick-17b-128e-instruct": "Llama 4 Maverick 17B · 128E",
        "llama-3.2-90b-vision-preview": "Llama 3.2 · 90B Vision",
        "llama-3.2-11b-vision-preview": "Llama 3.2 · 11B Vision (fast)",
    }

    selected_model = st.selectbox(
        "Vision Model",
        options=list(MODELS.keys()),
        format_func=lambda x: MODELS[x],
        index=list(MODELS.keys()).index(st.session_state.saved_model)
            if st.session_state.saved_model in MODELS else 0,
    )
    st.session_state.saved_model = selected_model

    st.markdown(f"""
    <div style='margin-top:8px; padding:8px 12px; background:#020810;
                border-radius:4px; font-family:Share Tech Mono,monospace; font-size:11px;'>
        <span style='color:#3a6a80;'>ACTIVE MODEL ▸ </span>
        <span style='color:#00c8ff;'>{selected_model.split("/")[-1]}</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Session controls ──
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🗂 SESSION CONTROLS</div>', unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    s1.metric("Total Requests", st.session_state.total_requests)
    s2.metric("Total Tokens", f"{st.session_state.total_tokens:,}")
    if st.button("🗑  CLEAR ALL SESSION DATA", use_container_width=True):
        for key in ["analysis_log","latency_history","token_history",
                    "timestamps","total_requests","total_tokens","last_result"]:
            st.session_state[key] = [] if isinstance(st.session_state[key], list) else \
                                    0 if isinstance(st.session_state[key], int) else \
                                    0.0 if isinstance(st.session_state[key], float) else None
        st.success("Session cleared.")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════ TAB 2 — ANALYZE ══════════════════════════════════
with tab_analyze:

    # ── Guard: API key required ──
    if not st.session_state.api_key_valid or not st.session_state.saved_api_key:
        st.markdown("""
        <div style='text-align:center; padding:40px 20px;
                    border:1px dashed rgba(0,200,255,0.2); border-radius:10px;
                    font-family:Share Tech Mono,monospace;'>
            <div style='font-size:32px; margin-bottom:12px;'>🔑</div>
            <div style='color:#00c8ff; font-size:13px; margin-bottom:6px;'>
                API KEY REQUIRED
            </div>
            <div style='color:#3a6a80; font-size:11px;'>
                Go to ⚙ CONFIG tab → enter your Groq API key → Validate
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── Image upload viewport ──
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">📡 IMAGE INPUT — FRAME VIEWPORT</div>',
                    unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Upload image",
            type=["jpg", "jpeg", "png", "bmp", "webp"],
            label_visibility="collapsed",
        )

        if uploaded:
            img = Image.open(uploaded)
            st.image(img, use_column_width=True,
                     caption=f"▸ {uploaded.name}  ·  {img.size[0]}×{img.size[1]}px  ·  {uploaded.size:,} bytes")
        else:
            st.markdown("""
            <div style='height:200px; display:flex; flex-direction:column;
                        align-items:center; justify-content:center;
                        border:1px dashed rgba(0,200,255,0.15); border-radius:8px;
                        color:#2a4a5c; font-family:Share Tech Mono,monospace; font-size:11px;'>
                <div style='font-size:36px; margin-bottom:10px; opacity:0.3;'>⬆</div>
                <div>AWAITING FRAME INPUT</div>
                <div style='font-size:9px; margin-top:4px; opacity:0.5;'>
                    JPG · PNG · BMP · WEBP
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Custom prompt ──
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">✏ CUSTOM INSTRUCTION (OPTIONAL)</div>',
                    unsafe_allow_html=True)
        custom_prompt = st.text_area(
            "Instruction",
            placeholder="e.g. Focus only on text elements…",
            height=80,
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Analyze button ──
        if uploaded:
            btn_label = "🔄 PROCESSING…" if st.session_state.processing else "⚡ EXECUTE VISION ANALYSIS"
            analyze = st.button(btn_label, use_container_width=True,
                                disabled=st.session_state.processing)

            if analyze:
                st.session_state.processing = True
                with st.spinner("Transmitting frame to Groq LPU…"):
                    try:
                        data = run_analysis(
                            api_key=st.session_state.saved_api_key,
                            model=st.session_state.saved_model,
                            image=Image.open(uploaded),
                            custom_prompt=custom_prompt,
                        )
                        # ── store results ──
                        st.session_state.last_result      = data
                        st.session_state.total_requests  += 1
                        st.session_state.total_tokens    += data["total_tokens"]
                        st.session_state.latency_history.append(data["latency_ms"])
                        st.session_state.token_history.append({
                            "prompt":     data["prompt_tokens"],
                            "completion": data["completion_tokens"],
                        })
                        st.session_state.timestamps.append(data["timestamp"])
                        st.session_state.analysis_log.insert(0, {
                            "seq":        st.session_state.total_requests,
                            "timestamp":  data["timestamp"],
                            "model":      data["model"].split("/")[-1],
                            "latency_ms": data["latency_ms"],
                            "tokens":     data["total_tokens"],
                            "result":     data["result"],
                        })
                        if len(st.session_state.analysis_log) > 20:
                            st.session_state.analysis_log = st.session_state.analysis_log[:20]

                        st.success(f"✓ Done in {data['latency_ms']} ms · {data['total_tokens']} tokens")

                    except groq.RateLimitError:
                        st.error("⚠ Rate limit hit — wait a moment and retry.")
                    except groq.AuthenticationError:
                        st.error("⚠ Auth failed — check your API key in CONFIG tab.")
                        st.session_state.api_key_valid = False
                    except Exception as e:
                        st.error(f"⚠ Error: {str(e)}")
                    finally:
                        st.session_state.processing = False
                st.rerun()

        # ── Last result preview ──
        if st.session_state.last_result:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">🧠 LAST ANALYSIS RESULT</div>',
                        unsafe_allow_html=True)
            r = st.session_state.last_result

            # Metadata strip
            st.markdown(f"""
            <div style='display:flex; gap:20px; flex-wrap:wrap; margin-bottom:12px;
                        font-family:Share Tech Mono,monospace; font-size:11px;'>
                <span style='color:#00c8ff;'>⏱ {r["latency_ms"]} ms</span>
                <span style='color:#00ff9d;'>🔤 {r["total_tokens"]} tokens</span>
                <span style='color:#6a9ab0;'>🤖 {r["model"].split("/")[-1]}</span>
                <span style='color:#6a9ab0;'>🕐 {r["timestamp"]}</span>
            </div>
            """, unsafe_allow_html=True)

            parsed = r["result"]

            if "environment_status" in parsed:
                with st.expander("🌐 ENVIRONMENT STATUS", expanded=True):
                    st.json(parsed["environment_status"])

            if "analytical_reasoning" in parsed:
                with st.expander("🧠 ANALYTICAL REASONING", expanded=True):
                    st.json(parsed["analytical_reasoning"])

            if "strategic_actions" in parsed:
                with st.expander("⚡ STRATEGIC ACTIONS", expanded=True):
                    for act in parsed["strategic_actions"]:
                        st.markdown(f"""
                        <div class='log-entry'>
                            [{act.get("priority","?")}]&nbsp;
                            <strong>{act.get("action","")}</strong><br>
                            <span style='color:#3a6a80;'>↳ {act.get("rationale","")}</span>
                        </div>
                        """, unsafe_allow_html=True)

            if "parse_error" in parsed:
                st.warning(parsed["parse_error"])
                st.code(parsed.get("raw_response", ""), language="text")

            st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════ TAB 3 — LOG ══════════════════════════════════════
with tab_logs:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">📋 AI REASONING LOG — ALL SESSIONS</div>',
                unsafe_allow_html=True)

    if not st.session_state.analysis_log:
        st.markdown("""
        <div style='text-align:center; padding:40px; color:#2a4a5c;
                    font-family:Share Tech Mono,monospace; font-size:11px;'>
            <div style='font-size:28px; margin-bottom:8px; opacity:0.3;'>◈</div>
            NO ANALYSIS DATA YET
        </div>
        """, unsafe_allow_html=True)
    else:
        for entry in st.session_state.analysis_log:
            label = (f"[{entry['seq']:03d}]  {entry['timestamp']}  ·  "
                     f"{entry['model']}  ·  {entry['latency_ms']} ms")
            with st.expander(label, expanded=False):
                st.json(entry["result"])

    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════ TAB 4 — ANALYTICS ════════════════════════════════
with tab_analytics:

    if not st.session_state.latency_history:
        st.markdown("""
        <div style='text-align:center; padding:60px 20px; color:#2a4a5c;
                    font-family:Share Tech Mono,monospace; font-size:11px;'>
            <div style='font-size:32px; margin-bottom:12px; opacity:0.3;'>📊</div>
            <div>RUN AT LEAST ONE ANALYSIS TO SEE METRICS</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        lh = st.session_state.latency_history

        # Summary stats
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">📊 PERFORMANCE SUMMARY</div>',
                    unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Min Latency",   f"{min(lh):.0f} ms")
        m2.metric("Max Latency",   f"{max(lh):.0f} ms")
        m3.metric("Avg Latency",   f"{sum(lh)/len(lh):.0f} ms")
        m4.metric("Requests",      st.session_state.total_requests)
        st.markdown("</div>", unsafe_allow_html=True)

        # Charts
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">📈 LATENCY TREND</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(latency_chart(), use_container_width=True,
                            config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">🔢 TOKEN USAGE</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(token_chart(), use_container_width=True,
                            config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        # Token breakdown table
        if st.session_state.token_history:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">🗃 TOKEN BREAKDOWN TABLE</div>',
                        unsafe_allow_html=True)
            df = pd.DataFrame([
                {
                    "Req #":        i + 1,
                    "Time":         st.session_state.timestamps[i]
                                    if i < len(st.session_state.timestamps) else "—",
                    "Latency (ms)": st.session_state.latency_history[i],
                    "Prompt Tok":   t["prompt"],
                    "Completion":   t["completion"],
                    "Total":        t["prompt"] + t["completion"],
                }
                for i, t in enumerate(st.session_state.token_history)
            ])
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding:20px 0 4px 0;
            border-top:1px solid rgba(0,200,255,0.08); margin-top:16px;'>
    <div style='font-family:Share Tech Mono,monospace; font-size:9px;
                color:#1a3a4c; letter-spacing:0.15em;'>
        GROQ VISION DASHBOARD · GROQ LPU™ · STREAMLIT CLOUD
    </div>
</div>
""", unsafe_allow_html=True)
