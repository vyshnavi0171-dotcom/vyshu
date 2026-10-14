"""Multilingual text claim verification and misinformation detection pipeline.

Handles vernacular scripts (Hindi, Bengali, Tamil, Telugu, etc.) as well as
transliterated social media text (Hinglish/Tanglish).
Uses Google Gemini API when configured, with an intelligent regional pattern
heuristic engine as an offline / zero-latency fallback for hackathon reliability.
"""

import json
import os
import re
from typing import Dict, List, Any, Optional

from backend.config import settings

# Attempt import of Google Generative AI
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


# Supported Regional Languages Metadata
SUPPORTED_LANGUAGES = {
    "auto": "Auto-Detect Language",
    "hi": "Hindi (हिंदी)",
    "hinglish": "Hinglish (Hindi in Roman script)",
    "bn": "Bengali (বাংলা)",
    "ta": "Tamil (தமிழ்)",
    "te": "Telugu (తెలుగు)",
    "mr": "Marathi (मराठी)",
    "gu": "Gujarati (ગુજરાતી)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "en": "English",
}

# Regional Misinformation Indicators & Signatures for Indian Vernacular Context
VIRAL_HOAX_PATTERNS = [
    {
        "pattern": r"(free\s*(recharge|laptop|smartphone|tablet|bike)|मुफ्त\s*रिचार्ज|१५\s*लाख|15\s*lakh|pm\s*(yojana|fund|awas)|modi\s*de\s*rahe)",
        "category": "Fake Government Scheme / Phishing Lure",
        "weight": 35,
    },
    {
        "pattern": r"(forward\s*(this\s*)?to\s*\d+|share\s*kar(o|e)|bhejo|sabko\s*bhejo|११\s*logo\s*ko|10\s*logo\s*ko|warna\s*whatsapp\s*band)",
        "category": "Viral WhatsApp Chain Letter / Engagement Bait",
        "weight": 30,
    },
    {
        "pattern": r"(baccha\s*chor|child\s*kidnap|child\s*lifter|bacha\s*uthane|kidney\s*gang|rat\s*ko\s*bahar\s*mat)",
        "category": "Panic-Inducing Public Safety Rumor",
        "weight": 40,
    },
    {
        "pattern": r"(electricity\s*power\s*cut|bijli\s*bill|account\s*blocked|sbi\s*yono|pan\s*card\s*link|kyc\s*update)",
        "category": "Urgent Financial / Phishing Impersonation",
        "weight": 35,
    },
    {
        "pattern": r"(unesco\s*declared|best\s*prime\s*minister|nasa\s*recorded|ram\s*mandir\s*drone|2000\s*(ke\s*)?note\s*(me\s*)?chip)",
        "category": "Classic Recycled Social Media Hoax",
        "weight": 40,
    },
]

SUSPICIOUS_URL_PATTERNS = r"(bit\.ly|tinyurl\.com|goo\.gl|t\.me|\.xyz|\.top|\.club|wa\.me|wp\.me)"


def detect_text_script_and_language(text: str) -> str:
    """Detects script or Romanized vernacular from text content."""
    # Check for Devanagari script (Hindi, Marathi, Nepali)
    if re.search(r"[\u0900-\u097F]", text):
        return "Hindi / Marathi (Devanagari)"
    # Check for Bengali script
    elif re.search(r"[\u0980-\u09FF]", text):
        return "Bengali (বাংলা)"
    # Check for Tamil script
    elif re.search(r"[\u0B80-\u0BFF]", text):
        return "Tamil (தமிழ்)"
    # Check for Telugu script
    elif re.search(r"[\u0C00-\u0C7F]", text):
        return "Telugu (తెలుగు)"
    # Check for Gujarati script
    elif re.search(r"[\u0A80-\u0AFF]", text):
        return "Gujarati (ગુજરાતી)"
    # Check for Kannada script
    elif re.search(r"[\u0C80-\u0CFF]", text):
        return "Kannada (ಕನ್ನಡ)"
    
    # Roman script: detect Hinglish / Vernacular Romanized markers
    hinglish_markers = [
        "karo", "bhejo", "hai", "nahi", "raha", "sabhi", "aaj", "kal", "chahiye",
        "milega", "dost", "bhai", "shuru", "hoga", "suno", "dekho", "khabar",
        "sarkari", "yojana", "paise", "account", "dhyan", "kripya", "turant"
    ]
    words = text.lower().split()
    matches = sum(1 for w in words if w in hinglish_markers)
    if matches >= 2:
        return "Hinglish (Hindi in Roman script)"
    
    return "English"


