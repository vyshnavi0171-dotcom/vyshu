"""FastAPI Application for SatyaNet (VakyaGuard).

Provides REST API endpoints for:
1. /api/detect-audio: Multi-part voice note upload for TTS/voice clone detection.
2. /api/detect-text: Multilingual claim analysis and credibility verification.
3. /api/health: Service health and configuration check.
4. /api/languages: List of supported regional languages.
"""

from typing import List, Optional, Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.config import settings
from backend.audio_processor import analyze_audio_deepfake
from backend.text_processor import analyze_text_misinformation, SUPPORTED_LANGUAGES

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for local Streamlit, React, Vite, Next.js, or mobile clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to trusted origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Request & Response Schemas
# ---------------------------------------------------------

class TextDetectionRequest(BaseModel):
    """Payload for text verification endpoint."""
    text: str = Field(..., min_length=3, description="Social media message or forwarded claim to analyze")
    language: Optional[str] = Field("auto", description="Language code (e.g. 'hi', 'hinglish', 'ta', 'auto')")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Modi sarkar sabhi vidyarthiyo ko free laptop de rahi hai, turant is link par click kare aur 10 dosto ko bhejo bit.ly/free-laptop-2024",
                "language": "hinglish"
            }
        }


class TextDetectionResponse(BaseModel):
    """Standardized response schema for text misinformation detection."""
    verdict: str = Field(..., description="Verdict: TRUE, FALSE, MISLEADING, or UNVERIFIED")
    credibility_score: int = Field(..., ge=0, le=100, description="Credibility score 0-100")
    confidence_percentage: str
    risk_category: str = Field(..., description="SAFE, SUSPICIOUS, or HIGH_RISK")
    detected_language: str
    core_claim: str
    summary: str
    reasoning: List[str]
    manipulation_tactics: List[str]
    recommended_action: str
    source_engine: str


class AudioBiomarkers(BaseModel):
    """Key acoustic features extracted during forensic analysis."""
    mean_spectral_flatness: float
    pitch_mean_hz: float
    pitch_jitter_proxy: float
    mfcc_delta_variance: float
    silent_frame_ratio: float


class AudioDetectionResponse(BaseModel):
    """Standardized response schema for audio deepfake detection."""
    status: str
    filename: str
    duration_seconds: float
    sample_rate_hz: int
    deepfake_probability: float = Field(..., ge=0.0, le=1.0)
    deepfake_percentage: str
    confidence_level: float = Field(..., ge=0.0, le=1.0)
    confidence_percentage: str
    verdict: str
    risk_category: str
    recommendation: str
    flagged_indicators: List[str]
    acoustic_biomarkers: AudioBiomarkers


class HealthResponse(BaseModel):
    status: str
    version: str
    gemini_configured: bool
    supported_audio_formats: List[str]


# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------

@app.get("/", tags=["Root"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "documentation": "/docs"
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Returns system status, engine mode, and supported media formats."""
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        gemini_configured=bool(settings.GEMINI_API_KEY),
        supported_audio_formats=["wav", "mp3", "ogg", "m4a", "flac"]
    )


@app.get("/api/languages", tags=["Metadata"])
def get_supported_languages() -> Dict[str, str]:
    """Returns mapping of supported regional language codes and localized names."""
    return SUPPORTED_LANGUAGES


@app.post("/api/detect-audio", response_model=AudioDetectionResponse, tags=["Audio Detection"])
async def detect_audio(
    file: UploadFile = File(..., description="Voice note / audio clip file (WAV, MP3, OGG, M4A)")
):
    """Processes an uploaded voice note and returns deepfake probability and acoustic indicators.
    
    Extracts Mel-Spectrogram, MFCC, and vocoder biomarkers via librosa to detect
    speech synthesis, voice cloning, or replay artifacts.
    """
    allowed_extensions = (".wav", ".mp3", ".ogg", ".m4a", ".flac", ".aac")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Please upload one of: {', '.join(allowed_extensions)}"
        )

    try:
        audio_bytes = await file.read()
        if len(audio_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )
            
        # Run forensic feature extraction and analysis
        result = analyze_audio_deepfake(audio_bytes=audio_bytes, filename=file.filename)
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio processing error: {str(e)}"
        )


@app.post("/api/detect-text", response_model=TextDetectionResponse, tags=["Text Detection"])
async def detect_text(payload: TextDetectionRequest):
    """Analyzes forwarded text or news snippets for misinformation.
    
    Supports vernacular scripts (Hindi, Bengali, Tamil, etc.) and transliterated Hinglish.
    Evaluates claims, detects manipulation tactics (urgency triggers, phishing lures),
    and assigns a credibility score and verdict.
    """
    try:
        result = analyze_text_misinformation(
            text=payload.text,
            language_hint=payload.language or "auto"
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text verification error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
