import re
import subprocess
import sys
from typing import Optional

from reflow.config import Config
from reflow.git_client import GitClient
from reflow.prompts import PromptBuilder
from reflow.providers.base import AIProvider


class MessageGenerator:
    def __init__(self, provider: AIProvider, prompt_builder: PromptBuilder, config: Config):
        self._provider = provider
        self._prompt_builder = prompt_builder
        self._config = config

    def generate(self, commit_hash: str, diff: str) -> Optional[str]:
        prompt = self._prompt_builder.build(diff, self._config.prompt_template)
        if self._config.verbosity >= 2:
            print(f"  [prompt:system] {commit_hash[:7]}: {self._provider.generate_system}", file=sys.stderr)
            print(f"  [prompt:user] {commit_hash[:7]}:\n{prompt}", file=sys.stderr)
        try:
            result = self._provider.generate(prompt)
            raw = result.get("message", "").strip()
            lines = [l.strip() for l in raw.splitlines() if l.strip()]
            msg = lines[0].strip("`'\"") if lines else ""
            if self._config.verbosity >= 1:
                print(f"  [debug] {commit_hash[:7]}: {msg}", file=sys.stderr)
            return msg or None
        except Exception as exc:
            if self._config.verbosity >= 1:
                print(f"  [debug] {commit_hash[:7]}: error — {exc}", file=sys.stderr)
            return None


class CheckpointGenerator:
    _PATTERN = re.compile(r"^Checkpoint #(\d+)$", re.IGNORECASE)

    def next_message(self) -> str:
        result = subprocess.run(
            ["git", "log", "--format=%s"],
            capture_output=True, text=True, check=True,
        )
        max_n = 0
        for line in result.stdout.splitlines():
            m = self._PATTERN.match(line.strip())
            if m:
                max_n = max(max_n, int(m.group(1)))
        return f"Checkpoint #{max_n + 1}"


class BranchNameGenerator:
    def __init__(self, git: GitClient, provider: AIProvider, prompt_builder: PromptBuilder, config: Config):
        self._git = git
        self._provider = provider
        self._prompt_builder = prompt_builder
        self._config = config

    def generate(self, since: str) -> Optional[str]:
        diff = self._git.get_range_diff(since, self._config.branch_context_lines)
        prompt = self._prompt_builder.build_branch(diff, self._config.branch_prompt_template)
        if self._config.verbosity >= 2:
            print(f"  [branch-prompt:system]: {self._provider.branch_system}", file=sys.stderr)
            print(f"  [branch-prompt:user]:\n{prompt}", file=sys.stderr)
        try:
            result = self._provider.generate_branch(prompt)
            name = result.get("name", "").strip().lower()
            name = re.sub(r"[^a-z0-9]+", "-", name).strip("-")
            if self._config.verbosity >= 1:
                print(f"  [branch] generated: {name}", file=sys.stderr)
            return name or None
        except Exception as exc:
            if self._config.verbosity >= 1:
                print(f"  [branch] error — {exc}", file=sys.stderr)
            return None
