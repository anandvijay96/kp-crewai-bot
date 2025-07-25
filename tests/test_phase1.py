"""
Phase 1 testing script
"""
import pytest
from src.seo_automation.config.settings import settings
from src.seo_automation.utils.vertex_ai_manager import vertex_ai_manager
from src.seo_automation.utils.logging import get_logger

logger = get_logger(__name__)


def test_settings_loaded():
    """Test that settings are properly loaded."""
    assert settings.google_cloud_project is not None
    assert settings.vertex_ai_location is not None
    assert settings.daily_budget_usd > 0


def test_vertex_ai_manager_initialization():
    """Test Vertex AI manager initialization."""
    assert vertex_ai_manager.project_id is not None
    assert vertex_ai_manager.location is not None
    assert vertex_ai_manager.daily_budget > 0


def test_model_creation():
    """Test that models can be created."""
    flash_model = vertex_ai_manager.get_flash_model()
    pro_model = vertex_ai_manager.get_pro_model()
    
    assert flash_model is not None
    assert pro_model is not None


def test_cost_estimation():
    """Test cost estimation functionality."""
    cost = vertex_ai_manager.estimate_cost("gemini-1.5-flash-001", 100, 50)
    assert cost > 0
    assert isinstance(cost, float)


def test_budget_check():
    """Test budget checking functionality."""
    result = vertex_ai_manager.check_daily_budget()
    assert isinstance(result, bool)


def test_usage_report():
    """Test usage report generation."""
    report = vertex_ai_manager.get_usage_report()
    
    required_keys = [
        "date", "daily_budget", "current_usage", 
        "remaining_budget", "usage_percentage", 
        "budget_exceeded", "alert_threshold_reached"
    ]
    
    for key in required_keys:
        assert key in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
