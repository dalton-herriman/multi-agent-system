"""
LLM-Enhanced Agent for Multi-Agent System
Provides agents with LLM reasoning capabilities.
"""

import json
from typing import Dict, List, Any, Optional
from agent import Agent
from utils.llm_interface import create_llm_interface, LLMInterface
from utils.logging_config import log_with_agent_id
import logging

logger = logging.getLogger(__name__)


class LLMAgent(Agent):
    """Agent enhanced with LLM reasoning capabilities."""

    def __init__(
        self,
        agent_id: str,
        message_bus=None,
        max_context=100,
        llm_provider: str = "mock",
        llm_config: Dict = None,
    ):
        super().__init__(agent_id, message_bus, max_context)

        # Initialize LLM
        self.llm_config = llm_config or {}
        self.llm = create_llm_interface(provider=llm_provider, **self.llm_config)

        # Enhanced task routes with LLM capabilities
        self.task_routes.update(
            {
                "analyze": self.handle_analyze,
                "reason": self.handle_reason,
                "generate": self.handle_generate,
                "summarize": self.handle_summarize,
                "plan": self.handle_plan,
            }
        )

        # Agent personality and capabilities
        self.personality = self.llm_config.get(
            "personality", "You are a helpful AI assistant."
        )
        self.capabilities = self.llm_config.get(
            "capabilities",
            ["data analysis", "text generation", "reasoning", "planning"],
        )

    def llm_reason(self, prompt: str, context: List[Dict] = None) -> str:
        """Use LLM for reasoning."""
        try:
            # Prepare context for LLM
            messages = []

            # Add system message with personality and capabilities
            system_msg = f"{self.personality}\n\nYour capabilities: {', '.join(self.capabilities)}"
            messages.append({"role": "system", "content": system_msg})

            # Add conversation context if provided
            if context:
                for msg in context[-5:]:  # Last 5 messages for context
                    role = "user" if msg.get("sender") != self.agent_id else "assistant"
                    content = f"Task: {msg.get('task', '')}\nPayload: {msg.get('payload', {})}"
                    messages.append({"role": role, "content": content})

            # Add current prompt
            messages.append({"role": "user", "content": prompt})

            # Generate response
            response = self.llm.generate_with_context(messages)
            return response

        except Exception as e:
            log_with_agent_id(
                logger, self.agent_id, logging.ERROR, f"LLM reasoning error: {e}"
            )
            return f"Error in reasoning: {e}"

    def handle_analyze(self, sender: str, payload: Dict) -> None:
        """Analyze data using LLM."""
        data = payload.get("data", {})
        analysis_type = payload.get("type", "general")

        prompt = f"""
        Please analyze the following data for {analysis_type} analysis:
        
        Data: {json.dumps(data, indent=2)}
        
        Provide insights, patterns, and recommendations.
        """

        analysis = self.llm_reason(prompt)

        # Send analysis results back
        self.send_message(
            sender,
            "analysis_complete",
            {
                "analysis": analysis,
                "original_data": data,
                "analysis_type": analysis_type,
            },
        )

    def handle_reason(self, sender: str, payload: Dict) -> None:
        """Use LLM for reasoning about a problem."""
        problem = payload.get("problem", "")
        context = payload.get("context", [])

        prompt = f"""
        Please help me reason about this problem:
        
        Problem: {problem}
        
        Consider the context and provide a thoughtful analysis with possible solutions.
        """

        reasoning = self.llm_reason(prompt, context)

        self.send_message(
            sender,
            "reasoning_complete",
            {"reasoning": reasoning, "original_problem": problem},
        )

    def handle_generate(self, sender: str, payload: Dict) -> None:
        """Generate content using LLM."""
        content_type = payload.get("type", "text")
        requirements = payload.get("requirements", "")

        prompt = f"""
        Please generate {content_type} content with the following requirements:
        
        Requirements: {requirements}
        
        Generate high-quality, relevant content.
        """

        generated_content = self.llm_reason(prompt)

        self.send_message(
            sender,
            "generation_complete",
            {
                "content": generated_content,
                "content_type": content_type,
                "requirements": requirements,
            },
        )

    def handle_summarize(self, sender: str, payload: Dict) -> None:
        """Summarize content using LLM."""
        content = payload.get("content", "")
        summary_type = payload.get("summary_type", "general")

        prompt = f"""
        Please provide a {summary_type} summary of the following content:
        
        Content: {content}
        
        Create a concise, informative summary.
        """

        summary = self.llm_reason(prompt)

        self.send_message(
            sender,
            "summary_complete",
            {
                "summary": summary,
                "summary_type": summary_type,
                "original_length": len(content),
            },
        )

    def handle_plan(self, sender: str, payload: Dict) -> None:
        """Create a plan using LLM."""
        goal = payload.get("goal", "")
        constraints = payload.get("constraints", [])

        prompt = f"""
        Please create a detailed plan to achieve this goal:
        
        Goal: {goal}
        Constraints: {constraints}
        
        Provide a step-by-step plan with timelines and resources needed.
        """

        plan = self.llm_reason(prompt)

        self.send_message(
            sender,
            "plan_complete",
            {"plan": plan, "goal": goal, "constraints": constraints},
        )


