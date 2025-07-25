"""
Structured logging configuration
"""
import os
import sys
from pathlib import Path
from typing import Any, Dict
import structlog
from rich.logging import RichHandler
from rich.console import Console

from ..config.settings import settings


def setup_logging() -> None:
    """Configure structured logging with Rich output."""
    
    # Create logs directory
    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="ISO"),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            min_level=30 if settings.log_level.upper() == "WARNING" else 20 if settings.log_level.upper() == "INFO" else 10
        ),
        logger_factory=structlog.WriteLoggerFactory(
            file=open(log_dir / "application.log", "a", encoding="utf-8")
        ),
        cache_logger_on_first_use=False,
    )
    
    # Set up rich handler for console output
    console = Console()
    rich_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        tracebacks_show_locals=settings.is_development
    )
    
    # Configure Python's logging for libraries
    import logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[rich_handler]
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


# Global logger for this module
logger = get_logger(__name__)
