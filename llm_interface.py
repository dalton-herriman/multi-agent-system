class LLMInterface:
    """Abstract base class for LLM provider."""
    def __init__(self, model_name: str, temperature: float = 0.7, max_tokens: int = 1000):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text response from prompt."""
        pass
    
    @abstractmethod
    async def generate_with_context(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response with conversation context."""
        pass

    def set_parameters(self, temperature: float = None, max_tokens: int = None):
        """Update generation parameters """
        if temperature is not None:
            self.temperature = temperature
        if max_tokens is not None:
            self.max_tokens = max_tokens

    
class OpenAILLMInterface(LLMInterface):
    pass

class AnthropicLLMInterface(LLMInterface):
    pass

class MockLLMInterface(LLMInterface):
    pass

def create_llm_interface():
    pass