import streamlit as st
import groq
import base64
import json
import time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import io
from datetime import datetime

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Groq Vision · AI Analysis Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS — Cyberpunk Dark-Metallic Theme ────────────────────────────────
st.markdown("""
<style>
  /* ── Google Font ── */
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');

  /* ── Root & Background ── */
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

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
      background: linear-gradient(180deg, #050d14 0%, #0a1628 50%, #050d14 100%) !important;
      border-right: 1px solid rgba(0,200,255,0.2) !important;
  }
  [data-testid="stSidebar"]::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 2px;
      background: linear-gradient(90deg, transparent, #00c8ff, #00ff9d, transparent);
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
  code, pre, .stCode {
      font-family: 'Share Tech Mono', monospace !important;
  }

  /* ── Metric Cards ── */
  [data-testid="metric-container"] {
      background: linear-gradient(135deg, #0a1628 0%, #0d1f35 100%);
      border: 1px solid rgba(0,200,255,0.25);
      border-radius: 8px;
      padding: 16px !important;
      box-shadow: 0 0 20px rgba(0,200,255,0.08), inset 0 0 20px rgba(0,0,0,0.3);
  }
  [data-testid="metric-container"]:hover {
      border-color: rgba(0,255,157,0.5);
      box-shadow: 0 0 30px rgba(0,255,157,0.15);
      transition: all 0.3s ease;
  }
  [data-testid="stMetricValue"] {
      font-family: 'Orbitron', monospace !important;
      color: #00ff9d !important;
      font-size: 1.8rem !important;
  }
  [data-testid="stMetricLabel"] {
      font-family: 'Rajdhani', sans-serif !important;
      color: #6a9ab0 !important;
      letter-spacing: 0.1em;
  }

  /* ── Buttons ── */
  .stButton > button {
      background: linear-gradient(135deg, #003d5c 0%, #00263d 100%) !important;
      color: #00c8ff !important;
      border: 1px solid rgba(0,200,255,0.4) !important;
      border-radius: 6px !important;
      font-family: 'Orbitron', monospace !important;
      font-size: 12px !important;
      letter-spacing: 0.1em !important;
      padding: 10px 24px !important;
      text-transform: uppercase;
      transition: all 0.3s ease !important;
  }
  .stButton > button:hover {
      background: linear-gradient(135deg, #005580 0%, #003a5c 100%) !important;
      border-color: #00ff9d !important;
      color: #00ff9d !important;
      box-shadow: 0 0 20px rgba(0,255,157,0.3) !important;
  }

  /* ── Inputs ── */
  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea {
      background: #040c16 !important;
      border: 1px solid rgba(0,200,255,0.2) !important;
      border-radius: 6px !important;
      color: #c8d8e8 !important;
      font-family: 'Share Tech Mono', monospace !important;
  }
  .stTextInput > div > div > input:focus,
  .stTextArea > div > div > textarea:focus {
      border-color: #00c8ff !important;
      box-shadow: 0 0 10px rgba(0,200,255,0.2) !important;
  }

  /* ── Select boxes ── */
  .stSelectbox > div > div {
      background: #040c16 !important;
      border: 1px solid rgba(0,200,255,0.2) !important;
      color: #c8d8e8 !important;
      border-radius: 6px !important;
  }

  /* ── File uploader ── */
  [data-testid="stFileUploaderDropzone"] {
      background: #040c16 !important;
      border: 2px dashed rgba(0,200,255,0.3) !important;
      border-radius: 8px !important;
  }
  [data-testid="stFileUploaderDropzone"]:hover {
      border-color: #00ff9d !important;
      background: #050f1a !important;
  }

  /* ── Expander ── */
  .streamlit-expanderHeader {
      background: #0a1628 !important;
      border: 1px solid rgba(0,200,255,0.2) !important;
      border-radius: 6px !important;
      font-family: 'Orbitron', monospace !important;
      font-size: 12px !important;
      color: #00c8ff !important;
  }

  /* ── Divider ── */
  hr {
      border-color: rgba(0,200,255,0.15) !important;
  }

  /* ── Custom panel cards ── */
  .panel-card {
      background: linear-gradient(135deg, #080f1a 0%, #0d1f35 100%);
      border: 1px solid rgba(0,200,255,0.2);
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 16px;
      box-shadow: 0 4px 24px rgba(0,0,0,0.5), inset 0 0 30px rgba(0,0,0,0.2);
  }
  .panel-title {
      font-family: 'Orbitron', monospace;
      font-size: 11px;
      letter-spacing: 0.2em;
      color: #00c8ff;
      text-transform: uppercase;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid rgba(0,200,255,0.15);
  }
  .status-online {
      display: inline-block;
      width: 8px; height: 8px;
      background: #00ff9d;
      border-radius: 50%;
      box-shadow: 0 0 8px #00ff9d;
      margin-right: 6px;
      animation: pulse 2s infinite;
  }
  .status-offline {
      display: inline-block;
      width: 8px; height: 8px;
      background: #ff4444;
      border-radius: 50%;
      box-shadow: 0 0 8px #ff4444;
      margin-right: 6px;
  }
  @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.4; }
  }
  .log-entry {
      font-family: 'Share Tech Mono', monospace;
      font-size: 12px;
      color: #00ff9d;
      background: #020810;
      border-left: 3px solid #00c8ff;
      padding: 8px 12px;
      margin: 4px 0;
      border-radius: 0 4px 4px 0;
  }
  .header-glow {
      font-family: 'Orbitron', monospace;
      font-size: 28px;
      font-weight: 900;
      background: linear-gradient(90deg, #00c8ff, #00ff9d, #00c8ff);
      background-size: 200%;
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      animation: shimmer 3s linear infinite;
  }
  @keyframes shimmer {
      0% { background-position: 0% 50%; }
      100% { background-position: 200% 50%; }
  }
  .subheader-dim {
      font-family: 'Rajdhani', sans-serif;
      font-size: 13px;
      color: #3a6a80;
      letter-spacing: 0.2em;
      text-transform: uppercase;
  }
  /* scrollbar */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #020408; }
  ::-webkit-scrollbar-thumb { background: #003d5c; border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: #00c8ff; }

  /* hide streamlit default header/footer */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)


# ── Session State Initialization ─────────────────────────────────────────────
def init_session_state():
    defaults = {
        "analysis_log":      [],
        "latency_history":   [],
        "token_history":     [],
        "timestamps":        [],
        "total_requests":    0,
        "total_tokens":      0,
        "avg_latency":       0.0,
        "last_result":       None,
        "groq_client":       None,
        "api_key_valid":     False,
        "processing":        False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()


# ── Helper: encode image to base64 ───────────────────────────────────────────
def encode_image(image: Image.Image, max_size: int = 1024) -> tuple[str, str]:
    """Resize if needed, convert to base64. Returns (b64_string, media_type)."""
    w, h = image.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        image = image.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=90)
    b64 = base64.standard_b64encode(buffer.getvalue()).decode("utf-8")
    return b64, "image/jpeg"


# ── Helper: validate Groq API key ─────────────────────────────────────────────
def validate_api_key(api_key: str) -> bool:
    if not api_key or len(api_key) < 20:
        return False
    try:
        client = groq.Groq(api_key=api_key)
        client.models.list()
        return True
    except Exception:
        return False


# ── Core: Groq Vision Analysis ────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an advanced AI Vision Analysis Engine. Your role is to perform thorough, structured visual analysis of any image provided to you.

You MUST respond with ONLY a valid JSON object — no markdown, no code fences, no explanations outside the JSON.

The JSON structure must be exactly:
{
  "environment_status": {
    "scene_type": "<indoor/outdoor/abstract/document/screenshot/other>",
    "dominant_elements": ["<element1>", "<element2>", "..."],
    "spatial_layout": "<description of how elements are arranged>",
    "color_palette": ["<primary color>", "<secondary color>", "..."],
    "lighting_conditions": "<description of lighting>",
    "notable_objects": [
      {"object": "<name>", "location": "<position in frame>", "confidence": <0.0-1.0>}
    ],
    "text_detected": "<any visible text, or 'none'>",
    "image_quality": "<excellent/good/fair/poor>"
  },
  "analytical_reasoning": {
    "primary_subject": "<what is the main focus of this image>",
    "context_inference": "<what situation or scenario does this image represent>",
    "key_observations": ["<observation1>", "<observation2>", "<observation3>"],
    "anomalies_or_highlights": "<anything unusual or particularly noteworthy>",
    "confidence_score": <overall confidence 0.0-1.0>
  },
  "strategic_actions": [
    {"priority": 1, "action": "<recommended action or insight>", "rationale": "<why this action>"},
    {"priority": 2, "action": "<recommended action or insight>", "rationale": "<why this action>"},
    {"priority": 3, "action": "<recommended action or insight>", "rationale": "<why this action>"}
  ]
}"""


def run_groq_analysis(
    api_key: str,
    model: str,
    image: Image.Image,
    custom_prompt: str = "",
) -> dict:
    """Send image to Groq, return parsed result dict with timing metadata."""

    client = groq.Groq(api_key=api_key)
    b64_image, media_type = encode_image(image)

    user_text = custom_prompt.strip() if custom_prompt.strip() else (
        "Analyze this image thoroughly and return the structured JSON as instructed."
    )

    start = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{b64_image}"
                        },
                    },
                    {"type": "text", "text": user_text},
                ],
            },
        ],
        max_tokens=1500,
        temperature=0.2,
    )
    elapsed = round((time.time() - start) * 1000, 1)

    raw_text = response.choices[0].message.content.strip()

    # Safe JSON parse
    try:
        raw_text_clean = raw_text
        if raw_text_clean.startswith("```"):
            raw_text_clean = raw_text_clean.split("```")[-2] if "```" in raw_text_clean else raw_text_clean
            raw_text_clean = raw_text_clean.lstrip("json").strip()
        parsed = json.loads(raw_text_clean)
    except json.JSONDecodeError:
        parsed = {"raw_response": raw_text, "parse_error": "Model returned non-JSON output"}

    usage = response.usage
    return {
        "result":          parsed,
        "latency_ms":      elapsed,
        "prompt_tokens":   usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens":    usage.total_tokens,
        "model":           model,
        "timestamp":       datetime.now().strftime("%H:%M:%S"),
        "raw":             raw_text,
    }


