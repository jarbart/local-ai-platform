from dataclasses import dataclass, field
from typing import Any


@dataclass
class NormalizedDocument:
    document_id: str
    filename: str
    content_type: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)