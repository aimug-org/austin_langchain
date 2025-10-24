"""Base agent class for all newsletter generation agents."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.chat_models.base import BaseChatModel
from langsmith import traceable

from discord_bot.core.config import settings
from discord_bot.core.logging import get_logger
from discord_bot.agents.state import NewsletterState, AgentResponse

logger = get_logger(__name__)


class BaseNewsletterAgent(ABC):
    """Base class for all newsletter generation agents."""
    
    def __init__(
        self, 
        name: str,
        role: str,
        model: Optional[BaseChatModel] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        self.name = name
        self.role = role
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._system_prompt = self._create_system_prompt()
        
    @abstractmethod
    def _create_system_prompt(self) -> str:
        """Create the system prompt for this agent."""
        pass
    
    @abstractmethod
    async def process(self, state: NewsletterState) -> AgentResponse:
        """Process the current state and return a response."""
        pass
    
    @traceable(name="agent_invoke")
    async def invoke(self, state: NewsletterState) -> AgentResponse:
        """Invoke the agent with error handling and tracing."""
        start_time = datetime.now()
        
        try:
            logger.info(f"Agent {self.name} starting processing", extra={
                "agent": self.name,
                "step": state.get("current_step", "unknown")
            })
            
            response = await self.process(state)
            
            # Add metadata
            response.metadata["processing_time"] = (datetime.now() - start_time).total_seconds()
            response.metadata["model_used"] = self.model.__class__.__name__ if self.model else "None"
            
            logger.info(f"Agent {self.name} completed processing", extra={
                "agent": self.name,
                "confidence": response.confidence,
                "processing_time": response.metadata["processing_time"]
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Agent {self.name} failed", extra={
                "agent": self.name,
                "error": str(e),
                "error_type": type(e).__name__
            })
            
            return AgentResponse(
                agent_name=self.name,
                action="error",
                output=None,
                confidence=0.0,
                reasoning=f"Agent failed with error: {str(e)}",
                metadata={"error": str(e), "error_type": type(e).__name__}
            )
    
    def _create_messages(self, user_prompt: str, context: Dict[str, Any] = None) -> List[BaseMessage]:
        """Create messages for the LLM."""
        messages = [SystemMessage(content=self._system_prompt)]
        
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            messages.append(HumanMessage(content=f"Context:\n{context_str}\n\nTask: {user_prompt}"))
        else:
            messages.append(HumanMessage(content=user_prompt))
        
        return messages
    
    async def _call_llm(self, messages: List[BaseMessage]) -> str:
        """Call the LLM with the given messages."""
        if not self.model:
            raise ValueError(f"No model configured for agent {self.name}")
        
        try:
            response = await self.model.ainvoke(
                messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.content
        except Exception as e:
            logger.error(f"LLM call failed for agent {self.name}", extra={
                "error": str(e),
                "agent": self.name
            })
            raise
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON from LLM response."""
        import json
        import re
        
        # Try to find JSON in code blocks
        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to parse the entire response as JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON object in the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        return {}
    
    def _calculate_confidence(self, response: str, expected_keys: List[str] = None) -> float:
        """Calculate confidence score for the response."""
        base_confidence = 0.5
        
        # Check response length
        if len(response) > 100:
            base_confidence += 0.2
        
        # Check for expected keys in JSON response
        if expected_keys:
            try:
                data = self._extract_json_from_response(response)
                found_keys = sum(1 for key in expected_keys if key in data)
                base_confidence += (found_keys / len(expected_keys)) * 0.3
            except:
                pass
        
        return min(1.0, base_confidence)