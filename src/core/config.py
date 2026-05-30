import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class Config:
    # Execution mode
    mode: str  # "claude-code" or "api"
    anthropic_api_key: Optional[str] = None

    # GitHub
    github_token: str = ""
    github_repo: str = ""

    # Target project
    project_root: Path = Path(".")

    # Agent settings
    max_retries: int = 3
    timeout_seconds: int = 600

    # Debug
    debug: bool = False
    use_tmux: bool = False

    @classmethod
    def load(cls, config_path: str = "config.yaml"):
        with open(config_path) as f:
            data = yaml.safe_load(f)

        # Handle ${ENV_VAR} substitution
        if data.get("github_token", "").startswith("${"):
            env_var = data["github_token"][2:-1]
            data["github_token"] = os.getenv(env_var, "")

        if data.get("anthropic_api_key") and data["anthropic_api_key"].startswith("${"):
            env_var = data["anthropic_api_key"][2:-1]
            data["anthropic_api_key"] = os.getenv(env_var)

        # Convert project_root to Path
        if "project_root" in data:
            data["project_root"] = Path(data["project_root"])

        return cls(**data)
