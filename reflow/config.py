from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    since: str = "--root"
    checkpoint: bool = False
    checkpoint_reword: bool = False
    branch: bool = False
    verbosity: int = 0
    use_claude: bool = False
    claude_model: str = "claude-haiku-4-5-20251001"
    use_ollama: bool = False
    ollama_model: str = "llama3.2"
    ollama_url: str = "http://localhost:11434"
    use_openai: bool = False
    openai_model: str = "gpt-4o-mini"
    openai_url: Optional[str] = None
    openai_api_key: str = ""
    context_lines: int = 3
    branch_context_lines: int = 3
    branch_prefix: str = ""
    auto_accept: bool = True
    checkpoint_auto_stage: bool = True
    squash: bool = False
    amend: bool = False
    prompt_template: Optional[str] = None
    branch_prompt_template: Optional[str] = None
    anthropic_api_key: str = ""
