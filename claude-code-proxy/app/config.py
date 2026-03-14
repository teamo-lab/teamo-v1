"""Claude Code Proxy configuration."""

import os
from dataclasses import dataclass, field


@dataclass
class ProxyConfig:
    instance_manager_url: str = field(
        default_factory=lambda: os.getenv(
            "INSTANCE_MANAGER_URL", "http://127.0.0.1:8900"
        )
    )
    mongodb_uri: str = field(
        default_factory=lambda: os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    )
    mongodb_db: str = field(
        default_factory=lambda: os.getenv("MONGODB_DB", "wowchat")
    )


CONFIG = ProxyConfig()
