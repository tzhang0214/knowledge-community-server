"""
ISP知识库系统后端服务主应用
"""
import os
import logging.config
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from src.config import settings, LOGGING_CONFIG
from src.database import init_db
from src.routers import auth, knowledge, search, chat, admin
from src.middleware import AuthMiddleware


# 配置日志
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("正在启动ISP知识库系统...")
    
    # 初始化数据库
    try:
        init_db()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise
    
    logger.info("ISP知识库系统启动完成")
    
    yield
    
    # 关闭时执行
    logger.info("正在关闭ISP知识库系统...")


# 创建FastAPI应用
app = FastAPI(
    title="ISP知识库系统",
    description="ISP知识库系统后端服务，提供知识库管理、架构图展示和AI智能问答功能",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS（必须先添加，这样CORS会先处理预检请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # 允许前端域名
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 添加认证中间件（在CORS之后添加）
app.add_middleware(AuthMiddleware)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "error_code": "INTERNAL_ERROR"
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": f"HTTP_{exc.status_code}"
        }
    )


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "ISP知识库系统",
        "version": "1.0.0"
    }


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "ISP知识库系统后端服务",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# 注册路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(knowledge.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="warning"  # 设置为warning级别，减少日志输出
    )
