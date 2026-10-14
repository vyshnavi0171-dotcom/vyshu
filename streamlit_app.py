"""SatyaNet (VakyaGuard) - Streamlit Dashboard
Multi-modal Misinformation & Audio Deepfake Detector for Regional Languages.

Run via:
    streamlit run streamlit_app.py
"""

import os
import sys
import io
import requests
import matplotlib.pyplot as plt
import numpy as np
import librosa
import streamlit as st

# Add project root to sys.path so it can also invoke backend logic directly if needed
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from backend.audio_processor import analyze_audio_deepfake, load_audio_from_bytes
    from backend.text_processor import analyze_text_misinformation, SUPPORTED_LANGUAGES
    LOCAL_BACKEND_AVAILABLE = True
except Exception as e:
    LOCAL_BACKEND_AVAILABLE = False
    SUPPORTED_LANGUAGES = {"auto": "Auto-Detect"}

# Page Configuration
st.set_page_config(
    page_title="SatyaNet | Regional Misinformation & Deepfake Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark-mode modern cyber-forensic aesthetic)
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #3B82F6, #10B981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #9CA3AF;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .badge-safe {
        background-color: #064E3B;
        color: #34D399;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        display: inline-block;
        border: 1px solid #059669;
    }
    .badge-suspicious {
        background-color: #78350F;
        color: #FBBF24;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        display: inline-block;
        border: 1px solid #D97706;
    }
    .badge-fake {
        background-color: #7F1D1D;
        color: #F87171;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        display: inline-block;
        border: 1px solid #DC2626;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=64)
    st.markdown("### **SatyaNet (VakyaGuard)**")
    st.caption("AI Misinformation & Deepfake Defense for Regional Languages")
    st.divider()
    
    api_backend_url = st.text_input(
        "Backend API URL",
        value="http://127.0.0.1:8000",
        help="FastAPI endpoint URL. If offline, the app switches automatically to embedded local execution."
    )
    
    use_remote_api = st.checkbox("Connect via FastAPI REST API", value=False)
    
    st.divider()
    st.markdown("#### 🌐 Target Indian Context")
    st.markdown("""
    - **Voice Note Forensics**: WhatsApp Opus/AMR downsampled audio
    - **Vernacular Scripts**: Hindi, Bengali, Tamil, Telugu, Marathi
    - **Hinglish/Tanglish**: Transliterated Latin script
    - **Low-Bandwidth**: Lightweight 16kHz mono feature processing
    """)
    st.divider()
    st.caption("v1.0.0 • Hackathon Prototype")

# Header Section
st.markdown('<div class="main-header">SatyaNet // सत्य-नेट</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multi-modal Misinformation & Audio Deepfake Verification Engine for Vernacular Environments</div>', unsafe_allow_html=True)

# Main Navigation Toggle
mode = st.radio(
    "Choose Verification Mode:",
    ["🎧 Audio Deepfake Scanner", "📰 Text Claim Verifier"],
    horizontal=True,
    index=0
)

# -------------------------------------------------------------
# MODE 1: AUDIO DEEPFAKE SCANNER
# -------------------------------------------------------------
if mode == "🎧 Audio Deepfake Scanner":
    st.markdown("### 🎙️ WhatsApp Voice Note & Audio Forensics")
    st.write("Upload an audio clip (WAV, MP3, OGG, M4A) to detect synthetic speech synthesis, voice cloning, or neural vocoder artifacts.")
    
    col1, col2 = st.columns([1, 1], gap="medium")
    
    with col1:
        st.markdown("#### 1. Upload Voice Note")
        uploaded_file = st.file_uploader(
            "Drag and drop regional audio clip or WhatsApp voice note",
            type=["wav", "mp3", "ogg", "m4a", "flac"],
            help="Low-bandwidth recordings are automatically normalized to 16 kHz mono."
        )
        
        analyze_btn = st.button("🚀 Analyze Audio Forensics", type="primary", disabled=(uploaded_file is None), use_container_width=True)
        
        if uploaded_file is not None:
            st.audio(uploaded_file, format=uploaded_file.type)
            st.caption(f"📁 **File:** `{uploaded_file.name}` | **Size:** {round(uploaded_file.size / 1024, 1)} KB")

    with col2:
        st.markdown("#### 2. Forensic Analysis & Verdict")
        
        if analyze_btn and uploaded_file is not None:
            with st.spinner("Extracting Mel-Spectrogram, MFCCs & Pitch Biomarkers..."):
                audio_bytes = uploaded_file.getvalue()
                result = None
                
                # Check whether to call REST API or internal module
                if use_remote_api:
                    try:
                        files = {"file": (uploaded_file.name, audio_bytes, uploaded_file.type)}
                        resp = requests.post(f"{api_backend_url}/api/detect-audio", files=files, timeout=15)
                        if resp.status_code == 200:
                            result = resp.json()
                        else:
                            st.warning(f"FastAPI backend returned {resp.status_code}. Using local processing.")
                    except Exception as e:
                        st.info(f"Could not reach REST API ({e}). Running local pipeline.")

                if result is None and LOCAL_BACKEND_AVAILABLE:
                    result = analyze_audio_deepfake(audio_bytes, filename=uploaded_file.name)

                if result:
                    prob = result["deepfake_probability"]
                    verdict = result["verdict"]
                    risk = result["risk_category"]
                    
                    # Risk Badge
                    if risk == "HIGH_RISK":
                        st.markdown(f'<span class="badge-fake">🚨 HIGH RISK: {verdict}</span>', unsafe_allow_html=True)
                    elif risk == "SUSPICIOUS":
                        st.markdown(f'<span class="badge-suspicious">⚠️ SUSPICIOUS: {verdict}</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<span class="badge-safe">✅ SAFE: {verdict}</span>', unsafe_allow_html=True)

                    st.markdown("")
                    # Metrics row
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric("Deepfake Probability", f"{round(prob * 100, 1)}%")
                    with m2:
                        st.metric("Confidence Level", result["confidence_percentage"])
                    with m3:
                        st.metric("Clip Duration", f"{result['duration_seconds']}s")

                    # Progress Bar Gauge
                    st.progress(prob, text=f"Deepfake Risk Gauge ({round(prob * 100, 1)}%)")

                    # Recommendation
                    st.info(f"**Action Recommendation:** {result['recommendation']}")

                    # Flagged Indicators
                    st.markdown("##### 🔍 Forensic Biomarkers & Indicators:")
                    for indicator in result["flagged_indicators"]:
                        st.markdown(f"- 🚩 **{indicator}**")

                    # Biomarkers Accordion
                    with st.expander("📊 Technical Acoustic Biomarkers (Librosa)"):
                        st.json(result["acoustic_biomarkers"])
                        
                        # Generate and show Mel-Spectrogram preview
                        try:
                            y, sr, _ = load_audio_from_bytes(audio_bytes)
                            fig, ax = plt.subplots(figsize=(8, 2.5))
                            S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
                            S_dB = librosa.power_to_db(S, ref=np.max)
                            img = librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=sr, ax=ax, cmap='magma')
                            fig.colorbar(img, ax=ax, format='%+2.0f dB')
                            ax.set_title('Forensic Mel-Spectrogram (16kHz Normalized)')
                            st.pyplot(fig)
                        except Exception:
                            pass
        else:
            st.info("Upload an audio file on the left and click **Analyze Audio Forensics** to evaluate.")


