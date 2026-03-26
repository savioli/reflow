import sys

from reflow.prompts import COMMIT_SCHEMA, BRANCH_SCHEMA
from reflow.providers.base import AIProvider


class ClaudeProvider(AIProvider):
    _GENERATE_SYSTEM = (
        "You are a git commit message generator. "
        "Output only a short imperative commit message (≤5 words) via the tool. "
        "No explanation, no chat, no preamble."
    )
    _BRANCH_SYSTEM = (
        "You are a git branch name generator. "
        "Output only a short kebab-case branch name (2-5 words) via the tool. "
        "No explanation, no chat, no preamble."
    )

    def __init__(self, api_key: str, model: str):
        if not api_key:
            print("error: GIT_REFLOW_ANTHROPIC_API_KEY is not set", file=sys.stderr)
            sys.exit(1)
        try:
            import anthropic as _anthropic
        except ImportError:
            print("Error: anthropic package is required. Install with: pip install anthropic", file=sys.stderr)
            sys.exit(1)
        self._client = _anthropic.Anthropic(api_key=api_key)
        self._model = model

    def _call(self, prompt: str, schema: dict, tool_name: str, max_tokens: int, system: str) -> dict:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=system,
            tools=[{"name": tool_name, "description": tool_name, "input_schema": schema}],
            tool_choice={"type": "tool", "name": tool_name},
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].input

    @property
    def generate_system(self) -> str:
        return self._GENERATE_SYSTEM

    @property
    def branch_system(self) -> str:
        return self._BRANCH_SYSTEM

    def generate(self, prompt: str) -> dict:
        return self._call(prompt, COMMIT_SCHEMA, "commit", max_tokens=64, system=self._GENERATE_SYSTEM)

    def generate_branch(self, prompt: str) -> dict:
        return self._call(prompt, BRANCH_SCHEMA, "branch", max_tokens=32, system=self._BRANCH_SYSTEM)
