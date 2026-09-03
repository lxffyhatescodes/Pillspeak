from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Medication:
    """Dataclass representing medication data and AI-simplified information."""

    name: str
    summary: str
    is_recalled: bool = False
    recall_reason: str = "No active recall notices found."
    timestamp: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    def to_dict(self) -> dict:
        """Convert object instance to dictionary format for JSON storage."""
        return {
            "name": self.name,
            "summary": self.summary,
            "is_recalled": self.is_recalled,
            "recall_reason": self.recall_reason,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Medication":
        """Reconstruct Medication instance from dictionary object."""
        return cls(
            name=data.get("name", ""),
            summary=data.get("summary", ""),
            is_recalled=data.get("is_recalled", False),
            recall_reason=data.get("recall_reason", ""),
            timestamp=data.get("timestamp", ""),
        )