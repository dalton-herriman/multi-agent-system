"""
LLM Interface for Multi-Agent System
Provides a unified interface for different LLM providers.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class LLMInterface(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, model_name: str = None, temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = 1000

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text response from prompt."""
        pass

    @abstractmethod
    def generate_with_context(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response with conversation context."""
        pass

    def set_parameters(self, temperature: float = None, max_tokens: int = None):
        """Update generation parameters."""
        if temperature is not None:
            self.temperature = temperature
        if max_tokens is not None:
            self.max_tokens = max_tokens


class MockLLMInterface(LLMInterface):
    """Mock LLM for testing without API calls."""

    def __init__(self, model_name: str = "mock-llm", temperature: float = 0.7):
        super().__init__(model_name, temperature)
        self.responses = {
            "ping": "I'm here and ready to help!",
            "process_data": "I've processed the data and found some interesting patterns.",
            "analyze": "Based on my analysis, here are the key insights...",
            "research": "I've researched the topic and found relevant information.",
            "generate": "I've generated the requested content.",
            "summarize": "Here's a concise summary of the content.",
            "plan": "I've created a detailed plan to achieve your goal.",
            "default": "I understand your request and will help you with that.",
        }

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate mock response based on prompt content."""
        prompt_lower = prompt.lower()

        for key, response in self.responses.items():
            if key in prompt_lower:
                return response

        return self.responses["default"]

    def generate_with_context(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate mock response with context."""
        if not messages:
            return self.responses["default"]

        last_message = messages[-1].get("content", "").lower()
        for key, response in self.responses.items():
            if key in last_message:
                return response

        return self.responses["default"]


class OpenAIInterface(LLMInterface):
    """OpenAI API interface."""

    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        super().__init__(model_name, temperature)
        try:
            import openai

            self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
        except Exception as e:
            raise Exception(f"Failed to initialize OpenAI client: {e}")

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"Error generating response: {e}"

    def generate_with_context(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response with conversation context."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"Error generating response: {e}"


def create_llm_interface(provider: str = "mock", **kwargs) -> LLMInterface:
    """Factory function to create LLM interface."""
    providers = {"openai": OpenAIInterface, "mock": MockLLMInterface}

    if provider not in providers:
        raise ValueError(
            f"Unknown LLM provider: {provider}. Available: {list(providers.keys())}"
        )

    return providers[provider](**kwargs)
