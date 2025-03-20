"""Core message class for agent communication"""

from dataclasses import dataclass
from time import perf_counter
from typing import List, Dict, Optional
import statistics


@dataclass
class PerformanceMetrics:
    """Track performance metrics for optimization"""
    avg_response_time: float
    tool_usage_count: int
    trials: int
    phrase_impact: Dict[str, float]


@dataclass
class BaseMessage:
    """Base message type for agent communication"""

    role_name: str
    content: str
    role_type: str = "user"

    @classmethod
    def make_user_message(cls, role_name: str, content: str) -> "BaseMessage":
        """Create a user message"""
        return cls(role_name=role_name, content=content, role_type="user")
