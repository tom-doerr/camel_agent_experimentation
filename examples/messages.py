"""Core message class for agent communication"""

from dataclasses import dataclass

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
