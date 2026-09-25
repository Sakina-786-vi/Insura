import os

from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")
    BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "replace_with_secure_random_value")
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() in {"1", "true", "yes"}

    N8N_POLICY_INTELLIGENCE_URL = os.getenv("N8N_POLICY_INTELLIGENCE_URL", "")
    N8N_POLICY_COMPARISON_URL = os.getenv("N8N_POLICY_COMPARISON_URL", "")
    N8N_LEARNING_GENERATION_URL = os.getenv("N8N_LEARNING_GENERATION_URL", "")
    N8N_TIMEOUT = os.getenv("N8N_TIMEOUT", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    EXPLABS_API_KEY = os.getenv("EXPLABS_API_KEY", "")
    AI_API_KEY = GROQ_API_KEY or EXPLABS_API_KEY or os.getenv("AI_API_KEY", "")
    AI_PROVIDER = "openai-compatible" if (GROQ_API_KEY or EXPLABS_API_KEY) else os.getenv("AI_PROVIDER", "openai-compatible")
    AI_TASK = "chat"
    AI_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b") if GROQ_API_KEY else ("nemotron-3-ultra-550b-a55b" if EXPLABS_API_KEY else os.getenv("AI_MODEL", ""))
    AI_BASE_URL = "https://api.groq.com/openai/v1" if GROQ_API_KEY else ("https://api.experientiallabs.ai/v1" if EXPLABS_API_KEY else os.getenv("AI_BASE_URL", ""))
    AI_TIMEOUT = os.getenv("AI_TIMEOUT", "30")