def _verify_with_gemini(text: str, language_hint: str) -> Optional[Dict[str, Any]]:
    """Evaluates text claim using Google Gemini API with structured JSON output."""
    api_key = settings.GEMINI_API_KEY
    if not api_key or not HAS_GENAI:
        return None

    try:
        genai.configure(api_key=api_key)
        # Using gemini-1.5-flash for rapid low-latency response
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )

        prompt = f"""
You are SatyaNet, an expert multilingual fact-checking AI designed for regional Indian social media content (WhatsApp forwards, Twitter/X posts, Facebook posts in Hindi, Hinglish, Bengali, Tamil, Telugu, English).

Evaluate the following message for misinformation, factual accuracy, phishing, or hoax patterns.

Input Message:
\"\"\"{text}\"\"\"

Language hint: {language_hint}

Return a valid JSON object matching EXACTLY this structure:
{{
  "verdict": "FALSE" | "MISLEADING" | "UNVERIFIED" | "TRUE",
  "credibility_score": <integer from 0 (completely false/dangerous) to 100 (fully verified fact)>,
  "risk_category": "HIGH_RISK" | "SUSPICIOUS" | "SAFE",
  "detected_language": "<detected language or dialect, e.g. Hinglish / Hindi>",
  "core_claim": "<1 concise sentence summarizing the main factual claim>",
  "summary": "<2-3 sentence explanation of why this is true, misleading, or a fabricated hoax>",
  "reasoning": [
    "<point 1: factual debunk or verification detail>",
    "<point 2: manipulation tactic or verification source>"
  ],
  "manipulation_tactics": ["<e.g. Urgency Trigger, Phishing URL, Impersonation of Government, None>"],
  "recommended_action": "<Advice for user, e.g. Do not forward, Report to PIB Fact Check, Safe to share>"
}}
"""
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        parsed = json.loads(result_text)
        parsed["source_engine"] = "Gemini-1.5-Flash Multilingual Fact-Checker"
        return parsed
    except Exception as e:
        print(f"[TextProcessor] Gemini API query failed: {e}. Falling back to heuristic engine.")
        return None


