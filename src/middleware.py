"""
认证中间件
统一处理token验证，避免在每个业务接口中重复验证
"""
import logging
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.auth import verify_token

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件"""
    
    # 不需要认证的路径列表
    EXCLUDED_PATHS = {
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh",
    }
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        # 检查是否需要跳过认证
        if self._should_skip_auth(request):
            return await call_next(request)
        
        # 获取token
        token = self._extract_token(request)
        if not token:
            return self._unauthorized_response("缺少认证token")
        
        # 验证token
        try:
            user_info = verify_token(token)
            if not user_info:
                return self._unauthorized_response("无效的认证token")
            
            # 将用户信息添加到请求状态中，供后续使用
            request.state.user = user_info
            logger.debug(f"用户 {user_info.get('sub')} 认证成功")
        except Exception as e:
            logger.warning(f"Token验证失败: {e}")
            return self._unauthorized_response("无效的认证token")
        
        # 继续处理请求
        return await call_next(request)
    
    def _should_skip_auth(self, request: Request) -> bool:
        """判断是否应该跳过认证"""
        path = request.url.path
        
        # 检查完全匹配的路径
        if path in self.EXCLUDED_PATHS:
            return True
        
        # 检查以某些前缀开头的路径
        excluded_prefixes = ["/static/", "/favicon.ico"]
        for prefix in excluded_prefixes:
            if path.startswith(prefix):
                return True
        
        return False
    
    def _extract_token(self, request: Request) -> str:
        """从请求中提取token"""
        # 优先从Authorization头获取 
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # 移除"Bearer "前缀
        
        # 也可以从查询参数获取（可选）
        return request.query_params.get("token", "")
    
    def _unauthorized_response(self, message: str) -> JSONResponse:
        """返回未授权响应"""
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "message": message,
                "error_code": "UNAUTHORIZED"
            }
        )
