"""
LLM Client implementations for Claude, OpenAI, and LM Studio
Provides unified interface for different LLM providers
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import json


class LLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Send chat messages to LLM and get response
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            str: LLM response content
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if connection to LLM is working"""
        pass


class ClaudeClient(LLMClient):
    """Claude API client"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", **kwargs):
        """
        Initialize Claude client
        
        Args:
            api_key: Anthropic API key
            model: Claude model name
        """
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
        
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.default_params = kwargs
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat to Claude"""
        # Merge default params with call-specific params
        params = {**self.default_params, **kwargs}
        
        # Extract system message if present
        system_message = None
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)
        
        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=params.get("max_tokens", 2000),
            temperature=params.get("temperature", 0.1),
            system=system_message if system_message else "",
            messages=user_messages
        )
        
        return response.content[0].text
    
    def test_connection(self) -> bool:
        """Test Claude API connection"""
        try:
            response = self.chat([
                {"role": "user", "content": "Hello"}
            ], max_tokens=10)
            return len(response) > 0
        except Exception as e:
            print(f"Claude connection test failed: {e}")
            return False


class OpenAIClient(LLMClient):
    """OpenAI API client"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o", **kwargs):
        """
        Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model name
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.default_params = kwargs
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat to OpenAI"""
        params = {**self.default_params, **kwargs}
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=params.get("temperature", 0.1),
            max_tokens=params.get("max_tokens", 2000)
        )
        
        return response.choices[0].message.content
    
    def test_connection(self) -> bool:
        """Test OpenAI API connection"""
        try:
            response = self.chat([
                {"role": "user", "content": "Hello"}
            ], max_tokens=10)
            return len(response) > 0
        except Exception as e:
            print(f"OpenAI connection test failed: {e}")
            return False


class LMStudioClient(LLMClient):
    """LM Studio local LLM client (OpenAI-compatible)"""
    
    def __init__(self, base_url: str = "http://localhost:1234", model: str = "local-model", **kwargs):
        """
        Initialize LM Studio client
        
        Args:
            base_url: LM Studio server URL
            model: Model name (usually "local-model")
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        self.client = OpenAI(
            base_url=f"{base_url}/v1",
            api_key="lm-studio"  # Dummy key for local server
        )
        self.model = model
        self.base_url = base_url
        self.default_params = kwargs
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat to LM Studio"""
        params = {**self.default_params, **kwargs}
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=params.get("temperature", 0.1),
            max_tokens=params.get("max_tokens", 2000)
        )
        
        return response.choices[0].message.content
    
    def test_connection(self) -> bool:
        """Test LM Studio connection"""
        try:
            response = self.chat([
                {"role": "user", "content": "Hello"}
            ], max_tokens=10)
            return len(response) > 0
        except Exception as e:
            print(f"LM Studio connection test failed: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """List available models in LM Studio"""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            print(f"Failed to list models: {e}")
            return []


class LLMFactory:
    """Factory for creating LLM clients"""
    
    @staticmethod
    def create(provider: str, **config) -> LLMClient:
        """
        Create LLM client based on provider
        
        Args:
            provider: 'claude', 'openai', or 'lm_studio'
            **config: Configuration parameters
        
        Returns:
            LLMClient: Configured LLM client
        
        Raises:
            ValueError: If provider is unknown
        """
        provider = provider.lower()
        
        if provider == "claude":
            api_key = config.get("claude_api_key")
            if not api_key:
                raise ValueError("claude_api_key is required for Claude provider")
            
            return ClaudeClient(
                api_key=api_key,
                model=config.get("model", "claude-3-5-sonnet-20241022"),
                temperature=config.get("temperature", 0.1),
                max_tokens=config.get("max_tokens", 2000)
            )
        
        elif provider == "openai":
            api_key = config.get("openai_api_key")
            if not api_key:
                raise ValueError("openai_api_key is required for OpenAI provider")
            
            return OpenAIClient(
                api_key=api_key,
                model=config.get("model", "gpt-4o"),
                temperature=config.get("temperature", 0.1),
                max_tokens=config.get("max_tokens", 2000)
            )
        
        elif provider == "lm_studio":
            return LMStudioClient(
                base_url=config.get("lm_studio_url", "http://localhost:1234"),
                model=config.get("lm_studio_model", "local-model"),
                temperature=config.get("temperature", 0.1),
                max_tokens=config.get("max_tokens", 2000)
            )
        
        else:
            raise ValueError(f"Unknown LLM provider: {provider}. Use 'claude', 'openai', or 'lm_studio'")
