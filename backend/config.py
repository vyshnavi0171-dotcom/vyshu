import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

class Settings:
    PROJECT_NAME: str = "SatyaNet (VakyaGuard)"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Multi-Modal Misinformation & Audio Deepfake Detector for Regional Languages"
    
    # API Settings (Render assigns dynamic PORT and requires 0.0.0.0)
    API_HOST: str = os.getenv("HOST", os.getenv("API_HOST", "0.0.0.0"))
    API_PORT: int = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))
    
    # Gemini / LLM API Key
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Audio Feature Thresholds
    DEEPFAKE_THRESHOLD_HIGH: float = float(os.getenv("DEEPFAKE_THRESHOLD_HIGH", "0.65"))
    DEEPFAKE_THRESHOLD_MED: float = float(os.getenv("DEEPFAKE_THRESHOLD_MED", "0.40"))
    
    # Audio target sample rate for low-bandwidth normalization
    TARGET_SAMPLE_RATE: int = 16000
    
    # Maximum audio length accepted (seconds) to prevent memory bottlenecks on low-resource servers
    MAX_AUDIO_DURATION_SEC: int = 60

settings = Settings()
