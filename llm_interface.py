import os
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

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
            logger.info(f"Setting temperature to {temperature}")
            self.temperature = temperature
        if max_tokens is not None:
            logger.info(f"Setting max tokens to {max_tokens}")
            self.max_tokens = max_tokens

    
class OpenAILLMInterface(LLMInterface):
    """ Open AI's API interface """
    def __init__(self, model_name: str = "gpt-4.1-nano", temperature: float = 0.7, max_tokens: int = 1000):
        super().__init__(model_name, temperature, max_tokens)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        try: 
            import openai
            self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except ImportError:
            logger.error("OpenAI is not installed. Please install it with 'pip install openai'.")
            raise ImportError("OpenAI is not installed. Please install it with 'pip install openai'.")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {e}")
            raise Exception(f"Error initializing OpenAI client: {e}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text response using OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise Exception(f"Error generating text: {e}")

    async def generate_with_context(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response with conversation context."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating text with context: {e}")
            raise Exception(f"Error generating text with context: {e}")
        
        
class AnthropicLLMInterface(LLMInterface):
    """ Anthropic's API interface """
    def __init__(self, model_name: str = "claude-3-5-sonnet-20240620", temperature: float = 0.7, max_tokens: int = 1000):
        super().__init__(model_name, temperature, max_tokens)
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        except ImportError:
            logger.error("Anthropic is not installed. Please install it with 'pip install anthropic'.")
            raise ImportError("Anthropic is not installed. Please install it with 'pip install anthropic'.")
        except Exception as e:
            logger.error(f"Error initializing Anthropic client: {e}")
            raise Exception(f"Error initializing Anthropic client: {e}")

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text response using Anthropic."""
        try:
            response = self.client.messages.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise Exception(f"Error generating text: {e}")
        
    async def generate_with_context(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response with conversation context."""
        try:
            response = self.client.messages.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating text with context: {e}")
            raise Exception(f"Error generating text with context: {e}")
        
        

class MockLLMInterface(LLMInterface):
    pass

def create_llm_interface():
    pass