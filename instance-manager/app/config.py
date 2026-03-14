"""Instance Manager configuration."""

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    claude_bin: str = field(default_factory=lambda: os.getenv("CLAUDE_BIN", "claude"))
    claude_model: str = field(default_factory=lambda: os.getenv("CLAUDE_MODEL", ""))
    claude_effort: str = field(default_factory=lambda: os.getenv("CLAUDE_EFFORT", ""))
    claude_timeout_seconds: int = field(
        default_factory=lambda: max(10, int(os.getenv("CLAUDE_TIMEOUT_SECONDS", "300")))
    )
    instance_base_dir: Path = field(
        default_factory=lambda: Path(os.getenv("INSTANCE_BASE_DIR", "/opt/teamo/instances"))
    )
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8900")))
    max_restart_attempts: int = 3


CONFIG = Config()
