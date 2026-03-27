import json
import sys
from typing import Optional

from reflow.prompts import BRANCH_SCHEMA, COMMIT_SCHEMA
from reflow.providers.base import AIProvider


class OpenAIProvider(AIProvider):
    _GENERATE_SYSTEM = (
        "You are a git commit message generator. "
        "Output only a short imperative commit message (≤5 words). "
        "No explanation, no chat, no preamble."
    )
    _BRANCH_SYSTEM = (
        "You are a git branch name generator. "
        "Output only a short kebab-case branch name (2-5 words). "
        "No explanation, no chat, no preamble."
    )

    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None):
        if not api_key:
            print("error: GIT_REFLOW_OPENAI_API_KEY is not set", file=sys.stderr)
            sys.exit(1)
        try:
            import openai as _openai
        except ImportError:
            print(
                "Error: openai package is required. Install with: pip install openai",
                file=sys.stderr,
            )
            sys.exit(1)
        self._client = _openai.OpenAI(
            api_key=api_key, **({"base_url": base_url} if base_url else {})
        )
        self._model = model

    def _call(self, prompt: str, schema: dict, system: str) -> dict:
        response = self._client.chat.completions.create(
            model=self._model,
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "response", "strict": True, "schema": schema},
            },
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )
        return json.loads(response.choices[0].message.content)

    @property
    def generate_system(self) -> str:
        return self._GENERATE_SYSTEM

    @property
    def branch_system(self) -> str:
        return self._BRANCH_SYSTEM

    def generate(self, prompt: str) -> dict:
        return self._call(prompt, COMMIT_SCHEMA, self._GENERATE_SYSTEM)

    def generate_branch(self, prompt: str) -> dict:
        return self._call(prompt, BRANCH_SCHEMA, self._BRANCH_SYSTEM)
