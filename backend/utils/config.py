import os
from dotenv import load_dotenv

# ---------------------------------------------------------
# LOAD ENVIRONMENT
# ---------------------------------------------------------
# טוען את קובץ .env פעם אחת בלבד
load_dotenv()

# ---------------------------------------------------------
# NVIDIA CONFIG
# ---------------------------------------------------------
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_LLM_MODEL = os.getenv("NVIDIA_LLM_MODEL", "meta/llama-4-maverick-17b-128e-instruct")
NVIDIA_LLM_BASE_URL = os.getenv("NVIDIA_LLM_BASE_URL", "https://integrate.api.nvidia.com/v1")

NVIDIA_EMBED_MODEL = os.getenv("NVIDIA_EMBED_MODEL", "nvidia/llama-3.2-nemoretriever-300m-embed-v2")
NVIDIA_EMBED_BASE_URL = os.getenv("NVIDIA_EMBED_BASE_URL", "https://integrate.api.nvidia.com/v1")

# ---------------------------------------------------------
# QDRANT CONFIG
# ---------------------------------------------------------
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "feedback_embeddings")

# ---------------------------------------------------------
# LOGGING SETTINGS
# ---------------------------------------------------------
DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"

# ---------------------------------------------------------
# GENERAL PRINT FUNCTION
# ---------------------------------------------------------
def debug_log(message: str, icon: str = "🔧"):
    """מדפיס הודעת דיבוג רק אם DEBUG_MODE מופעל"""
    if DEBUG_MODE:
        print(f"[{icon}] {message}")
