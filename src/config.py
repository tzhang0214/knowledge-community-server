"""
配置管理模块
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置类"""
    
    # 数据库配置
    database_url: str = Field(default="sqlite:///./isp_knowledge.db", env="DATABASE_URL")
    
    # QWEN API配置
    qwen_api_key: str = Field(..., env="QWEN_API_KEY")
    qwen_base_url: str = Field(default="https://dashscope.aliyuncs.com/api/v1", env="QWEN_BASE_URL")
    
    # JWT配置
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Redis配置
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # 服务器配置
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # 日志配置
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()

# QWEN模型配置
QWEN_CONFIG = {
    "model_name": "qwen-turbo",
    "api_key": settings.qwen_api_key,
    "base_url": settings.qwen_base_url,
    "max_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.9
}

# 缓存键设计
CACHE_KEYS = {
    "knowledge_categories": "knowledge:categories",
    "knowledge_item": "knowledge:item:{item_id}",
    "flow_version": "flow:version:{version_id}",
    "flow_module": "flow:module:{module_id}",
    "search_result": "search:result:{query_hash}",
    "chat_session": "chat:session:{session_id}"
}

# 缓存过期时间
CACHE_TTL = {
    "knowledge": 3600,      # 1小时
    "flow": 1800,          # 30分钟
    "search": 300,         # 5分钟
    "chat": 1800          # 30分钟
}

# 日志配置
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": settings.log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "": {
            "handlers": ["default", "file"],
            "level": settings.log_level,
            "propagate": False
        }
    }
}
