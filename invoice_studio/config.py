"""
Configuration management for AI Invoice Builder
Loads settings from .env file
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    OUTPUT_DIR = BASE_DIR / "output"
    UPLOAD_DIR = DATA_DIR / "uploads"
    CACHE_DIR = DATA_DIR / "cache"
    
    # LLM Configuration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "lm_studio")
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # LM Studio Configuration
    LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234")
    LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "llama-3.3-70b-instruct")
    
    # LLM Parameters
    DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.1"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
    CONTEXT_LENGTH = int(os.getenv("CONTEXT_LENGTH", "8192"))
    
    # Application Defaults
    DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "KRW")
    DEFAULT_INVOICE_TYPE = os.getenv("DEFAULT_INVOICE_TYPE", "tax")
    
    # OCR Configuration
    TESSERACT_PATH = os.getenv("TESSERACT_PATH", "C:/Program Files/Tesseract-OCR/tesseract.exe")
    OCR_LANG = os.getenv("OCR_LANG", "kor+eng")
    
    # Database
    DATABASE_PATH = DATA_DIR / "invoices.db"
    
    # Excel Template
    TEMPLATE_PATH = DATA_DIR / "Invoice template.xlsx"
    MAPPING_PATH = DATA_DIR / "template_mapping.json"
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        cls.UPLOAD_DIR.mkdir(exist_ok=True)
        cls.CACHE_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        # Check LLM provider configuration
        if cls.LLM_PROVIDER == "claude" and not cls.CLAUDE_API_KEY:
            errors.append("CLAUDE_API_KEY is required when using Claude provider")
        
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required when using OpenAI provider")
        
        # Check required files
        if not cls.TEMPLATE_PATH.exists():
            errors.append(f"Excel template not found: {cls.TEMPLATE_PATH}")
        
        if not cls.MAPPING_PATH.exists():
            errors.append(f"Template mapping not found: {cls.MAPPING_PATH}")
        
        return errors
    
    @classmethod
    def get_llm_config(cls):
        """Get LLM configuration as dictionary"""
        return {
            "provider": cls.LLM_PROVIDER,
            "claude_api_key": cls.CLAUDE_API_KEY,
            "openai_api_key": cls.OPENAI_API_KEY,
            "lm_studio_url": cls.LM_STUDIO_URL,
            "lm_studio_model": cls.LM_STUDIO_MODEL,
            "temperature": cls.DEFAULT_TEMPERATURE,
            "max_tokens": cls.MAX_TOKENS,
            "context_length": cls.CONTEXT_LENGTH,
        }


# Initialize directories on import
Config.ensure_directories()