# ── Plotly chart helpers ───────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(5,15,25,0.8)",
    font=dict(family="Share Tech Mono", color="#6a9ab0", size=11),
    margin=dict(l=40, r=20, t=30, b=40),
    xaxis=dict(gridcolor="rgba(0,200,255,0.06)", linecolor="rgba(0,200,255,0.15)"),
    yaxis=dict(gridcolor="rgba(0,200,255,0.06)", linecolor="rgba(0,200,255,0.15)"),
)


def make_latency_chart(timestamps, latencies):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(latencies))),
        y=latencies,
        mode="lines+markers",
        name="Latency (ms)",
        line=dict(color="#00c8ff", width=2),
        marker=dict(color="#00ff9d", size=6, symbol="circle"),
        fill="tozeroy",
        fillcolor="rgba(0,200,255,0.05)",
        hovertemplate="<b>%{y:.0f} ms</b><extra></extra>",
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text="API RESPONSE LATENCY", font=dict(family="Orbitron", color="#00c8ff", size=11)),
        yaxis_title="ms",
        showlegend=False,
        height=220,
    )
    return fig


def make_token_chart(token_history):
    if not token_history:
        return go.Figure()
    df_data = {
        "Index":      list(range(len(token_history))),
        "Prompt":     [t["prompt"] for t in token_history],
        "Completion": [t["completion"] for t in token_history],
    }
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_data["Index"], y=df_data["Prompt"],
        name="Prompt", marker_color="rgba(0,200,255,0.6)",
    ))
    fig.add_trace(go.Bar(
        x=df_data["Index"], y=df_data["Completion"],
        name="Completion", marker_color="rgba(0,255,157,0.6)",
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        barmode="stack",
        title=dict(text="TOKEN USAGE PER REQUEST", font=dict(family="Orbitron", color="#00c8ff", size=11)),
        height=220,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            font=dict(color="#6a9ab0", size=10),
        ),
    )
    return fig


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px 0;'>
        <div style='font-family:Orbitron,monospace; font-size:18px; font-weight:900;
                    background:linear-gradient(90deg,#00c8ff,#00ff9d);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    background-clip:text;'>
            GROQ VISION
        </div>
        <div style='font-family:Rajdhani,sans-serif; font-size:11px;
                    color:#3a6a80; letter-spacing:0.25em; margin-top:4px;'>
            AI ANALYSIS ENGINE v2.0
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── API Key ──
    st.markdown('<p class="panel-title">🔑 &nbsp;API CONFIGURATION</p>', unsafe_allow_html=True)
    api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_••••••••••••••••••••",
        help="Get your key at console.groq.com",
    )

    if api_key:
        if not st.session_state.api_key_valid:
            with st.spinner("Validating key…"):
                valid = validate_api_key(api_key)
            st.session_state.api_key_valid = valid
            if valid:
                st.session_state.groq_client = groq.Groq(api_key=api_key)
        if st.session_state.api_key_valid:
            st.markdown('<span class="status-online"></span><span style="color:#00ff9d;font-size:12px;font-family:Rajdhani,sans-serif;">API CONNECTED</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-offline"></span><span style="color:#ff4444;font-size:12px;font-family:Rajdhani,sans-serif;">INVALID KEY</span>', unsafe_allow_html=True)
            st.session_state.api_key_valid = False
    else:
        st.markdown('<span class="status-offline"></span><span style="color:#3a6a80;font-size:12px;font-family:Rajdhani,sans-serif;">NOT CONFIGURED</span>', unsafe_allow_html=True)

    st.markdown("---")

    # ── Model Selection ──
    st.markdown('<p class="panel-title">🤖 &nbsp;MODEL SELECTION</p>', unsafe_allow_html=True)
    VISION_MODELS = {
        "meta-llama/llama-4-scout-17b-16e-instruct": "Llama 4 Scout 17B · 16E Instruct ★",
        "meta-llama/llama-4-maverick-17b-128e-instruct": "Llama 4 Maverick 17B · 128E",
        "llama-3.2-90b-vision-preview":               "Llama 3.2 · 90B Vision",
        "llama-3.2-11b-vision-preview":               "Llama 3.2 · 11B Vision",
    }
    selected_model = st.selectbox(
        "Vision Model",
        options=list(VISION_MODELS.keys()),
        format_func=lambda x: VISION_MODELS[x],
        index=0,
    )

    st.markdown("---")

    # ── Analysis Settings ──
    st.markdown('<p class="panel-title">⚙️ &nbsp;ANALYSIS SETTINGS</p>', unsafe_allow_html=True)
    custom_prompt = st.text_area(
        "Custom Instruction (optional)",
        placeholder="e.g. Focus on text elements only…",
        height=80,
    )
    max_img_size = st.slider("Max Image Dimension (px)", 256, 1920, 1024, 64)
    auto_clear_log = st.checkbox("Auto-clear log after 20 entries", value=True)

    st.markdown("---")

    # ── Stats ──
    st.markdown('<p class="panel-title">📊 &nbsp;SESSION STATS</p>', unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    s1.metric("Requests", st.session_state.total_requests)
    s2.metric("Tokens", f"{st.session_state.total_tokens:,}")
    if st.session_state.latency_history:
        avg = round(sum(st.session_state.latency_history) / len(st.session_state.latency_history), 1)
        st.metric("Avg Latency", f"{avg} ms")

    if st.button("🗑  Clear Session Data", use_container_width=True):
        st.session_state.analysis_log     = []
        st.session_state.latency_history  = []
        st.session_state.token_history    = []
        st.session_state.timestamps       = []
        st.session_state.total_requests   = 0
        st.session_state.total_tokens     = 0
        st.session_state.last_result      = None
        st.rerun()


# ── Main Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style='display:flex; align-items:center; justify-content:space-between;
            border-bottom: 1px solid rgba(0,200,255,0.15); padding-bottom:16px; margin-bottom:24px;'>
    <div>
        <div class='header-glow'>GROQ VISION ANALYSIS DASHBOARD</div>
        <div class='subheader-dim' style='margin-top:4px;'>
            Real-time AI image understanding · Powered by Groq LPU™
        </div>
    </div>
    <div style='text-align:right;'>
        <div style='font-family:Share Tech Mono,monospace; font-size:11px; color:#3a6a80;'>
            SYSTEM READY
        </div>
        <div style='font-family:Share Tech Mono,monospace; font-size:20px; color:#00ff9d;'>
            ◉ ONLINE
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Top KPI Strip ─────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Analyses", st.session_state.total_requests, delta=None)
k2.metric(
    "Last Latency",
    f"{st.session_state.latency_history[-1]} ms" if st.session_state.latency_history else "—",
)
k3.metric(
    "Peak Latency",
    f"{max(st.session_state.latency_history):.0f} ms" if st.session_state.latency_history else "—",
)
k4.metric("Total Tokens Used", f"{st.session_state.total_tokens:,}")

st.markdown("<br>", unsafe_allow_html=True)


# ── Row 1: Image Upload + Viewport ───────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">📡 &nbsp;IMAGE INPUT — FRAME VIEWPORT</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload image frame for analysis",
        type=["jpg", "jpeg", "png", "bmp", "webp"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True, caption=f"Frame: {uploaded_file.name}")
        st.markdown(f"""
        <div style='font-family:Share Tech Mono,monospace; font-size:11px; color:#3a6a80;
                    margin-top:8px; padding:8px; background:#020810; border-radius:4px;'>
            ▸ FILE&nbsp;&nbsp;&nbsp;{uploaded_file.name}<br>
            ▸ SIZE&nbsp;&nbsp;&nbsp;{uploaded_file.size:,} bytes<br>
            ▸ MODE&nbsp;&nbsp;&nbsp;{image.mode} &nbsp;|&nbsp; {image.size[0]}×{image.size[1]} px
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='height:280px; display:flex; flex-direction:column; align-items:center;
                    justify-content:center; border:1px dashed rgba(0,200,255,0.15);
                    border-radius:8px; color:#2a4a5c; font-family:Share Tech Mono,monospace;
                    font-size:12px;'>
            <div style='font-size:40px; margin-bottom:12px; opacity:0.3;'>⬆</div>
            <div>AWAITING FRAME INPUT</div>
            <div style='font-size:10px; margin-top:6px; opacity:0.6;'>JPG · PNG · BMP · WEBP</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🧠 &nbsp;ANALYSIS CONTROL</div>', unsafe_allow_html=True)

    if not api_key or not st.session_state.api_key_valid:
        st.warning("⚠ Configure a valid Groq API key in the sidebar to enable analysis.")
    elif not uploaded_file:
        st.info("ℹ Upload an image frame to the left to begin analysis.")
    else:
        model_label = VISION_MODELS.get(selected_model, selected_model)
        st.markdown(f"""
        <div style='padding:12px; background:#020810; border-radius:6px; margin-bottom:16px;
                    border:1px solid rgba(0,200,255,0.1);'>
            <div style='font-family:Orbitron,monospace; font-size:10px; color:#3a6a80;
                        letter-spacing:0.15em; margin-bottom:6px;'>READY TO ANALYZE</div>
            <div style='font-family:Rajdhani,sans-serif; font-size:14px; color:#c8d8e8;'>
                Model&nbsp;&nbsp;&nbsp;<span style='color:#00c8ff;'>{model_label}</span>
            </div>
            <div style='font-family:Rajdhani,sans-serif; font-size:14px; color:#c8d8e8;'>
                Frame&nbsp;&nbsp;&nbsp;<span style='color:#00ff9d;'>{uploaded_file.name}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        analyze_btn = st.button(
            "⚡  EXECUTE VISION ANALYSIS",
            use_container_width=True,
            disabled=st.session_state.processing,
        )

        if analyze_btn:
            st.session_state.processing = True
            with st.spinner("🔄 Transmitting frame to Groq LPU…"):
                try:
                    img = Image.open(uploaded_file)
                    data = run_groq_analysis(
                        api_key=api_key,
                        model=selected_model,
                        image=img,
                        custom_prompt=custom_prompt,
                    )

                    # update session state
                    st.session_state.last_result = data
                    st.session_state.latency_history.append(data["latency_ms"])
                    st.session_state.token_history.append({
                        "prompt":     data["prompt_tokens"],
                        "completion": data["completion_tokens"],
                    })
                    st.session_state.timestamps.append(data["timestamp"])
                    st.session_state.total_requests += 1
                    st.session_state.total_tokens   += data["total_tokens"]

                    log_entry = {
                        "seq":       st.session_state.total_requests,
                        "timestamp": data["timestamp"],
                        "model":     data["model"].split("/")[-1],
                        "latency_ms": data["latency_ms"],
                        "tokens":    data["total_tokens"],
                        "result":    data["result"],
                    }
                    st.session_state.analysis_log.insert(0, log_entry)

                    if auto_clear_log and len(st.session_state.analysis_log) > 20:
                        st.session_state.analysis_log = st.session_state.analysis_log[:20]

                    st.success(f"✓ Analysis complete in {data['latency_ms']} ms")

                except groq.RateLimitError:
                    st.error("⚠ Rate limit reached. Please wait a moment before retrying.")
                except groq.AuthenticationError:
                    st.error("⚠ Authentication failed. Please check your API key.")
                    st.session_state.api_key_valid = False
                except Exception as e:
                    st.error(f"⚠ Analysis failed: {str(e)}")
                finally:
                    st.session_state.processing = False
            st.rerun()

    if st.session_state.last_result:
        d = st.session_state.last_result
        st.markdown("---")
        st.markdown(f"""
        <div style='font-family:Share Tech Mono,monospace; font-size:11px;'>
            <div style='color:#3a6a80; margin-bottom:4px;'>LAST RESPONSE METADATA</div>
            <div style='color:#00c8ff;'>⏱ {d["latency_ms"]} ms latency</div>
            <div style='color:#00ff9d;'>🔤 {d["total_tokens"]} tokens
                ({d["prompt_tokens"]} prompt + {d["completion_tokens"]} completion)</div>
            <div style='color:#6a9ab0;'>🤖 {d["model"].split("/")[-1]}</div>
            <div style='color:#6a9ab0;'>🕐 {d["timestamp"]}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ── Row 2: AI Reasoning Log ───────────────────────────────────────────────────
st.markdown('<div class="panel-card">', unsafe_allow_html=True)
st.markdown('<div class="panel-title">🔬 &nbsp;AI REASONING LOG — STRUCTURED OUTPUT</div>', unsafe_allow_html=True)

if not st.session_state.analysis_log:
    st.markdown("""
    <div style='text-align:center; padding:40px; color:#2a4a5c;
                font-family:Share Tech Mono,monospace; font-size:12px;'>
        <div style='font-size:30px; margin-bottom:10px; opacity:0.3;'>◈</div>
        NO ANALYSIS DATA YET — AWAITING FIRST FRAME
    </div>
    """, unsafe_allow_html=True)
else:
    for entry in st.session_state.analysis_log:
        with st.expander(
            f"[{entry['seq']:03d}]  {entry['timestamp']}  ·  "
            f"{entry['model']}  ·  {entry['latency_ms']} ms  ·  {entry['tokens']} tokens",
            expanded=(entry == st.session_state.analysis_log[0]),
        ):
            st.json(entry["result"])

st.markdown("</div>", unsafe_allow_html=True)


# ── Row 3: Analytics Charts ───────────────────────────────────────────────────
ch1, ch2 = st.columns(2, gap="large")

with ch1:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">📈 &nbsp;LATENCY TREND</div>', unsafe_allow_html=True)
    if st.session_state.latency_history:
        st.plotly_chart(
            make_latency_chart(
                st.session_state.timestamps,
                st.session_state.latency_history
            ),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    else:
        st.markdown("""
        <div style='height:180px; display:flex; align-items:center; justify-content:center;
                    color:#2a4a5c; font-family:Share Tech Mono,monospace; font-size:11px;'>
            NO LATENCY DATA YET
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with ch2:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🔢 &nbsp;TOKEN USAGE</div>', unsafe_allow_html=True)
    if st.session_state.token_history:
        st.plotly_chart(
            make_token_chart(st.session_state.token_history),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    else:
        st.markdown("""
        <div style='height:180px; display:flex; align-items:center; justify-content:center;
                    color:#2a4a5c; font-family:Share Tech Mono,monospace; font-size:11px;'>
            NO TOKEN DATA YET
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ── Row 4: Last Raw Result Preview ────────────────────────────────────────────
if st.session_state.last_result:
    with st.expander("🗃  RAW JSON RESPONSE — LAST REQUEST", expanded=False):
        r = st.session_state.last_result["result"]

        if "environment_status" in r:
            st.markdown("#### 🌐 Environment Status")
            st.json(r["environment_status"])

        if "analytical_reasoning" in r:
            st.markdown("#### 🧠 Analytical Reasoning")
            st.json(r["analytical_reasoning"])

        if "strategic_actions" in r:
            st.markdown("#### ⚡ Strategic Actions")
            for action in r["strategic_actions"]:
                st.markdown(f"""
                <div class='log-entry'>
                    [{action.get('priority', '?')}] &nbsp;
                    <strong>{action.get('action', '')}</strong><br>
                    <span style='color:#3a6a80;'>↳ {action.get('rationale', '')}</span>
                </div>
                """, unsafe_allow_html=True)

        if "parse_error" in r:
            st.warning(f"Parse warning: {r['parse_error']}")
            st.code(r.get("raw_response", ""), language="text")


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding:24px 0 8px 0;
            border-top:1px solid rgba(0,200,255,0.08); margin-top:20px;'>
    <div style='font-family:Share Tech Mono,monospace; font-size:10px; color:#1a3a4c;
                letter-spacing:0.2em;'>
        GROQ VISION ANALYSIS DASHBOARD &nbsp;·&nbsp;
        POWERED BY GROQ LPU™ &nbsp;·&nbsp;
        BUILT WITH STREAMLIT
    </div>
</div>
""", unsafe_allow_html=True)
