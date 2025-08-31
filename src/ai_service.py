"""
AI服务模块 - QWEN大模型集成
"""
import hashlib
import json
import time
from typing import List, Dict, Any, Optional
import httpx
from src.config import QWEN_CONFIG


class QWENService:
    """QWEN AI服务类"""
    
    def __init__(self):
        self.api_key = QWEN_CONFIG["api_key"]
        self.base_url = QWEN_CONFIG["base_url"]
        self.model_name = QWEN_CONFIG["model_name"]
        self.max_tokens = QWEN_CONFIG["max_tokens"]
        self.temperature = QWEN_CONFIG["temperature"]
        self.top_p = QWEN_CONFIG["top_p"]
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """聊天完成"""
        start_time = time.time()
        
        # 构建请求数据
        request_data = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "stream": False
        }
        
        # 添加上下文信息
        if context:
            system_message = {
                "role": "system",
                "content": f"你是ISP知识库系统的AI助手。请基于以下上下文回答问题：\n{context}"
            }
            request_data["messages"].insert(0, system_message)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/services/aigc/text-generation/generation",
                    headers=headers,
                    json=request_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_time = int((time.time() - start_time) * 1000)
                    
                    return {
                        "success": True,
                        "response": result.get("output", {}).get("text", ""),
                        "response_time_ms": response_time,
                        "usage": result.get("usage", {})
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API请求失败: {response.status_code}",
                        "response_time_ms": int((time.time() - start_time) * 1000)
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"请求异常: {str(e)}",
                "response_time_ms": int((time.time() - start_time) * 1000)
            }
    
    async def generate_answer(
        self, 
        question: str, 
        knowledge_context: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """生成答案"""
        messages = []
        
        # 添加聊天历史
        if chat_history:
            messages.extend(chat_history)
        
        # 添加当前问题
        messages.append({
            "role": "user",
            "content": question
        })
        
        # 构建知识上下文
        context = ""
        if knowledge_context:
            context = f"相关知识：\n{knowledge_context}\n\n请基于以上知识回答用户问题。"
        
        return await self.chat_completion(messages, context)
    
    async def search_enhancement(
        self, 
        query: str, 
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """搜索增强"""
        # 构建搜索结果的上下文
        context_parts = []
        for i, result in enumerate(search_results[:5], 1):  # 限制前5个结果
            context_parts.append(f"{i}. {result.get('title', '')}: {result.get('description', '')}")
        
        context = "搜索结果：\n" + "\n".join(context_parts)
        
        # 构建问题
        enhanced_query = f"基于以下搜索结果，请为用户查询'{query}'提供更详细的解释和建议："
        
        messages = [
            {
                "role": "user",
                "content": enhanced_query
            }
        ]
        
        return await self.chat_completion(messages, context)
    
    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取逻辑
        # 在实际项目中可以使用更复杂的NLP技术
        stop_words = {"的", "是", "在", "有", "和", "与", "或", "但", "而", "如果", "因为", "所以"}
        words = text.split()
        keywords = [word for word in words if word not in stop_words and len(word) > 1]
        return keywords[:10]  # 返回前10个关键词
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（简单实现）"""
        # 这里使用简单的Jaccard相似度
        # 在实际项目中可以使用更复杂的向量相似度算法
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if len(union) == 0:
            return 0.0
        
        return len(intersection) / len(union)


# 全局AI服务实例
ai_service = QWENService()
