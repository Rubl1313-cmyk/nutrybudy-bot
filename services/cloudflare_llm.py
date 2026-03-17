"""
services/cloudflare_llm.py
Cloudflare LLM обёртка для LangChain с поддержкой function calling
"""
import os
import logging
from typing import List, Dict, Any, Optional
from langchain_cloudflare import ChatCloudflareWorkersAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

logger = logging.getLogger(__name__)

class CloudflareLLM:
    """Обёртка над Cloudflare Workers AI для LangChain"""
    
    def __init__(self, model: str = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"):
        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        
        if not self.account_id or not self.api_token:
            raise ValueError(
                "❌ Cloudflare credentials not found. "
                "Please set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN environment variables."
            )
        
        self.llm = ChatCloudflareWorkersAI(
            account_id=self.account_id,
            api_token=self.api_token,
            model=model,
            temperature=0.2,
            max_tokens=2000,
            top_p=0.9,
        )
        logger.info(f"✅ Cloudflare LLM initialized: {model}")

    async def ainvoke(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> AIMessage:
        """
        Вызов модели с поддержкой инструментов (function calling)
        
        Args:
            messages: Список сообщений в формате [{"role": "user|system|assistant", "content": "..."}]
            tools: Список инструментов для function calling
            
        Returns:
            AIMessage с ответом модели
        """
        if not self.llm:
            raise RuntimeError("Cloudflare LLM not initialized")
        
        try:
            # Конвертируем сообщения в формат LangChain
            lc_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    lc_messages.append(SystemMessage(content=msg["content"]))
                elif msg["role"] == "user":
                    lc_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    lc_messages.append(AIMessage(content=msg["content"]))
            
            # Если есть инструменты, передаём их
            if tools:
                response = await self.llm.ainvoke(lc_messages, tools=tools)
            else:
                response = await self.llm.ainvoke(lc_messages)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in Cloudflare LLM: {e}")
            return AIMessage(content=f"❌ Ошибка AI: {str(e)}")

    def is_available(self) -> bool:
        """Проверяет доступность LLM"""
        return self.llm is not None

# Глобальный экземпляр для использования во всём приложении
cloudflare_llm = CloudflareLLM()
