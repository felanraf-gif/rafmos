from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum


class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    QUERY = "query"
    ANSWER = "answer"
    FEEDBACK = "feedback"


class Priority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Message:
    msg_id: str
    msg_type: MessageType
    sender: str
    receiver: Optional[str]
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
    priority: Priority = Priority.NORMAL
    correlation_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "msg_id": self.msg_id,
            "type": self.msg_type.value,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        data = data.copy()
        data["msg_type"] = MessageType(data.get("type", "request"))
        data["priority"] = Priority(data.get("priority", 2))
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


def create_message(
    msg_type: MessageType,
    sender: str,
    content: Any,
    receiver: str = None,
    priority: Priority = Priority.NORMAL,
    correlation_id: str = None,
    metadata: Dict = None,
) -> Message:
    import uuid
    return Message(
        msg_id=str(uuid.uuid4()),
        msg_type=msg_type,
        sender=sender,
        receiver=receiver,
        content=content,
        priority=priority,
        correlation_id=correlation_id,
        metadata=metadata or {},
    )
