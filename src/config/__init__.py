"""Centralized configuration system using Pydantic."""

from pydantic import BaseSettings, Field, validator
from typing import Optional, List
import os
from pathlib import Path


class AppConfig(BaseSettings):
    """Application configuration with environment variable support."""
    
    # Data configuration
    data_provider: str = Field(default="yahoo", env="DATA_PROVIDER")
    data_cache_enabled: bool = Field(default=True, env="DATA_CACHE_ENABLED")
    data_cache_ttl: int = Field(default=3600, env="DATA_CACHE_TTL")  # 1 hour
    
    # LLM configuration
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    default_ollama_model: str = Field(default="qwen3.5:latest", env="DEFAULT_OLLAMA_MODEL")
    llm_timeout: int = Field(default=30, env="LLM_TIMEOUT")
    llm_max_retries: int = Field(default=3, env="LLM_MAX_RETRIES")
    
    # API keys (optional)
    financial_datasets_api_key: Optional[str] = Field(default=None, env="FINANCIAL_DATASETS_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    deepseek_api_key: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    
    # Performance configuration
    max_concurrent_requests: int = Field(default=5, env="MAX_CONCURRENT_REQUESTS")
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    
    # Logging configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/ai_hedge_fund.log", env="LOG_FILE")
    log_max_size: int = Field(default=10, env="LOG_MAX_SIZE_MB")  # MB
    log_backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")
    
    # Backtesting configuration
    default_initial_capital: float = Field(default=100000.0, env="DEFAULT_INITIAL_CAPITAL")
    default_margin_requirement: float = Field(default=0.0, env="DEFAULT_MARGIN_REQUIREMENT")
    
    # Redis configuration (optional)
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    @validator('data_provider')
    def validate_data_provider(cls, v):
        valid_providers = ['yahoo', 'financialdatasets']
        if v not in valid_providers:
            raise ValueError(f"Data provider must be one of {valid_providers}")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra environment variables
        
        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            # Prioritize environment variables over init settings
            return env_settings, init_settings, file_secret_settings


# Global configuration instance
config = AppConfig()


def reload_config() -> AppConfig:
    """Reload configuration from environment."""
    global config
    config = AppConfig()
    return config


def get_config() -> AppConfig:
    """Get the current configuration instance."""
    return config


# Export the configuration
__all__ = ['AppConfig', 'config', 'reload_config', 'get_config']