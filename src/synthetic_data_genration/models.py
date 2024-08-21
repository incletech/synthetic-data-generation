import os
from collections import deque
from typing import List, Optional, Dict, Any

from openai import AsyncOpenAI
from groq import AsyncGroq
from together import AsyncTogether

class ClientInitializerLlm:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ClientInitializerLlm, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'): 
            self.initialized = True
            together_ai_keys = [os.getenv(f"together_ai{i}") for i in range(11)]
            if not all(together_ai_keys):
                raise ValueError("One or more Together AI API keys are missing.")
            
            self.together_ai_keys = deque(together_ai_keys)
            self.api_keys = {
                'groq': os.getenv("groq_api"),
                'aimlapi': os.getenv("aiml_api")
            }
            self.clients = {
                'groq': self.init_groq_client(),
                'aimlapi': self.init_aimlapi_client(),
                'together_ai': self.init_together_ai_client()
            }

    def init_groq_client(self):
        api_key = self.api_keys['groq']
        if not api_key:
            raise ValueError("Groq API key is missing.")
        return AsyncGroq(api_key=api_key)

    def init_aimlapi_client(self):
        api_key = self.api_keys['aimlapi']
        if not api_key:
            raise ValueError("AIML API key is missing.")
        return AsyncOpenAI(api_key=api_key, base_url="https://api.aimlapi.com")

    def init_together_ai_client(self):
        api_key = self.together_ai_keys[0] 
        if not api_key:
            raise ValueError("Together AI API key is missing.")
        return AsyncTogether(api_key=api_key)

    def rotate_together_ai_client(self):
        self.together_ai_keys.rotate(-1)
        new_key = self.together_ai_keys[0]
        print(f"Rotated to new Together AI API key: {new_key}")
        self.clients['together_ai'] = self.init_together_ai_client()

    def get_client(self, client_name):
        return self.clients.get(client_name)

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

    async def json_completion(self, messages: List[Dict[str, Any]], response_format={"type": "json_object"}):
        return await self._create_completion(messages, response_format)

    async def function_calling(self, messages: List[Dict[str, Any]]):
        return await self._create_completion(messages)

    async def rotate_client(self, client_name: str):
        initializer = ClientInitializerLlm()
        initializer.rotate_together_ai_client() 
        self.client = initializer.get_client(client_name) 
