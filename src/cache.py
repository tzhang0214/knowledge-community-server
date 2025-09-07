"""
缓存管理模块
"""
import json
import hashlib
from typing import Optional, Any, Dict
import redis
from src.config import settings, CACHE_KEYS, CACHE_TTL


class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.redis_client = None
        if settings.redis_url:
            try:
                self.redis_client = redis.from_url(settings.redis_url)
                # 测试连接
                self.redis_client.ping()
            except Exception as e:
                print(f"Redis连接失败: {e}")
                self.redis_client = None
    
    def _generate_key(self, key_template: str, **kwargs) -> str:
        """生成缓存键"""
        return key_template.format(**kwargs)
    
    def _serialize(self, data: Any) -> str:
        """序列化数据"""
        return json.dumps(data, ensure_ascii=False, default=str)
    
    def _deserialize(self, data: str) -> Any:
        """反序列化数据"""
        return json.loads(data)
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if not self.redis_client:
            return None
        
        try:
            data = self.redis_client.get(key)
            if data:
                return self._deserialize(data.decode('utf-8'))
        except Exception as e:
            print(f"获取缓存失败: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """设置缓存"""
        if not self.redis_client:
            return False
        
        try:
            serialized_value = self._serialize(value)
            self.redis_client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            print(f"设置缓存失败: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"删除缓存失败: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        if not self.redis_client:
            return False
        
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            print(f"检查缓存失败: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> bool:
        """清除匹配模式的缓存"""
        if not self.redis_client:
            return False
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"清除缓存失败: {e}")
            return False


# 全局缓存管理器实例
cache_manager = CacheManager()


# 缓存装饰器
def cache_result(ttl: int = 3600):
    """缓存结果装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            func_name = func.__name__
            args_str = str(args) + str(sorted(kwargs.items()))
            cache_key = f"{func_name}:{hashlib.md5(args_str.encode()).hexdigest()}"
            
            # 尝试从缓存获取
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 缓存结果
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


# 知识库缓存函数
def get_cached_knowledge_categories():
    """获取缓存的知识分类"""
    return cache_manager.get(CACHE_KEYS["knowledge_categories"])


def set_cached_knowledge_categories(data: Dict[str, Any]):
    """设置缓存的知识分类"""
    return cache_manager.set(
        CACHE_KEYS["knowledge_categories"], 
        data, 
        CACHE_TTL["knowledge"]
    )


def get_cached_knowledge_item(item_id: int):
    """获取缓存的知识项"""
    key = cache_manager._generate_key(CACHE_KEYS["knowledge_item"], item_id=item_id)
    return cache_manager.get(key)


def set_cached_knowledge_item(item_id: int, data: Dict[str, Any]):
    """设置缓存的知识项"""
    key = cache_manager._generate_key(CACHE_KEYS["knowledge_item"], item_id=item_id)
    return cache_manager.set(key, data, CACHE_TTL["knowledge"])


# 搜索缓存函数
def get_cached_search_result(query: str):
    """获取缓存的搜索结果"""
    query_hash = hashlib.md5(query.encode()).hexdigest()
    key = cache_manager._generate_key(CACHE_KEYS["search_result"], query_hash=query_hash)
    return cache_manager.get(key)


def set_cached_search_result(query: str, data: Dict[str, Any]):
    """设置缓存的搜索结果"""
    query_hash = hashlib.md5(query.encode()).hexdigest()
    key = cache_manager._generate_key(CACHE_KEYS["search_result"], query_hash=query_hash)
    return cache_manager.set(key, data, CACHE_TTL["search"])


# 聊天缓存函数
def get_cached_chat_session(session_id: str):
    """获取缓存的聊天会话"""
    key = cache_manager._generate_key(CACHE_KEYS["chat_session"], session_id=session_id)
    return cache_manager.get(key)


def set_cached_chat_session(session_id: str, data: Dict[str, Any]):
    """设置缓存的聊天会话"""
    key = cache_manager._generate_key(CACHE_KEYS["chat_session"], session_id=session_id)
    return cache_manager.set(key, data, CACHE_TTL["chat"])


def clear_knowledge_cache():
    """清除知识库缓存"""
    cache_manager.clear_pattern("knowledge:*")




def clear_search_cache():
    """清除搜索缓存"""
    cache_manager.clear_pattern("search:*")


def clear_chat_cache():
    """清除聊天缓存"""
    cache_manager.clear_pattern("chat:*")


def clear_all_cache():
    """清除所有缓存"""
    cache_manager.clear_pattern("*")
