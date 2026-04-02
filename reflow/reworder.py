import tempfile
from pathlib import Path
from typing import Optional

from reflow.config import Config
from reflow.generators import MessageGenerator
from reflow.git_client import GitClient


class Reworder:
    def __init__(self, git: GitClient, config: Config, generator: MessageGenerator):
        self._git = git
        self._config = config
        self._generator = generator

    def run(self) -> None:
        since = self._git.resolve_since(self._config.since)

        if self._config.checkpoint_reword:
            hashes = self._git.get_checkpoint_hashes(since)
            if not hashes:
                print("No checkpoint commits found on this branch.")
                return
            n = len(hashes)
            print(f"Rewording {n} checkpoint {'commit' if n == 1 else 'commits'}...")
        else:
            hashes = self._git.get_hashes(since)
            if not hashes:
                print("No commits to reword.")
                return
            n = len(hashes)
            print(f"Rewording {n} {'commit' if n == 1 else 'commits'}...")

        messages = self._generate(hashes)
        hashes_to_reword = (
            set(h[:7] for h in hashes) if self._config.checkpoint_reword else None
        )
        self._confirm_and_apply(
            since, hashes, messages, hashes_to_reword=hashes_to_reword
        )

    def _generate(self, hashes: list[str]) -> list[str]:
        messages = []
        print()
        for commit_hash in hashes:
            diff = self._git.get_diff(commit_hash, self._config.context_lines)
            msg = self._generator.generate(
                commit_hash, diff
            ) or self._git.get_original_message(commit_hash)
            messages.append(msg)
            print(f"{commit_hash[:7]} reworded to {msg}")
        return messages

    def _confirm_and_apply(
        self,
        since: str,
        hashes: list[str],
        messages: list[str],
        hashes_to_reword: Optional[set[str]] = None,
    ) -> None:
        if not self._config.auto_accept and not self._config.dry_run:
            confirm = input("\nApply these messages? [Y/n] ").strip().lower()
            if confirm == "n":
                print("Aborted.")
                return

        print()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            messages_file = Path(f.name)
        try:
            self._git.rebase(
                since, messages, messages_file, hashes_to_reword=hashes_to_reword
            )
            n = len(messages)
            print(f"\nSuccessfully reworded {n} {'commit' if n == 1 else 'commits'}.")
        finally:
            messages_file.unlink(missing_ok=True)