class ResearchAgent(LLMAgent):
    """Specialized research agent with enhanced analysis capabilities."""

    def __init__(self, agent_id: str, message_bus=None, llm_provider: str = "mock"):
        research_config = {
            "personality": "You are a research assistant specialized in data analysis and information synthesis.",
            "capabilities": [
                "research",
                "data analysis",
                "information synthesis",
                "trend analysis",
            ],
        }

        super().__init__(
            agent_id, message_bus, llm_provider=llm_provider, llm_config=research_config
        )

        # Add research-specific tasks
        self.task_routes.update(
            {
                "research": self.handle_research,
                "synthesize": self.handle_synthesize,
                "trend_analysis": self.handle_trend_analysis,
            }
        )

    def handle_research(self, sender: str, payload: Dict) -> None:
        """Conduct research on a topic."""
        topic = payload.get("topic", "")
        depth = payload.get("depth", "moderate")

        prompt = f"""
        Please conduct {depth} research on the following topic:
        
        Topic: {topic}
        
        Provide comprehensive information, key findings, and relevant sources.
        """

        research_results = self.llm_reason(prompt)

        self.send_message(
            sender,
            "research_complete",
            {"topic": topic, "results": research_results, "depth": depth},
        )

    def handle_synthesize(self, sender: str, payload: Dict) -> None:
        """Synthesize information from multiple sources."""
        sources = payload.get("sources", [])
        synthesis_type = payload.get("type", "comprehensive")

        prompt = f"""
        Please synthesize information from the following sources:
        
        Sources: {json.dumps(sources, indent=2)}
        
        Provide a {synthesis_type} synthesis that identifies patterns, contradictions, and insights.
        """

        synthesis = self.llm_reason(prompt)

        self.send_message(
            sender,
            "synthesis_complete",
            {
                "synthesis": synthesis,
                "synthesis_type": synthesis_type,
                "source_count": len(sources),
            },
        )

    def handle_trend_analysis(self, sender: str, payload: Dict) -> None:
        """Analyze trends in data."""
        data = payload.get("data", {})
        time_period = payload.get("time_period", "recent")

        prompt = f"""
        Please analyze trends in the following data over {time_period}:
        
        Data: {json.dumps(data, indent=2)}
        
        Identify patterns, trends, and potential future developments.
        """

        trend_analysis = self.llm_reason(prompt)

        self.send_message(
            sender,
            "trend_analysis_complete",
            {
                "analysis": trend_analysis,
                "time_period": time_period,
                "data_points": len(data) if isinstance(data, (list, dict)) else 0,
            },
        )


class CreativeAgent(LLMAgent):
    """Specialized creative agent for content generation."""

    def __init__(self, agent_id: str, message_bus=None, llm_provider: str = "mock"):
        creative_config = {
            "personality": "You are a creative assistant with expertise in writing, storytelling, and artistic expression.",
            "capabilities": [
                "creative writing",
                "storytelling",
                "content creation",
                "artistic expression",
            ],
        }

        super().__init__(
            agent_id, message_bus, llm_provider=llm_provider, llm_config=creative_config
        )

        # Add creative-specific tasks
        self.task_routes.update(
            {
                "write_story": self.handle_write_story,
                "create_content": self.handle_create_content,
                "brainstorm": self.handle_brainstorm,
            }
        )

    def handle_write_story(self, sender: str, payload: Dict) -> None:
        """Write a creative story."""
        genre = payload.get("genre", "general")
        theme = payload.get("theme", "")
        length = payload.get("length", "medium")

        prompt = f"""
        Please write a {length} {genre} story with the theme: {theme}
        
        Make it engaging, creative, and well-structured.
        """

        story = self.llm_reason(prompt)

        self.send_message(
            sender,
            "story_complete",
            {"story": story, "genre": genre, "theme": theme, "length": length},
        )

    def handle_create_content(self, sender: str, payload: Dict) -> None:
        """Create various types of content."""
        content_type = payload.get("content_type", "article")
        topic = payload.get("topic", "")
        style = payload.get("style", "professional")

        prompt = f"""
        Please create {content_type} content about: {topic}
        
        Style: {style}
        
        Make it engaging, informative, and well-crafted.
        """

        content = self.llm_reason(prompt)

        self.send_message(
            sender,
            "content_complete",
            {
                "content": content,
                "content_type": content_type,
                "topic": topic,
                "style": style,
            },
        )

    def handle_brainstorm(self, sender: str, payload: Dict) -> None:
        """Brainstorm ideas."""
        topic = payload.get("topic", "")
        idea_count = payload.get("idea_count", 5)

        prompt = f"""
        Please brainstorm {idea_count} creative ideas about: {topic}
        
        Provide diverse, innovative, and practical ideas.
        """

        ideas = self.llm_reason(prompt)

        self.send_message(
            sender,
            "brainstorm_complete",
            {"ideas": ideas, "topic": topic, "idea_count": idea_count},
        )
