import json
import sys

from reflow.prompts import BRANCH_SCHEMA, COMMIT_SCHEMA
from reflow.providers.base import AIProvider


class OllamaProvider(AIProvider):
    _GENERATE_SYSTEM = (
        "You are a git commit message generator. "
        "Output only a short imperative commit message (≤5 words). "
        "No explanation, no chat, no preamble, no JSON wrapper."
    )
    _BRANCH_SYSTEM = (
        "You are a git branch name generator. "
        "Output only a short kebab-case branch name (2-5 words). "
        "No explanation, no chat, no preamble, no JSON wrapper."
    )

    def __init__(self, url: str, model: str, api_key: str = ""):
        try:
            import ollama as _ollama
        except ImportError:
            print(
                "Error: ollama package is required. Install with: pip install ollama",
                file=sys.stderr,
            )
            sys.exit(1)
        self._ollama = _ollama
        self._model = model
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self._client = _ollama.Client(host=url, timeout=120, headers=headers)

    def check(self) -> None:
        try:
            self._client.list()
        except self._ollama.ResponseError as exc:
            print(f"Error: Ollama responded with an error: {exc}", file=sys.stderr)
            sys.exit(1)
        except self._ollama.RequestError as exc:
            print(
                f"Error: could not connect to Ollama: {exc}\nStart with: ollama serve",
                file=sys.stderr,
            )
            sys.exit(1)
        except Exception as exc:
            print(f"Error: unexpected failure checking Ollama: {exc}", file=sys.stderr)
            sys.exit(1)

    def _chat(self, prompt: str, schema: dict, system: str) -> dict:
        response = self._client.chat(
            model=self._model,
            format=schema,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )
        return json.loads(response.message.content)

    @property
    def generate_system(self) -> str:
        return self._GENERATE_SYSTEM

    @property
    def branch_system(self) -> str:
        return self._BRANCH_SYSTEM

    def generate(self, prompt: str) -> dict:
        return self._chat(prompt, COMMIT_SCHEMA, self._GENERATE_SYSTEM)

    def generate_branch(self, prompt: str) -> dict:
        return self._chat(prompt, BRANCH_SCHEMA, self._BRANCH_SYSTEM)
