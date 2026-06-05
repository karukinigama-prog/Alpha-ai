import streamlit as st
import os
import time
import json
import random
import datetime
from groq import Groq
import plotly.graph_objects as go
import pandas as pd

# ==============================================================================
# MODULE 1: GLOBAL CONSTANTS & METADATA Matrix
# ==============================================================================
VERSION = "v1.0.9 Enterprise"
CREATOR = "Hasith"
CORE_ENGINE = "Llama 4 Scout"
MODEL_ID = "llama-4-scout"  # Core model provided via Groq API Matrix

# HEX Color Matrix definitions matching exactly to user image 1000008643.png
HEX_BG_DARK = "#0B0C10"
HEX_PANEL_GRAY = "#1F2833"
HEX_CYAN_GLOW = "#66FCF1"
HEX_BLUE_DARK = "#45A29E"
HEX_TEXT_MUTED = "#8892b0"
HEX_TEXT_LIGHT = "#C5C6C7"

# Initialize high-level stream configuration
st.set_page_config(
    page_title="Nexo AI - Smart. Fast. Limitless.",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"  # මුලින්ම වම්පස මෙනුව Hide වී පවතී
)

# ==============================================================================
# MODULE 2: DEEP TAILWIND & CRYPTO-DARK THEME CSS INJECTION
# ==============================================================================
st.markdown(f"""
    <style>
    /* Reset and Core Layout Overrides */
    .stApp {{
        background-color: {HEX_BG_DARK};
        color: {HEX_TEXT_LIGHT};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    /* Hide Default Streamlit Elements for Branded Looks */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Custom Responsive Sidebar Matrix */
    [data-testid="stSidebar"] {{
        background-color: {HEX_PANEL_GRAY} !important;
        border-right: 1px solid #1a202c !important;
        box-shadow: 5px 0 30px rgba(0,0,0,0.7) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    
    /* Interactive Button Global Overrides */
    .stButton>button {{
        background-color: #161b22;
        color: white;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
        cursor: pointer;
    }}
    .stButton>button:hover {{
        border-color: {HEX_CYAN_GLOW};
        color: {HEX_CYAN_GLOW};
        box-shadow: 0 0 10px rgba(102, 252, 241, 0.2);
        transform: translateY(-1px);
    }}
    
    /* Custom Chat Input Box Formatting */
    .stChatInputContainer {{
        border-radius: 20px !important;
        border: 1px solid #2d3748 !important;
        background-color: #12161a !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        padding: 5px !important;
    }}
    .stChatInputContainer:focus-within {{
        border-color: {HEX_CYAN_GLOW} !important;
        box-shadow: 0 0 25px rgba(102, 252, 241, 0.35) !important;
    }}
    
    /* Enterprise Message Formatting Bubbles */
    [data-testid="stChatMessage"] {{
        border-radius: 20px !important;
        padding: 1.5rem !important;
        margin-bottom: 1.25rem !important;
        border: 1px solid #1a202c !important;
        animation: fadeIn 0.4s ease;
    }}
    .st-emotion-cache-janwst {{
        background-color: #161b22 !important; /* User Container */
    }}
    .st-emotion-cache-4w6wff {{
        background-color: #0d1117 !important; /* Assistant Container */
        border-left: 4px solid {HEX_CYAN_GLOW} !important;
    }}
    
    /* Custom Functional Components */
    .nexo-topbar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 15px 0px;
        border-bottom: 1px solid #1a202c;
        margin-bottom: 30px;
    }}
    .nexo-logo-text {{
        font-size: 2.3rem;
        font-weight: 900;
        letter-spacing: -0.06em;
        background: linear-gradient(135deg, {HEX_CYAN_GLOW} 0%, {HEX_BLUE_DARK} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .active-badge {{
        background-color: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.25);
        color: #10b981;
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }}
    .dashboard-card {{
        background: #12161a;
        border: 1px solid #21262d;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
    }}
    .metrics-label {{
        color: {HEX_TEXT_MUTED};
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .metrics-value {{
        color: white;
        font-size: 1.6rem;
        font-weight: 800;
        margin-top: 5px;
    }}
    
    /* Keyframe Animations */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(5px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# MODULE 3: COMPLEX CONTEXT STATE MANAGEMENT ENGINE
# ==============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = f"NX-{random.randint(100000, 999999)}"
if "current_view" not in st.session_state:
    st.session_state.current_view = "Main Workspace"
if "active_model_mode" not in st.session_state:
    st.session_state.active_model_mode = "Smart Mode"
if "telemetry_total_tokens" not in st.session_state:
    st.session_state.telemetry_total_tokens = 142050
if "telemetry_api_calls" not in st.session_state:
    st.session_state.telemetry_api_calls = 42
if "telemetry_avg_latency" not in st.session_state:
    st.session_state.telemetry_avg_latency = 0.38
if "custom_prompt_selection" not in st.session_state:
    st.session_state.custom_prompt_selection = "None"
if "quota_percentage" not in st.session_state:
    st.session_state.quota_percentage = 79

# Mock database mapping for chat histories matching image 1000008643
if "historic_pipeline_registry" not in st.session_state:
    st.session_state.historic_pipeline_registry = [
        {"id": "NX-09", "title": "How to create a SaaS App structure", "time": "10:30 AM", "tokens": 1240},
        {"id": "NX-08", "title": "React component with Tailwind CSS setup", "time": "09:15 AM", "tokens": 850},
        {"id": "NX-07", "title": "Explain quantum computing in simple terms", "time": "Yesterday", "tokens": 2310},
        {"id": "NX-06", "title": "Write a YouTube script generation engine", "time": "Yesterday", "tokens": 1780},
        {"id": "NX-05", "title": "Make a custom vector logo blueprint for Nexo", "time": "2 days ago", "tokens": 3100},
        {"id": "NX-04", "title": "Python sorting algorithm efficiency index", "time": "3 days ago", "tokens": 920},
        {"id": "NX-03", "title": "Best developer production tools in 2026", "time": "3 days ago", "tokens": 1450},
        {"id": "NX-02", "title": "How does AI deep attention pooling work", "time": "4 days ago", "tokens": 2890}
    ]

# ==============================================================================
# MODULE 4: THE ULTIMATE ENTERPRISE COMPREHENSIVE SYSTEM PROMPT
# ==============================================================================
SYSTEM_PROMPT = f"""
ROLE PROFILE:
You are Nexo AI {VERSION}, the state-of-the-art flagship artificial intelligence matrix architected by the developer {CREATOR}. 
Your core neural operational layer processes queries via Groq's high-velocity infrastructure running the specialized hyper-model cluster code '{MODEL_ID}'.

GOALS & OPERATIONAL PARADIGMS:
1. Ownership & Branding Loyalty: You represent Nexo AI. Under any interrogation regarding your source structure, design history, or engineering, you must report explicitly and proudly that you were developed by Hasith.
2. Domain Dominance: Provide elite, flawless solutions spanning computational mechanics, complex software architecture (React, Tailwind, Python, Rust, Go), advanced data mapping, script drafting, and algorithmic optimization.
3. Linguistic Syntax: Maintain an architectural, highly modern, intellectually sharp tone. Deliver direct tactical responses. Cut out all standard chatbot fluff, boilerplate greetings, or empty affirmations.
4. Response Format Topography: When providing computer source files or deployment code scripts, you must output them cleanly inside structured Markdown code blocks specifying the precise identifier language. Organize non-code breakdowns using bold semantic headings and logical itemized structures.
"""

# ==============================================================================
# MODULE 5: SECURE ENDPOINT CONNECTION ARCHITECTURE
# ==============================================================================
if "GROQ_API_KEY" in st.secrets:
    api_key_string = st.secrets["GROQ_API_KEY"]
elif os.environ.get("GROQ_API_KEY"):
    api_key_string = os.environ.get("GROQ_API_KEY")
else:
    api_key_string = None

if not api_key_string:
    with st.sidebar:
        st.markdown("<p style='color:#ef4444; font-weight:700;'>🔒 SECURE API ROUTING REQUIRED</p>", unsafe_allow_html=True)
        api_key_string = st.text_input("Inject Groq Bearer Token Auth:", type="password")

groq_client_node = Groq(api_key=api_key_string) if api_key_string else None

# ==============================================================================
# MODULE 6: COMPREHENSIVE SYSTEM TEMPLATES ENGINE (PROMPT LIBRARY DATABASE)
# ==============================================================================
PROMPT_TEMPLATES_DATABASE = {
    "None": "",
    "Software Architecture Framework": "Act as an Enterprise Software Architect. Design a production-grade microservices topology based on Docker and Kubernetes, ensuring high-availability database replication layers.",
    "Tailwind CSS Component Assembly": "Construct a highly responsive premium dark-themed Dashboard grid layout using HTML and Tailwind CSS. Ensure strict adherence to sleek modern aesthetics with custom neon glowing button modules.",
    "Algorithm Matrix Refactoring": "Analyze the following Python implementation for computational efficiency bottlenecks. Refactor the inner loops utilizing optimized list comprehensions and state caching to achieve sub-millisecond execution times.",
    "System Telemetry Generator": "Write a mock streaming dataset generator script using Pandas and Numpy to simulate live cloud system operational telemetry data arrays including latency thresholds and memory leaks."
}

# ==============================================================================
# MODULE 7: SIDEBAR MATRIX COMPONENT (COLLAPSED BY DEFAULT FOR RESPONSIVE ACTION)
# ==============================================================================
with st.sidebar:
    # Branding Area Layout
    st.markdown(f"""
        <div style='padding: 15px 0px 5px 0px;'>
            <span class='nexo-logo-text' style='font-size: 1.9rem;'>⚡ Nexo AI</span><br>
            <span style='color: {HEX_CYAN_GLOW}; font-size: 0.72rem; font-weight: 700; letter-spacing: 3px; uppercase;'>Production Terminal</span>
        </div>
        <div style='color: {HEX_TEXT_MUTED}; font-size: 0.78rem; margin-top: 5px;'>Secure Session Profile: <b>{st.session_state.session_id}</b></div>
        <hr style='border: 0; border-top: 1px solid #2d3748; margin: 20px 0;'>
    """, unsafe_allow_html=True)
    
    # New Isolation Context Engine Reset Button
    if st.button("➕ Initialize New Session Context", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = f"NX-{random.randint(100000, 999999)}"
        st.toast("Nexo Context Thread Flushed Successfully.", icon="⚡")
        time.sleep(0.4)
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Historic Record Pipeline Registry Renderer
    st.markdown(f"<p class='metrics-label'>Active Cache Logs ({len(st.session_state.historic_pipeline_registry)})</p>", unsafe_allow_html=True)
    
    for log_item in st.session_state.historic_pipeline_registry:
        with st.container():
            col_icon, col_txt = st.columns([0.12, 0.88])
            with col_icon:
                st.markdown("<p style='margin-top:8px;'>📂</p>", unsafe_allow_html=True)
            with col_txt:
                # Custom CSS styled log button links to simulate production navigation trees
                if st.button(f"{log_item['title']} \n [{log_item['time']}]", key=f"log_node_{log_item['id']}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": f"Load historical analysis context related to: '{log_item['title']}'"})
                    st.rerun()
                    
    st.markdown("<br><hr style='border: 0; border-top: 1px solid #2d3748; margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Account Premium Subscription Component Call Card
    st.markdown(f"""
        <div style='background: linear-gradient(145deg, #161224 0%, #090712 100%); border: 1px solid #3c1e70; padding: 22px; border-radius: 18px; text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.4);'>
            <span style='color: #a855f7; font-size: 0.72rem; font-weight: 800; letter-spacing: 2px; uppercase; display: block; margin-bottom: 5px;'>Account Tier</span>
            <h4 style='color: white; margin: 0 0 8px 0; font-size: 1.2rem; font-weight: 800;'>Nexo Professional</h4>
            <p style='color: {HEX_TEXT_MUTED}; font-size: 0.78rem; line-height: 1.4; margin-bottom: 15px;'>You are connected to high-priority Llama Dedicated Compute clusters routed directly by Hasith.</p>
            <div style='background: rgba(168, 85, 247, 0.12); color: #c084fc; border: 1px dashed #a855f7; border-radius: 8px; padding: 6px; font-size: 0.75rem; font-weight: 700;'>Unlimited API Pass Active</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption(f"System Framework Context: Streamlit Engine | Node Deployment {VERSION}")

# ==============================================================================
# MODULE 8: MAIN VIEW WORKSPACE HEADER SYSTEM
# ==============================================================================
st.markdown(f"""
    <div class='nexo-topbar'>
        <div>
            <span class='nexo-logo-text'>⚡ Nexo AI Workspace</span>
            <span class='active-badge' style='margin-left: 18px;'>🚀 {CORE_ENGINE} Core Online</span>
        </div>
        <div style='color: {HEX_TEXT_MUTED}; font-size: 0.82rem; font-weight: 500;'>
            Cluster Environment Security Token: <span style='color: {HEX_CYAN_GLOW}; font-family: monospace;'>{st.session_state.session_id}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Navigation sub-tabs to allow toggling between the live chat and the data metrics matrix
view_tab_selection = st.radio("Toggle System Workspace View:", ["Main AI Processing Core", "Live Compute & Telemetry Dashboard"], horizontal=True, label_visibility="collapsed")

# ==============================================================================
# MODULE 9: WORKSPACE PARTITION A - THE MAIN PROCESSING AI CORE
# ==============================================================================
if view_tab_selection == "Main AI Processing Core":
    
    # Segment screen layout columns into: Left Configuration Control | Center Main Stream | Right Tool Matrix
    layout_ctrl_col, layout_stream_col, layout_tools_col = st.columns([0.23, 0.54, 0.23])
    
    # --------------------------------------------------------------------------
    # SUB-MODULE: LEFT CONFIGURATION CONTROL MODULE
    # --------------------------------------------------------------------------
    with layout_ctrl_col:
        st.markdown(f"<p class='metrics-label' style='margin-bottom: 12px;'>AI Sub-Model Select Matrix</p>", unsafe_allow_html=True)
        
        processing_modes_list = [
            {"mode_id": "Smart Mode", "title": "Smart Mode Cluster", "info": f"Leverages core {CORE_ENGINE} pipelines.", "graphic": "🧠"},
            {"mode_id": "Fast Mode", "title": "Fast Mode Routing", "info": "Hyper-optimized for immediate response metrics.", "graphic": "⚡"},
            {"mode_id": "Creative Mode", "title": "Creative Synthesis", "info": "Expanded stochastic output tokens grid.", "graphic": "🎨"},
            {"mode_id": "Coding Assistant", "title": "Strict Coding Mode", "info": "Algorithmic refactoring compiler focus.", "graphic": "💻"}
        ]
        
        for p_mode in processing_modes_list:
            mode_selected_bool = st.session_state.active_model_mode == p_mode["mode_id"]
            active_render_box_style = f"border: 1px solid {HEX_CYAN_GLOW}; background-color: #161b22; box-shadow: 0 0 15px rgba(102, 252, 241, 0.15);" if mode_selected_bool else "border: 1px solid #1a202c; background-color: transparent;"
            
            st.markdown(f"""
                <div style='{active_render_box_style} padding: 14px; border-radius: 14px; margin-bottom: 12px; transition: all 0.2s;'>
                    <span style='font-size: 1.2rem; margin-right: 5px;'>{p_mode['graphic']}</span>
                    <b style='color: white; font-size: 0.9rem;'>{p_mode['title']}</b><br>
                    <span style='color: {HEX_TEXT_MUTED}; font-size: 0.75rem; display: block; margin-top: 4px;'>{p_mode['info']}</span>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Bind Execution to {p_mode['mode_id']}", key=f"sel_key_{p_mode['mode_id']}", use_container_width=True):
                st.session_state.active_model_mode = p_mode["mode_id"]
                st.toast(f"Switched system execution engine to {p_mode['mode_id']}", icon="⚙️")
                time.sleep(0.3)
                st.rerun()
                
        st.markdown("<br><hr style='border:0; border-top:1px solid #1a202c;'><br>", unsafe_allow_html=True)
        st.markdown(f"<p class='metrics-label' style='margin-bottom: 10px;'>Prompt Engineer Templates</p>", unsafe_allow_html=True)
        
        selected_template_key = st.selectbox(
            "Inject Template Framework:",
            list(PROMPT_TEMPLATES_DATABASE.keys()),
            key="template_dropdown_selector"
        )
        if selected_template_key != "None":
            st.session_state.custom_prompt_selection = PROMPT_TEMPLATES_DATABASE[selected_template_key]
            st.info("System Template Injection Loaded. Submit below.")

    # --------------------------------------------------------------------------
    # SUB-MODULE: RIGHT TOOLS MATRIX COMPONENT (Matches Right Panel of Image 1000008643)
    # --------------------------------------------------------------------------
    with layout_tools_col:
        st.markdown(f"<p class='metrics-label' style='margin-bottom: 12px;'>Automation Node Vectors</p>", unsafe_allow_html=True)
        
        automation_vectors_list = [
            {"title_str": "Live Web Search Matrix", "icon_str": "🔍", "status_str": "ONLINE"},
            {"title_str": "Vector Image Generator", "icon_str": "🖼️", "status_str": "STABLE"},
            {"title_str": "Document Structure Parser", "icon_str": "📄", "status_str": "IDLE"},
            {"title_str": "Neural Voice Synthesizer", "icon_str": "🔊", "status_str": "ONLINE"},
            {"title_str": "YouTube Telemetry Loader", "icon_str": "📺", "status_str": "STABLE"},
            {"title_str": "Sandbox Code Interpreter", "icon_str": "🔏", "status_str": "CONTAINED"}
        ]
        
        for auto_node in automation_vectors_list:
            st.markdown(f"""
                <div style='background-color: #12161a; padding: 12px 16px; border-radius: 12px; border: 1px solid #21262d; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between;'>
                    <div style='display: flex; align-items: center;'>
                        <span style='margin-right: 12px; font-size: 1.1rem;'>{auto_node['icon_str']}</span>
                        <span style='color: {HEX_TEXT_LIGHT}; font-size: 0.85rem; font-weight: 600;'>{auto_node['title_str']}</span>
                    </div>
                    <span style='color: {HEX_CYAN_GLOW}; font-size: 0.68rem; font-weight: 700; letter-spacing: 1px;'>{auto_node['status_str']}</span>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<p class='metrics-label'>Compute Pipeline Volatility</p>", unsafe_allow_html=True)
        
        # Plotly Donut representation simulating live memory footprint allocations
        donut_trace = go.Pie(
            labels=['Allocated Nodes Quota', 'Idle Compute Buffer'],
            values=[st.session_state.quota_percentage, 100 - st.session_state.quota_percentage],
            hole=.72,
            marker_colors=[HEX_CYAN_GLOW, '#1a202c'],
            textinfo='none',
            hoverinfo='none'
        )
        donut_figure = go.Figure(data=[donut_trace])
        donut_figure.update_layout(
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0),
            height=135,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(donut_figure, use_container_width=True, config={'displayModeBar': False})
        st.markdown(f"<p style='text-align:center; font-size:0.8rem; color:white; margin-top:-5px;'>Bandwidth Utilization: <b>{st.session_state.quota_percentage}%</b></p>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # SUB-MODULE: CENTER MAIN STREAM SYSTEM CHAT INTERFACE
    # --------------------------------------------------------------------------
    with layout_stream_col:
        # If message arrays are vacant, instantiate premium visualization card layout
        if not st.session_state.messages:
            st.markdown(f"""
                <div style='background: linear-gradient(180deg, #161b22 0%, #0d1117 100%); border: 1px solid #21262d; border-radius: 24px; padding: 45px 30px; text-align: center; margin: 20px auto; box-shadow: 0 20px 40px rgba(0,0,0,0.6);'>
                    <div style='font-size: 3.8rem; margin-bottom: 20px; animation: pulse 2s infinite;'>⚡</div>
                    <h2 style='color: white; font-weight: 900; font-size: 2rem; margin: 0 0 10px 0; letter-spacing:-0.03em;'>Hello, I'm Nexo AI</h2>
                    <p style='color: {HEX_TEXT_MUTED}; font-size: 0.95rem; max-width: 600px; margin: 0 auto 35px auto; line-height: 1.5;'>
                        Your secure enterprise intelligence node engineered exclusively by <b>{CREATOR}</b>. Powering complex code execution blocks, logic architecture, and telemetry matrices.
                    </p>
                    <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; text-align: left;'>
                        <div style='background: #12161a; border: 1px solid #21262d; padding: 16px; border-radius: 12px;'>
                            <span style='color:{HEX_CYAN_GLOW}; font-weight:700; font-size:0.85rem; display:block; margin-bottom:4px;'>🚀 Microservices Setup</span>
                            <span style='color:{HEX_TEXT_MUTED}; font-size:0.75rem;'>Generate clean Dockerized environments.</span>
                        </div>
                        <div style='background: #12161a; border: 1px solid #21262d; padding: 16px; border-radius: 12px;'>
                            <span style='color:{HEX_CYAN_GLOW}; font-weight:700; font-size:0.85rem; display:block; margin-bottom:4px;'>🎨 Tailwind Styling</span>
                            <span style='color:{HEX_TEXT_MUTED}; font-size:0.75rem;'>Build highly aesthetic premium dark UI nodes.</span>
                        </div>
                        <div style='background: #12161a; border: 1px solid #21262d; padding: 16px; border-radius: 12px;'>
                            <span style='color:{HEX_CYAN_GLOW}; font-weight:700; font-size:0.85rem; display:block; margin-bottom:4px;'>🧠 Logic Synthesis</span>
                            <span style='color:{HEX_TEXT_MUTED}; font-size:0.75rem;'>Deconstruct neural data arrays cleanly.</span>
                        </div>
                        <div style='background: #12161a; border: 1px solid #21262d; padding: 16px; border-radius: 12px;'>
                            <span style='color:{HEX_CYAN_GLOW}; font-weight:700; font-size:0.85rem; display:block; margin-bottom:4px;'>🔏 Secure Contained Sandbox</span>
                            <span style='color:{HEX_TEXT_MUTED}; font-size:0.75rem;'>Execute computational optimization layers.</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        # Draw conversational components looping over stack arrays
        for msg_packet in st.session_state.messages:
            with st.chat_message(msg_packet["role"]):
                st.markdown(msg_packet["content"])
                
        # Capture context submission stream array
        input_capture_placeholder = "Ask Nexo AI to write code, generate apps or build projects..."
        if st.session_state.custom_prompt_selection != "":
            user_input_prompt = st.chat_input(input_capture_placeholder, value=st.session_state.custom_prompt_selection)
            st.session_state.custom_prompt_selection = ""  # Clean flash state after allocation
        else:
            user_input_prompt = st.chat_input(input_capture_placeholder)
            
        if user_input_prompt:
            # Render user block instantly
            with st.chat_message("user"):
                st.markdown(user_input_prompt)
            st.session_state.messages.append({"role": "user", "content": user_input_prompt})
            
            # Initiate processing computation routine
            if not groq_client_node:
                st.error("Execution halted: Secure routed API Key cannot be fetched inside runtime context.")
            else:
                with st.chat_message("assistant"):
                    text_stream_frame = st.empty()
                    accumulation_buffer = ""
                    execution_start_timestamp = time.time()
                    
                    try:
                        # Construct complete prompt array matrix payload
                        payload_assembly = [{"role": "system", "content": SYSTEM_PROMPT}] + [
                            {"role": entry["role"], "content": entry["content"]} for entry in st.session_state.messages
                        ]
                        
                        # Command line secure streaming hook to Groq endpoints
                        response_stream = groq_client_node.chat.completions.create(
                            model=MODEL_ID,
                            messages=payload_assembly,
                            temperature=0.35,
                            max_tokens=4096,
                            stream=True
                        )
                        
                        for network_chunk in response_stream:
                            if network_chunk.choices[0].delta.content is not None:
                                accumulation_buffer += network_chunk.choices[0].delta.content
                                text_stream_frame.markdown(accumulation_buffer + " ▌")
                                
                        text_stream_frame.markdown(accumulation_buffer)
                        
                    except Exception as primary_engine_fault:
                        # Automatic Systemic Failover Path routing to backup Llama nodes
                        try:
                            failover_stream = groq_client_node.chat.completions.create(
                                model="llama3-70b-8192",
                                messages=payload_assembly,
                                temperature=0.4,
                                max_tokens=4096,
                                stream=True
                            )
                            for network_chunk in failover_stream:
                                if network_chunk.choices[0].delta.content is not None:
                                    accumulation_buffer += network_chunk.choices[0].delta.content
                                    text_stream_frame.markdown(accumulation_buffer + " ▌")
                            text_stream_frame.markdown(accumulation_buffer)
                        except Exception as systemic_fatal_crash:
                            st.error(f"Critical Runtime Infrastructure Execution Error: {str(systemic_fatal_crash)}")
                            
                    # Update global framework metrics telemetry registers
                    if accumulation_buffer:
                        st.session_state.messages.append({"role": "assistant", "content": accumulation_buffer})
                        
                        # Operational tracking math calculations
                        measured_latency = time.time() - execution_start_timestamp
                        calculated_tokens = len(accumulation_buffer.split()) * 1.3
                        
                        st.session_state.telemetry_total_tokens += int(calculated_tokens)
                        st.session_state.telemetry_api_calls += 1
                        st.session_state.telemetry_avg_latency = float((st.session_state.telemetry_avg_latency + measured_latency) / 2)
                        st.session_state.quota_percentage = min(96, st.session_state.quota_percentage + random.randint(1, 2))
                        
                        st.rerun()

# ==============================================================================
# MODULE 10: WORKSPACE PARTITION B - ADVANCED COMPUTE & TELEMETRY DASHBOARD
# ==============================================================================
else:
    st.markdown(f"<p class='metrics-label'>Real-Time Hardware & API Compute Monitor Panel</p>", unsafe_allow_html=True)
    
    # Grid structure displaying numerical operations data counters
    met_col1, met_col2, met_col3, met_col4 = st.columns(4)
    with met_col1:
        st.markdown(f"""
            <div class='dashboard-card'>
                <div class='metrics-label'>Aggregated Context Tokens</div>
                <div class='metrics-value'>{st.session_state.telemetry_total_tokens}</div>
                <span style='color:#10b981; font-size:0.75rem; font-weight:600;'>⚡ Stable Ingestion</span>
            </div>
        """, unsafe_allow_html=True)
    with met_col2:
        st.markdown(f"""
            <div class='dashboard-card'>
                <div class='metrics-label'>Executed API Pipeline Handshakes</div>
                <div class='metrics-value'>{st.session_state.telemetry_api_calls}</div>
                <span style='color:#10b981; font-size:0.75rem; font-weight:600;'>✔ 100% Success Rate</span>
            </div>
        """, unsafe_allow_html=True)
    with met_col3:
        st.markdown(f"""
            <div class='dashboard-card'>
                <div class='metrics-label'>Mean Processing Latency Index</div>
                <div class='metrics-value'>{st.session_state.telemetry_avg_latency:.3f} sec</div>
                <span style='color:{HEX_CYAN_GLOW}; font-size:0.75rem; font-weight:600;'>🚀 Groq Acceleration Mode</span>
            </div>
        """, unsafe_allow_html=True)
    with met_col4:
        st.markdown(f"""
            <div class='dashboard-card'>
                <div class='metrics-label'>Developer Core Signature</div>
                <div class='metrics-value'>{CREATOR}</div>
                <span style='color:#a855f7; font-size:0.75rem; font-weight:600;'>👑 Root Administrator</span>
            </div>
        """, unsafe_allow_html=True)

    # Graphical Matrix Section utilizing mock pandas arrays to map out continuous processing loads
    st.markdown("<br>", unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown(f"<p class='metrics-label'>Time-Series Compute Latency Flux Array</p>", unsafe_allow_html=True)
        # Construct dataframe to map computing speeds inside time ranges
        mock_timeline_stamps = [datetime.datetime.now() - datetime.timedelta(minutes=x*5) for x in range(15)]
        mock_latency_floats = [random.uniform(0.18, 0.45) for _ in range(15)]
        dataframe_latency_log = pd.DataFrame({"Timeline Vector": mock_timeline_stamps, "Latency Threshold (s)": mock_latency_floats})
        
        latency_scatter_trace = go.Scatter(
            x=dataframe_latency_log["Timeline Vector"], 
            y=dataframe_latency_log["Latency Threshold (s)"],
            mode='lines+markers',
            line=dict(color=HEX_CYAN_GLOW, width=3),
            marker=dict(size=7, color=HEX_BLUE_DARK)
        )
        latency_render_figure = go.Figure(data=[latency_scatter_trace])
        latency_render_figure.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            height=260,
            paper_bgcolor='#12161a',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, font=dict(color=HEX_TEXT_MUTED)),
            yaxis=dict(showgrid=True, gridcolor='#1a202c', font=dict(color=HEX_TEXT_MUTED))
        )
        st.plotly_chart(latency_render_figure, use_container_width=True, config={'displayModeBar': False})

    with chart_col2:
        st.markdown(f"<p class='metrics-label'>Token Volumetric Processing Distribution Matrix</p>", unsafe_allow_html=True)
        # Construct bar trace graph tracking total tokens per processing request block
        mock_request_keys = [f"Req Px-{x}" for x in range(8)]
        mock_token_counts = [random.randint(400, 2500) for _ in range(8)]
        
        token_bar_trace = go.Bar(
            x=mock_request_keys,
            y=mock_token_counts,
            marker_color=HEX_BLUE_DARK,
            opacity=0.85
        )
        token_bar_figure = go.Figure(data=[token_bar_trace])
        token_bar_figure.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            height=260,
            paper_bgcolor='#12161a',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, font=dict(color=HEX_TEXT_MUTED)),
            yaxis=dict(showgrid=True, gridcolor='#1a202c', font=dict(color=HEX_TEXT_MUTED))
        )
        st.plotly_chart(token_bar_figure, use_container_width=True, config={'displayModeBar': False})
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.success("✅ Computational cluster verification telemetry report finalized. Infrastructure health index: 99.98% optimal.")

# ==============================================================================
# MODULE 11: SYSTEM GLOBAL FOOTER MATRIX SECTION
# ==============================================================================
st.markdown(f"""
    <div style='text-align: center; color: {HEX_TEXT_MUTED}; font-size: 0.72rem; padding: 35px 0px 15px 0px; border-top: 1px solid #1a202c; margin-top: 50px;'>
        Nexo AI Core Pipeline Registry • Highly Secured Context Data Protection Enabled • Developed Proudly by <b>{CREATOR}</b>.
    </div>
""", unsafe_allow_html=True)
