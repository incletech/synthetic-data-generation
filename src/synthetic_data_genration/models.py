from typing import List, Optional, Dict, Any
from openai import AsyncOpenAI
from groq import AsyncGroq
from together import AsyncTogether
import os


class ClientInitializerLlm:
    def __init__(self):
        self.clients = {
            'openai': self.init_openai_client(),
            'groq': self.init_groq_client(),
            'aimlapi': self.init_aimlapi_client(),
            'together_ai' : self.init_together_ai_client()
        }

    def init_groq_client(self):
        api_key = os.getenv("groq_api")
        if not api_key:
            raise ValueError("Groq API key is missing.")
        return AsyncGroq(api_key=api_key)

    def init_openai_client(self):
        api_key = os.getenv("openai_api")
        if not api_key:
            raise ValueError("OpenAI API key is missing.")
        return AsyncOpenAI(api_key=api_key)

    def init_aimlapi_client(self):
        api_key = os.getenv("aiml_api")
        if not api_key:
            raise ValueError("AIML API key is missing.")
        return AsyncOpenAI(api_key=api_key, base_url="https://api.aimlapi.com")
    
    def init_together_ai_client(self):
        api_key = os.getenv("together_ai")
        if not api_key:
            raise ValueError("AIML API key is missing.")
        return AsyncTogether(api_key=api_key)

    def get_client(self, client_name: str):
        client = self.clients.get(client_name)
        return client


class LlmModel:
    def __init__(self, client, model: str, temperature: float, max_tokens: int, tools: Optional[List[Any]] = None):
        self.client = client
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.tools = tools

    @staticmethod
    def from_config(client_name: str, model: str, temperature: float, max_tokens: int, tools: Optional[List[Any]] = None):
        initializer = ClientInitializerLlm()
        client = initializer.get_client(client_name)
        if not client:
            raise ValueError(f"Client '{client_name}' not found.")
        return LlmModel(client, model, temperature, max_tokens, tools)

    async def _create_completion(self, messages: List[Dict[str, Any]], response_format: Optional[Dict[str, str]] = None):
        try:
            params = {
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "messages": messages,
            }
            if response_format:
                params["response_format"] = response_format
            if self.tools:
                params["tools"] = self.tools
                params["tool_choice"] = "auto"
                
            response = await self.client.chat.completions.create(**params)
            return response
        except Exception as e:
            raise RuntimeError(f"Failed to create completion: {e}")

    async def text_completion(self, messages: List[Dict[str, Any]]):
        return await self._create_completion(messages)

    async def json_completion(self, messages: List[Dict[str, Any]]):
        response_format = {"type": "json_object"}
        return await self._create_completion(messages, response_format)

    async def function_calling(self, messages: List[Dict[str, Any]]):
        return await self._create_completion(messages)

