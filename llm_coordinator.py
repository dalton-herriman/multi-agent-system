"""
LLM-Enhanced Coordinator for Multi-Agent System
Provides intelligent coordination between LLM agents.
"""

import json
from typing import Dict, List, Any, Optional
from coordinator_agent import CoordinatorAgent
from utils.llm_interface import create_llm_interface
from utils.logging_config import log_with_agent_id
import logging

logger = logging.getLogger(__name__)


class LLMCoordinator(CoordinatorAgent):
    """Coordinator enhanced with LLM reasoning for intelligent task decomposition."""

    def __init__(self, agent_id: str, message_bus, llm_provider: str = "mock"):
        super().__init__(agent_id, message_bus)

        # Initialize LLM for intelligent coordination
        self.llm = create_llm_interface(provider=llm_provider)

        # Enhanced task routes
        self.task_routes.update(
            {
                "coordinate_complex_task": self.handle_complex_task,
                "orchestrate_workflow": self.handle_workflow,
                "mediate_agents": self.handle_mediation,
                "optimize_plan": self.handle_optimization,
            }
        )

        # Available agent types for task assignment
        self.agent_capabilities = {
            "research_agent": ["research", "analyze", "synthesize", "trend_analysis"],
            "creative_agent": [
                "generate",
                "write_story",
                "create_content",
                "brainstorm",
            ],
            "llm_agent": ["analyze", "reason", "generate", "summarize", "plan"],
        }

    def llm_decompose(self, request: Dict) -> List[Dict]:
        """Use LLM to intelligently decompose a complex request."""
        try:
            request_text = json.dumps(request, indent=2)

            prompt = f"""
            Please decompose this complex request into subtasks for different agents:
            
            Request: {request_text}
            
            Available agent types and their capabilities:
            {json.dumps(self.agent_capabilities, indent=2)}
            
            Return a JSON array of subtasks, each with:
            - agent: target agent type
            - task: specific task to perform
            - payload: data for the task
            - priority: 1-5 (1=highest)
            - dependencies: list of subtask indices this depends on
            """

            response = self.llm.generate(prompt)

            # Try to parse JSON response
            try:
                subtasks = json.loads(response)
                if isinstance(subtasks, list):
                    return subtasks
            except json.JSONDecodeError:
                pass

            # Fallback to simple decomposition
            return self.fallback_decompose(request)

        except Exception as e:
            log_with_agent_id(
                logger, self.agent_id, logging.ERROR, f"LLM decomposition error: {e}"
            )
            return self.fallback_decompose(request)

    def fallback_decompose(self, request: Dict) -> List[Dict]:
        """Fallback decomposition when LLM fails."""
        data = request.get("data", {})
        task_type = request.get("type", "general")

        subtasks = []

        if task_type == "research":
            subtasks.append(
                {
                    "agent": "research_agent",
                    "task": "research",
                    "payload": {"topic": data.get("topic", "general research")},
                    "priority": 1,
                    "dependencies": [],
                }
            )
        elif task_type == "creative":
            subtasks.append(
                {
                    "agent": "creative_agent",
                    "task": "create_content",
                    "payload": {
                        "topic": data.get("topic", ""),
                        "content_type": "article",
                    },
                    "priority": 1,
                    "dependencies": [],
                }
            )
        else:
            subtasks.append(
                {
                    "agent": "llm_agent",
                    "task": "analyze",
                    "payload": {"data": data, "type": "general"},
                    "priority": 1,
                    "dependencies": [],
                }
            )

        return subtasks

    def handle_complex_task(self, sender: str, payload: Dict) -> None:
        """Handle complex tasks that require multiple agents."""
        log_with_agent_id(
            logger, self.agent_id, logging.INFO, f"Coordinating complex task: {payload}"
        )

        # Use LLM to decompose the task
        subtasks = self.llm_decompose(payload)

        # Execute subtasks in priority order
        executed_tasks = []
        for i, subtask in enumerate(subtasks):
            agent_type = subtask["agent"]
            task = subtask["task"]
            task_payload = subtask["payload"]

            # Check dependencies
            dependencies = subtask.get("dependencies", [])
            if dependencies and not all(
                dep < len(executed_tasks) for dep in dependencies
            ):
                log_with_agent_id(
                    logger,
                    self.agent_id,
                    logging.WARNING,
                    f"Dependencies not met for task {i}",
                )
                continue

            # Send task to appropriate agent
            self.send_message(agent_type, task, task_payload)
            executed_tasks.append(i)

            log_with_agent_id(
                logger,
                self.agent_id,
                logging.INFO,
                f"Sent task {task} to {agent_type} with priority {subtask.get('priority', 1)}",
            )

        # Send completion notification
        self.send_message(
            sender,
            "coordination_complete",
            {
                "subtasks": len(subtasks),
                "executed": len(executed_tasks),
                "original_request": payload,
            },
        )

    def handle_workflow(self, sender: str, payload: Dict) -> None:
        """Handle workflow orchestration."""
        workflow = payload.get("workflow", [])
        workflow_id = payload.get("workflow_id", "default")

        log_with_agent_id(
            logger, self.agent_id, logging.INFO, f"Orchestrating workflow {workflow_id}"
        )

        # Execute workflow steps
        for step in workflow:
            agent = step.get("agent")
            task = step.get("task")
            step_payload = step.get("payload", {})

            if agent and task:
                self.send_message(agent, task, step_payload)
                log_with_agent_id(
                    logger,
                    self.agent_id,
                    logging.INFO,
                    f"Workflow step: {task} -> {agent}",
                )

        self.send_message(
            sender,
            "workflow_complete",
            {"workflow_id": workflow_id, "steps": len(workflow)},
        )

    def handle_mediation(self, sender: str, payload: Dict) -> None:
        """Mediate between conflicting agents or requests."""
        conflict = payload.get("conflict", {})
        agents_involved = payload.get("agents", [])

        log_with_agent_id(
            logger,
            self.agent_id,
            logging.INFO,
            f"Mediating conflict between {agents_involved}",
        )

        # Use LLM to analyze conflict and suggest resolution
        prompt = f"""
        Please analyze this conflict and suggest a resolution:
        
        Conflict: {json.dumps(conflict, indent=2)}
        Agents involved: {agents_involved}
        
        Provide a fair and effective resolution strategy.
        """

        resolution = self.llm.generate(prompt)

        # Send resolution to involved agents
        for agent in agents_involved:
            self.send_message(
                agent,
                "mediation_result",
                {
                    "resolution": resolution,
                    "conflict": conflict,
                    "mediator": self.agent_id,
                },
            )

        self.send_message(
            sender,
            "mediation_complete",
            {"resolution": resolution, "agents_involved": agents_involved},
        )

    def handle_optimization(self, sender: str, payload: Dict) -> None:
        """Optimize agent allocation and task distribution."""
        current_plan = payload.get("plan", {})
        constraints = payload.get("constraints", {})

        log_with_agent_id(
            logger, self.agent_id, logging.INFO, "Optimizing agent allocation"
        )

        # Use LLM to optimize the plan
        prompt = f"""
        Please optimize this agent allocation plan:
        
        Current Plan: {json.dumps(current_plan, indent=2)}
        Constraints: {json.dumps(constraints, indent=2)}
        
        Suggest optimizations for efficiency, load balancing, and resource utilization.
        """

        optimization = self.llm.generate(prompt)

        self.send_message(
            sender,
            "optimization_complete",
            {
                "optimization": optimization,
                "original_plan": current_plan,
                "constraints": constraints,
            },
        )

    def handle_request(self, sender: str, payload: Dict) -> None:
        """Enhanced request handling with LLM assistance."""
        log_with_agent_id(
            logger, self.agent_id, logging.INFO, f"Received enhanced request: {payload}"
        )

        # Determine if this is a complex task that needs LLM decomposition
        if payload.get("complex", False) or len(payload.get("data", {})) > 3:
            self.handle_complex_task(sender, payload)
        else:
            # Use simple decomposition for basic requests
            for subtask in self.decompose_request(payload):
                self.send_message(subtask["agent"], subtask["task"], subtask["payload"])

    def decompose_request(self, payload: Dict) -> List[Dict]:
        """Enhanced request decomposition."""
        data = payload.get("data", {})
        request_type = payload.get("type", "general")

        if request_type == "research":
            return [{"agent": "research_agent", "task": "research", "payload": data}]
        elif request_type == "creative":
            return [
                {"agent": "creative_agent", "task": "create_content", "payload": data}
            ]
        elif request_type == "analysis":
            return [{"agent": "llm_agent", "task": "analyze", "payload": data}]
        else:
            return [{"agent": "llm_agent", "task": "process_data", "payload": data}]