def _verify_with_heuristic_engine(text: str, language_hint: str) -> Dict[str, Any]:
    """Deterministic offline fallback fact-checking engine for hackathon demos.
    
    Uses pattern signatures, linguistic urgency detection, known regional hoax templates,
    and phishing heuristics to provide instantaneous, reliable scoring.
    """
    detected_lang = detect_text_script_and_language(text)
    if language_hint and language_hint != "auto" and language_hint in SUPPORTED_LANGUAGES:
        detected_lang = SUPPORTED_LANGUAGES[language_hint]

    text_lower = text.lower()
    manipulation_tactics: List[str] = []
    risk_score = 10  # Base natural suspicion

    # Check for known viral hoax patterns
    for item in VIRAL_HOAX_PATTERNS:
        if re.search(item["pattern"], text_lower, re.IGNORECASE):
            manipulation_tactics.append(item["category"])
            risk_score += item["weight"]

    # Check for suspicious shortened URLs or phishing domains
    has_suspicious_url = bool(re.search(SUSPICIOUS_URL_PATTERNS, text_lower))
    if has_suspicious_url:
        manipulation_tactics.append("Unverified Shortened/Phishing Link detected")
        risk_score += 25

    # Check for urgency keywords
    urgency_words = ["turant", "urgent", "aaj hi", "last date", "aaj raat", "jaldi karo", "hurry", "limited time"]
    if any(w in text_lower for w in urgency_words):
        manipulation_tactics.append("Artificial Urgency / Time-Pressure Trigger")
        risk_score += 15

    # Check for WhatsApp forward hallmarks
    if "forward" in text_lower or "share" in text_lower or "bhejo" in text_lower:
        if "WhatsApp" not in manipulation_tactics:
            manipulation_tactics.append("Forward Propagation Pressure")

    # Bound risk score and compute credibility
    risk_score = min(risk_score, 95)
    credibility_score = 100 - risk_score

    # Determine verdict and risk tier
    if credibility_score <= 35:
        verdict = "FALSE"
        risk_category = "HIGH_RISK"
        summary = (
            "This message displays classic hallmarks of a manufactured viral forward or phishing lure. "
            "It exploits urgency triggers and unauthorized institutional names to deceive users."
        )
        recommended_action = "Do not forward. Block sender and verify through official government portals (e.g., pib.gov.in)."
    elif credibility_score <= 65:
        verdict = "MISLEADING"
        risk_category = "SUSPICIOUS"
        summary = (
            "The message contains unverified or exaggerated assertions. Key facts appear distorted "
            "or lack authoritative attribution."
        )
        recommended_action = "Exercise caution. Do not share in groups until cross-verified with recognized press."
    else:
        verdict = "AUTHENTIC"
        risk_category = "SAFE"
        summary = "No standard regional disinformation patterns, artificial urgency lures, or malicious URLs were detected."
        recommended_action = "Appears consistent with normal conversational or factual communication."

    # Extract core claim preview (first 100 chars or first sentence)
    sentences = re.split(r"[.!?।\n]", text.strip())
    core_claim = sentences[0].strip() if sentences and len(sentences[0].strip()) > 5 else text[:80] + "..."

    reasoning = []
    if manipulation_tactics:
        for tactic in manipulation_tactics:
            reasoning.append(f"Identified manipulation factor: {tactic}")
    else:
        reasoning.append("Text exhibits natural syntactic structure without artificial viral triggers.")
        reasoning.append("No blacklisted scheme, phishing domain, or communal rumor markers found.")

    return {
        "verdict": verdict,
        "credibility_score": credibility_score,
        "confidence_percentage": f"{credibility_score}%",
        "risk_category": risk_category,
        "detected_language": detected_lang,
        "core_claim": core_claim,
        "summary": summary,
        "reasoning": reasoning,
        "manipulation_tactics": manipulation_tactics if manipulation_tactics else ["None Identified"],
        "recommended_action": recommended_action,
        "source_engine": "SatyaNet Vernacular Heuristic & Signature Engine (Offline Mode)",
    }


def analyze_text_misinformation(text: str, language_hint: str = "auto") -> Dict[str, Any]:
    """Main verification pipeline for submitted text messages.
    
    Tries the Gemini LLM engine first for nuanced reasoning; smoothly falls back
    to the heuristic signature engine if offline or if no API key is set.
    """
    clean_text = text.strip()
    if not clean_text:
        return {
            "verdict": "UNVERIFIED",
            "credibility_score": 50,
            "confidence_percentage": "50%",
            "risk_category": "SUSPICIOUS",
            "detected_language": "Unknown",
            "core_claim": "Empty input",
            "summary": "No text provided for analysis.",
            "reasoning": ["Input was empty or whitespace."],
            "manipulation_tactics": [],
            "recommended_action": "Provide a forwarded message or news claim to evaluate.",
            "source_engine": "None"
        }

    # 1. Try Gemini API
    llm_result = _verify_with_gemini(clean_text, language_hint)
    if llm_result:
        # Normalize fields
        score = int(llm_result.get("credibility_score", 50))
        llm_result["confidence_percentage"] = f"{score}%"
        return llm_result

    # 2. Heuristic fallback
    return _verify_with_heuristic_engine(clean_text, language_hint)
