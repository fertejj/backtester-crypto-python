import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # BingX API
    bingx_api_key: str = os.getenv("BINGX_API_KEY", "")
    bingx_secret_key: str = os.getenv("BINGX_SECRET_KEY", "")
    bingx_base_url: str = os.getenv("BINGX_BASE_URL", "https://open-api.bingx.com")
    
    # Backtesting defaults
    default_initial_capital: float = float(os.getenv("DEFAULT_INITIAL_CAPITAL", "10000"))
    default_commission: float = float(os.getenv("DEFAULT_COMMISSION", "0.001"))
    
    # Rate limiting
    rate_limit_calls: int = 100
    rate_limit_period: int = 60  # seconds
    
    class Config:
        env_file = ".env"


settings = Settings()