"""
Vertex AI model management with cost optimization
"""
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime, date
from langchain_google_vertexai import ChatVertexAI
import structlog

from ..config.settings import settings

logger = structlog.get_logger(__name__)


class VertexAIManager:
    """Manages Vertex AI models with cost optimization."""
    
    def __init__(self):
        self.project_id = settings.google_cloud_project
        self.location = settings.vertex_ai_location
        self.daily_budget = settings.daily_budget_usd
        
        # Daily usage tracking (in-memory for now)
        self.daily_usage = 0.0
        self.usage_date = date.today()
        
        # Model pricing per 1K tokens (as of 2024)
        self.model_costs = {
            "gemini-1.5-flash-001": {"input": 0.000125, "output": 0.000375},
            "gemini-1.5-pro-001": {"input": 0.00125, "output": 0.00375},
            "gemini-2.5-flash": {"input": 0.000125, "output": 0.000375}  # Gemini 2.5 Flash pricing
        }
        
        # Simple logging to avoid structlog issues
        print(f"✅ VertexAI Manager initialized - Project: {self.project_id}, Location: {self.location}, Budget: ${self.daily_budget}")
    
    def get_flash_model(self, **kwargs) -> ChatVertexAI:
        """Get cost-effective Gemini Flash model."""
        default_params = {
            "model_name": "gemini-2.5-flash",
            "project": self.project_id,
            "location": self.location,
            "max_output_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40
        }
        default_params.update(kwargs)
        
        return ChatVertexAI(**default_params)
    
    def get_pro_model(self, **kwargs) -> ChatVertexAI:
        """Get high-capability Gemini Pro model."""
        default_params = {
            "model_name": "gemini-1.5-pro-001",
            "project": self.project_id,
            "location": self.location,
            "max_output_tokens": 2048,
            "temperature": 0.8,
            "top_p": 0.9,
            "top_k": 40
        }
        default_params.update(kwargs)
        
        return ChatVertexAI(**default_params)
    
    def get_llm(self, model_name: str = "gemini-2.0-flash-exp", **kwargs) -> ChatVertexAI:
        """Get LLM instance by model name for CrewAI agents."""
        
        # Map newer model names to available models
        model_mapping = {
            "gemini-2.0-flash-exp": "gemini-2.5-flash",
            "gemini-2.5-flash": "gemini-2.5-flash",
            "gemini-1.5-flash": "gemini-1.5-flash-001",
            "gemini-1.5-pro": "gemini-1.5-pro-001"
        }
        
        mapped_model = model_mapping.get(model_name, "gemini-2.5-flash")
        
        if "flash" in mapped_model:
            return self.get_flash_model(model_name=mapped_model, **kwargs)
        else:
            return self.get_pro_model(model_name=mapped_model, **kwargs)
    
    def should_use_pro_model(self, task_complexity: str = "routine") -> bool:
        """Determine if Pro model should be used based on budget and complexity."""
        # Reset daily usage if new day
        if date.today() != self.usage_date:
            self.daily_usage = 0.0
            self.usage_date = date.today()
        
        # Check budget constraints
        if self.daily_usage > self.daily_budget * settings.cost_alert_threshold:
            logger.warning(
                "approaching_daily_budget_limit",
                current_usage=self.daily_usage,
                budget=self.daily_budget,
                threshold=settings.cost_alert_threshold
            )
            return False
        
        # Define complex tasks that benefit from Pro model
        complex_tasks = {
            "creative_writing",
            "complex_analysis", 
            "multi_step_reasoning",
            "comment_generation",
            "quality_review"
        }
        
        return task_complexity in complex_tasks
    
    def estimate_cost(
        self, 
        model_name: str, 
        input_tokens: int, 
        output_tokens: int
    ) -> float:
        """Estimate cost for a model operation."""
        if model_name not in self.model_costs:
            logger.warning("unknown_model_for_cost_estimation", model=model_name)
            return 0.0
        
        costs = self.model_costs[model_name]
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        
        total_cost = input_cost + output_cost
        
        logger.debug(
            "cost_estimated",
            model=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost
        )
        
        return total_cost
    
    def track_usage(
        self, 
        model_name: str, 
        input_tokens: int, 
        output_tokens: int,
        operation_type: str = "generation"
    ) -> float:
        """Track API usage and return cost."""
        cost = self.estimate_cost(model_name, input_tokens, output_tokens)
        
        # Reset daily usage if new day
        if date.today() != self.usage_date:
            self.daily_usage = 0.0
            self.usage_date = date.today()
        
        self.daily_usage += cost
        
        # Simple logging to avoid structlog issues
        print(f"✅ Usage tracked: {model_name} - {operation_type} - tokens: {input_tokens}+{output_tokens} - cost: ${cost:.6f}")
        
        # Alert if approaching budget
        if self.daily_usage > self.daily_budget * settings.cost_alert_threshold:
            logger.warning(
                "daily_budget_alert",
                current_usage=self.daily_usage,
                budget=self.daily_budget,
                percentage=(self.daily_usage / self.daily_budget) * 100
            )
        
        return cost
    
    def check_daily_budget(self) -> bool:
        """Check if we're within daily budget limits."""
        # Reset daily usage if new day
        if date.today() != self.usage_date:
            self.daily_usage = 0.0
            self.usage_date = date.today()
        
        return self.daily_usage < self.daily_budget
    
    def get_usage_report(self) -> Dict[str, Any]:
        """Generate usage report."""
        # Reset daily usage if new day
        if date.today() != self.usage_date:
            self.daily_usage = 0.0
            self.usage_date = date.today()
        
        return {
            "date": self.usage_date.isoformat(),
            "daily_budget": self.daily_budget,
            "current_usage": self.daily_usage,
            "remaining_budget": max(0, self.daily_budget - self.daily_usage),
            "usage_percentage": (self.daily_usage / self.daily_budget) * 100,
            "budget_exceeded": self.daily_usage > self.daily_budget,
            "alert_threshold_reached": self.daily_usage > (self.daily_budget * settings.cost_alert_threshold),
            "available_models": list(self.model_costs.keys())
        }
    
    def get_session_cost(self) -> float:
        """Get current session cost."""
        return self.daily_usage
    
    async def generate_text(
        self, 
        prompt: str, 
        model_name: str = "gemini-2.5-flash",
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        """Generate text using Vertex AI with cost tracking."""
        try:
            # Get the appropriate LLM instance with higher output token limit
            actual_max_tokens = max(1024, max_tokens * 2)  # Ensure adequate token allocation
            llm = self.get_llm(model_name, 
                             max_output_tokens=actual_max_tokens,
                             temperature=temperature)
            
            # Generate response
            response = llm.invoke(prompt)
            
            # Extract text content from response
            result = ""
            if hasattr(response, 'content'):
                result = response.content
            elif hasattr(response, 'text'):
                result = response.text
            else:
                result = str(response)
            
            # Ensure we got actual content
            if not result or len(result.strip()) == 0:
                # Check response metadata for more details
                if hasattr(response, 'response_metadata'):
                    metadata = response.response_metadata
                    finish_reason = metadata.get('finish_reason', 'unknown')
                    print(f"WARNING: Empty response. Finish reason: {finish_reason}")
                    if finish_reason == 'MAX_TOKENS':
                        print(f"Model hit token limit. Consider increasing max_output_tokens.")
                
                # Return empty result but log the issue
                print(f"WARNING: Generated empty content from model {model_name}")
            
            # Estimate token usage for cost tracking
            # Use actual token counts if available
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                input_tokens = usage.get('input_tokens', len(prompt) // 4)
                output_tokens = usage.get('output_tokens', len(result) // 4)
            else:
                # Fallback to estimation
                input_tokens = len(prompt) // 4
                output_tokens = len(result) // 4
            
            # Track usage and cost
            self.track_usage(model_name, input_tokens, output_tokens, "text_generation")
            
            return result
            
        except Exception as e:
            logger.error("text_generation_failed", error=str(e))
            raise


# Global instance
vertex_ai_manager = VertexAIManager()
