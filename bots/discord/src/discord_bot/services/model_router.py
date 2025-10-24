"""Model router service for requesty.ai integration."""

import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone
from enum import Enum
import httpx
import json

from discord_bot.core.config import settings
from discord_bot.core.logging import get_logger

logger = get_logger(__name__)


class ModelCapability(Enum):
    """Model capabilities for task routing."""
    RESEARCH = "research"
    CONTENT_WRITING = "content_writing"
    TECHNICAL_ANALYSIS = "technical_analysis"
    EDITING = "editing"
    FORMATTING = "formatting"


class ModelProvider(Enum):
    """Supported model providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    COHERE = "cohere"
    MISTRAL = "mistral"


class ModelInfo:
    """Information about a model."""
    
    def __init__(
        self,
        id: str,
        name: str,
        provider: ModelProvider,
        capabilities: List[ModelCapability],
        input_cost_per_token: float = 0.0,
        output_cost_per_token: float = 0.0,
        max_tokens: int = 4096,
        context_window: int = 4096,
        is_available: bool = True
    ):
        self.id = id
        self.name = name
        self.provider = provider
        self.capabilities = capabilities
        self.input_cost_per_token = input_cost_per_token
        self.output_cost_per_token = output_cost_per_token
        self.max_tokens = max_tokens
        self.context_window = context_window
        self.is_available = is_available


class ModelRouter:
    """Service for routing tasks to appropriate models via requesty.ai."""
    
    def __init__(self):
        self.base_url = settings.requesty_base_url
        self.api_key = settings.requesty_api_key
        self.client: Optional[httpx.AsyncClient] = None
        self.available_models: Dict[str, ModelInfo] = {}
        self.user_preferences: Dict[str, str] = {}
        self._model_cache_expires = None
        self._usage_tracking: Dict[str, Dict] = {}
    
    async def initialize(self):
        """Initialize the model router service."""
        if not self.api_key:
            logger.warning("Requesty.ai API key not configured, using fallback models")
            self._initialize_fallback_models()
            return
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        
        await self._load_available_models()
        self._load_user_preferences()
        
        logger.info("Model router service initialized", extra={
            "available_models": len(self.available_models),
            "base_url": self.base_url
        })
    
    async def close(self):
        """Close the model router service."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("Model router service closed")
    
    async def get_model_for_capability(
        self,
        capability: ModelCapability,
        user_preference: Optional[str] = None
    ) -> Optional[ModelInfo]:
        """Get the best model for a specific capability."""
        # Check user preference first
        if user_preference and user_preference in self.available_models:
            model = self.available_models[user_preference]
            if capability in model.capabilities and model.is_available:
                return model
        
        # Check global user preferences
        pref_key = f"{capability.value}_model"
        if pref_key in self.user_preferences:
            preferred_model_id = self.user_preferences[pref_key]
            if preferred_model_id in self.available_models:
                model = self.available_models[preferred_model_id]
                if capability in model.capabilities and model.is_available:
                    return model
        
        # Find best available model for capability
        suitable_models = [
            model for model in self.available_models.values()
            if capability in model.capabilities and model.is_available
        ]
        
        if not suitable_models:
            logger.warning(f"No available models for capability: {capability}")
            return None
        
        # Sort by preference: Anthropic first, then by cost-effectiveness
        def model_score(model: ModelInfo) -> tuple:
            # Prefer Anthropic models
            provider_score = 0 if model.provider == ModelProvider.ANTHROPIC else 1
            
            # Prefer lower cost (higher score for lower cost)
            cost_score = 1.0 / (model.input_cost_per_token + 1e-6)
            
            # Prefer larger context window for complex tasks
            context_score = model.context_window / 100000  # Normalize
            
            return (provider_score, -cost_score, -context_score)
        
        best_model = min(suitable_models, key=model_score)
        
        logger.debug(f"Selected model {best_model.id} for {capability}", extra={
            "model_id": best_model.id,
            "provider": best_model.provider.value,
            "capability": capability.value
        })
        
        return best_model
    
    async def invoke_model(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Invoke a specific model via requesty.ai."""
        if not self.client or not self.api_key:
            return self._fallback_model_response(messages, model_id)
        
        try:
            # Prepare request payload
            payload = {
                "model": model_id,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }
            
            # Make API request
            response = await self.client.post("/chat/completions", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                # Track usage
                self._track_usage(model_id, payload, result)
                
                return result
            else:
                logger.error(f"Model invocation failed: {response.status_code} - {response.text}")
                return self._fallback_model_response(messages, model_id)
                
        except Exception as e:
            logger.error(f"Error invoking model {model_id}: {e}")
            return self._fallback_model_response(messages, model_id)
    
    async def invoke_model_by_capability(
        self,
        capability: ModelCapability,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        user_preference: Optional[str] = None,
        **kwargs
    ) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Invoke the best model for a capability."""
        model = await self.get_model_for_capability(capability, user_preference)
        
        if not model:
            return None, None
        
        response = await self.invoke_model(
            model.id,
            messages,
            temperature,
            max_tokens,
            **kwargs
        )
        
        return response, model.id
    
    async def _load_available_models(self):
        """Load available models from requesty.ai."""
        try:
            response = await self.client.get("/models")
            
            if response.status_code == 200:
                models_data = response.json()
                self._parse_models_response(models_data)
                self._model_cache_expires = datetime.now(timezone.utc).timestamp() + 3600  # Cache for 1 hour
            else:
                logger.error(f"Failed to load models: {response.status_code}")
                self._initialize_fallback_models()
                
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self._initialize_fallback_models()
    
    def _parse_models_response(self, models_data: Dict[str, Any]):
        """Parse models response from requesty.ai."""
        self.available_models = {}
        
        if "data" not in models_data:
            logger.warning("Invalid models response format")
            self._initialize_fallback_models()
            return
        
        for model_data in models_data["data"]:
            model_id = model_data.get("id", "")
            model_name = model_data.get("name", model_id)
            
            # Determine provider from model ID
            provider = self._determine_provider(model_id)
            
            # Determine capabilities based on model characteristics
            capabilities = self._determine_capabilities(model_id, model_data)
            
            # Extract cost information
            input_cost = model_data.get("pricing", {}).get("input", 0.0)
            output_cost = model_data.get("pricing", {}).get("output", 0.0)
            
            # Extract context window
            context_window = model_data.get("context_length", 4096)
            max_tokens = min(context_window // 2, model_data.get("max_tokens", 4096))
            
            model_info = ModelInfo(
                id=model_id,
                name=model_name,
                provider=provider,
                capabilities=capabilities,
                input_cost_per_token=input_cost,
                output_cost_per_token=output_cost,
                max_tokens=max_tokens,
                context_window=context_window,
                is_available=model_data.get("available", True)
            )
            
            self.available_models[model_id] = model_info
        
        logger.info(f"Loaded {len(self.available_models)} models from requesty.ai")
    
    def _determine_provider(self, model_id: str) -> ModelProvider:
        """Determine provider from model ID."""
        model_id_lower = model_id.lower()
        
        if "claude" in model_id_lower or "anthropic" in model_id_lower:
            return ModelProvider.ANTHROPIC
        elif "gpt" in model_id_lower or "openai" in model_id_lower:
            return ModelProvider.OPENAI
        elif "cohere" in model_id_lower:
            return ModelProvider.COHERE
        elif "mistral" in model_id_lower:
            return ModelProvider.MISTRAL
        else:
            return ModelProvider.OPENAI  # Default fallback
    
    def _determine_capabilities(self, model_id: str, model_data: Dict) -> List[ModelCapability]:
        """Determine model capabilities based on model characteristics."""
        capabilities = []
        model_id_lower = model_id.lower()
        
        # All models can do basic content writing
        capabilities.append(ModelCapability.CONTENT_WRITING)
        
        # Claude models are excellent for technical analysis and editing
        if "claude" in model_id_lower:
            capabilities.extend([
                ModelCapability.TECHNICAL_ANALYSIS,
                ModelCapability.EDITING,
                ModelCapability.RESEARCH
            ])
            
            # Larger Claude models are better for formatting
            if "sonnet" in model_id_lower or "opus" in model_id_lower:
                capabilities.append(ModelCapability.FORMATTING)
        
        # GPT models are versatile
        elif "gpt" in model_id_lower:
            capabilities.extend([
                ModelCapability.RESEARCH,
                ModelCapability.TECHNICAL_ANALYSIS,
                ModelCapability.EDITING
            ])
            
            # GPT-4 and newer for formatting
            if "gpt-4" in model_id_lower:
                capabilities.append(ModelCapability.FORMATTING)
        
        # Other models get basic capabilities
        else:
            capabilities.extend([
                ModelCapability.RESEARCH,
                ModelCapability.TECHNICAL_ANALYSIS
            ])
        
        return capabilities
    
    def _initialize_fallback_models(self):
        """Initialize fallback models when API is not available."""
        self.available_models = {
            "claude-3-sonnet-20240229": ModelInfo(
                id="claude-3-sonnet-20240229",
                name="Claude 3 Sonnet",
                provider=ModelProvider.ANTHROPIC,
                capabilities=[
                    ModelCapability.RESEARCH,
                    ModelCapability.CONTENT_WRITING,
                    ModelCapability.TECHNICAL_ANALYSIS,
                    ModelCapability.EDITING,
                    ModelCapability.FORMATTING
                ],
                input_cost_per_token=0.000003,
                output_cost_per_token=0.000015,
                max_tokens=4096,
                context_window=200000,
                is_available=False  # Not actually available without API
            ),
            "claude-3-haiku-20240307": ModelInfo(
                id="claude-3-haiku-20240307",
                name="Claude 3 Haiku",
                provider=ModelProvider.ANTHROPIC,
                capabilities=[
                    ModelCapability.EDITING,
                    ModelCapability.FORMATTING,
                    ModelCapability.CONTENT_WRITING
                ],
                input_cost_per_token=0.00000025,
                output_cost_per_token=0.00000125,
                max_tokens=4096,
                context_window=200000,
                is_available=False
            ),
            "gpt-4-turbo": ModelInfo(
                id="gpt-4-turbo",
                name="GPT-4 Turbo",
                provider=ModelProvider.OPENAI,
                capabilities=[
                    ModelCapability.RESEARCH,
                    ModelCapability.CONTENT_WRITING,
                    ModelCapability.TECHNICAL_ANALYSIS,
                    ModelCapability.FORMATTING
                ],
                input_cost_per_token=0.00001,
                output_cost_per_token=0.00003,
                max_tokens=4096,
                context_window=128000,
                is_available=False
            )
        }
        
        logger.info("Initialized fallback models")
    
    def _load_user_preferences(self):
        """Load user model preferences."""
        # For now, use defaults from settings
        self.user_preferences = {
            "research_model": settings.default_research_model,
            "content_writing_model": settings.default_writing_model,
            "editing_model": settings.default_editing_model,
            "technical_analysis_model": settings.default_writing_model,
            "formatting_model": settings.default_editing_model
        }
        
        logger.debug("Loaded user preferences", extra={
            "preferences": self.user_preferences
        })
    
    def _fallback_model_response(
        self, 
        messages: List[Dict[str, str]], 
        model_id: str
    ) -> Dict[str, Any]:
        """Generate fallback response when model API is not available."""
        user_message = messages[-1].get("content", "") if messages else ""
        
        # Simple template-based response
        fallback_response = f"This response would be generated by {model_id}, but the model API is not available. "
        
        if "research" in user_message.lower():
            fallback_response += "Please check official documentation for the latest information."
        elif "analyze" in user_message.lower():
            fallback_response += "Manual analysis would be needed without model access."
        else:
            fallback_response += "Please configure model API access for full functionality."
        
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": fallback_response
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": len(fallback_response.split()),
                "total_tokens": len(user_message.split()) + len(fallback_response.split())
            },
            "model": model_id,
            "fallback": True
        }
    
    def _track_usage(
        self,
        model_id: str,
        request_payload: Dict,
        response: Dict
    ):
        """Track model usage for cost monitoring."""
        usage = response.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        
        if model_id not in self._usage_tracking:
            self._usage_tracking[model_id] = {
                "requests": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_cost": 0.0
            }
        
        tracking = self._usage_tracking[model_id]
        tracking["requests"] += 1
        tracking["prompt_tokens"] += prompt_tokens
        tracking["completion_tokens"] += completion_tokens
        
        # Calculate cost if model info is available
        if model_id in self.available_models:
            model_info = self.available_models[model_id]
            cost = (
                prompt_tokens * model_info.input_cost_per_token +
                completion_tokens * model_info.output_cost_per_token
            )
            tracking["total_cost"] += cost
        
        logger.debug(f"Usage tracked for {model_id}", extra={
            "model_id": model_id,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens
        })
    
    def set_user_preference(self, capability: ModelCapability, model_id: str):
        """Set user preference for a specific capability."""
        pref_key = f"{capability.value}_model"
        self.user_preferences[pref_key] = model_id
        
        logger.info(f"Set user preference: {capability.value} -> {model_id}")
    
    def get_available_models(self) -> Dict[str, ModelInfo]:
        """Get all available models."""
        return self.available_models.copy()
    
    def get_usage_stats(self) -> Dict[str, Dict]:
        """Get usage statistics."""
        return self._usage_tracking.copy()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of model router service."""
        health = {
            "service": "model_router",
            "status": "unknown",
            "api_key_configured": bool(self.api_key),
            "client_initialized": bool(self.client),
            "available_models": len(self.available_models),
            "models_loaded": list(self.available_models.keys())[:5]  # Show first 5
        }
        
        if not self.api_key:
            health["status"] = "disabled"
            health["note"] = "Using fallback models"
            return health
        
        if not self.client:
            try:
                await self.initialize()
            except Exception as e:
                health["status"] = "error"
                health["error"] = str(e)
                return health
        
        # Test with a simple model list request
        try:
            response = await self.client.get("/models")
            if response.status_code == 200:
                health["status"] = "healthy"
            else:
                health["status"] = "degraded"
                health["error"] = f"API returned {response.status_code}"
                
        except Exception as e:
            health["status"] = "error"
            health["error"] = str(e)
        
        return health


# Global model router instance
model_router = ModelRouter()