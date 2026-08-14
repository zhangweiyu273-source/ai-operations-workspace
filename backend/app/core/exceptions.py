from dataclasses import dataclass, field
from typing import Any


@dataclass
class AppError(Exception):
    message: str
    status_code: int = 400
    code: str = "BAD_REQUEST"
    details: list[dict[str, Any]] = field(default_factory=list)