# -------------------------------------------------------------
# MODE 2: TEXT CLAIM VERIFIER
# -------------------------------------------------------------
elif mode == "📰 Text Claim Verifier":
    st.markdown("### ✍️ Vernacular & Social Media Claim Verification")
    st.write("Detect forwarded hoaxes, phishing lures, fake government schemes, and viral misinformation across regional Indian languages and Hinglish.")

    # Preset Example Buttons for Instant Hackathon Demos
    st.markdown("##### ⚡ Quick-Load Hackathon Test Cases:")
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    sample_text = ""
    if btn_col1.button("📱 Fake Recharge Lure (Hinglish)"):
        sample_text = "Modi sarkar sabhi vidyarthiyo ko 3 mahine ka free recharge de rahi hai! Turant is link par click karo bit.ly/free-recharge-2024 aur 10 WhatsApp groups me bhejo warna offer cancel ho jayega."
    if btn_col2.button("🧒 WhatsApp Panic Rumor (Hindi)"):
        sample_text = "सावधान! आपके इलाके में 5 बच्चा चोर घूम रहे हैं जो रात को बच्चों को उठा रहे हैं। यह संदेश अपने सभी जानने वालों को तुरंत भेजें।"
    if btn_col3.button("🚀 Legitimate News (English/Hindi)"):
        sample_text = "ISRO successfully launched the Chandrayaan mission from Sriharikota, achieving soft landing on the lunar south pole."

    col1, col2 = st.columns([1, 1], gap="medium")
    
    with col1:
        st.markdown("#### 1. Input Forwarded Text")
        
        language_selection = st.selectbox(
            "Select Regional Language Hint:",
            options=list(SUPPORTED_LANGUAGES.keys()),
            format_func=lambda x: SUPPORTED_LANGUAGES[x],
            index=0
        )
        
        user_input_text = st.text_area(
            "Paste forwarded message, tweet, or WhatsApp text snippet:",
            value=sample_text,
            height=180,
            placeholder="Type or paste vernacular text here (e.g. Hindi, Hinglish, Tamil, Telugu)..."
        )
        
        verify_btn = st.button("🔎 Verify Factual Claim", type="primary", disabled=(len(user_input_text.strip()) < 3), use_container_width=True)

    with col2:
        st.markdown("#### 2. Credibility Score & Fact Analysis")
        
        if verify_btn and user_input_text.strip():
            with st.spinner("Analyzing vernacular semantics, claims & hoax signatures..."):
                result = None
                
                # Check whether to call REST API or internal module
                if use_remote_api:
                    try:
                        payload = {"text": user_input_text, "language": language_selection}
                        resp = requests.post(f"{api_backend_url}/api/detect-text", json=payload, timeout=15)
                        if resp.status_code == 200:
                            result = resp.json()
                        else:
                            st.warning(f"FastAPI backend returned {resp.status_code}. Using local processing.")
                    except Exception as e:
                        st.info(f"Could not reach REST API ({e}). Running local pipeline.")

                if result is None and LOCAL_BACKEND_AVAILABLE:
                    result = analyze_text_misinformation(user_input_text, language_hint=language_selection)

                if result:
                    verdict = result["verdict"]
                    score = result["credibility_score"]
                    risk = result["risk_category"]

                    # Verdict Badges
                    if risk == "HIGH_RISK" or verdict in ["FALSE", "FAKE"]:
                        st.markdown(f'<span class="badge-fake">🚨 VERDICT: {verdict}</span>', unsafe_allow_html=True)
                    elif risk == "SUSPICIOUS" or verdict == "MISLEADING":
                        st.markdown(f'<span class="badge-suspicious">⚠️ VERDICT: {verdict}</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<span class="badge-safe">✅ VERDICT: {verdict}</span>', unsafe_allow_html=True)

                    st.markdown("")
                    # Metrics
                    tm1, tm2 = st.columns(2)
                    with tm1:
                        st.metric("Credibility Score", f"{score} / 100")
                    with tm2:
                        st.metric("Detected Language", result["detected_language"])

                    # Progress Bar Gauge
                    cred_ratio = score / 100.0
                    st.progress(cred_ratio, text=f"Credibility Confidence ({score}%)")

                    # Core Claim & Summary
                    st.markdown(f"**Core Claim:** {result['core_claim']}")
                    st.info(f"**Analysis Summary:** {result['summary']}")

                    # Manipulation Tactics Found
                    st.markdown("##### 🚩 Manipulation Factors:")
                    for tactic in result.get("manipulation_tactics", []):
                        st.markdown(f"- ⚠️ **{tactic}**")

                    # Detailed Reasoning
                    with st.expander("🔍 Detailed Debunking / Reasoning Points"):
                        for reason in result.get("reasoning", []):
                            st.write(f"• {reason}")
                        st.caption(f"Engine: {result.get('source_engine', 'SatyaNet')}")

                    st.warning(f"**Recommended Action:** {result['recommended_action']}")
        else:
            st.info("Paste a social media message on the left or click a quick-load test button.")
