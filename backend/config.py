"""
Configuration management for LLM Inference API
"""

import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings"""
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS settings
    ALLOWED_ORIGINS: list = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000"
    ).split(",")
    
    # HuggingFace settings
    HF_TOKEN: str = os.getenv("HUGGING_FACE_HUB_TOKEN", "")
    
    # Model endpoints
    MODEL_ENDPOINTS: Dict[str, str] = {
        "gpt-2": os.getenv("TGI_GPT2_ENDPOINT", "http://localhost:8080"),
        "tiny-llama": os.getenv("TGI_TINYLLAMA_ENDPOINT", "http://localhost:8081"),
        "mistral-7b": os.getenv("TGI_MISTRAL_ENDPOINT", "http://localhost:8082"),
        "llama-2-7b": os.getenv("TGI_LLAMA2_ENDPOINT", "http://localhost:8083"),
        "falcon-7b": os.getenv("TGI_FALCON_ENDPOINT", "http://localhost:8084"),
        "phi-2": os.getenv("TGI_PHI2_ENDPOINT", "http://localhost:8085"),
    }


settings = Settings()

