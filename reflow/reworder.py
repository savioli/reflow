import tempfile
from pathlib import Path
from typing import Optional

from reflow.config import Config
from reflow.generators import MessageGenerator
from reflow.git_client import GitClient


class Reworder:
    def __init__(
        self,
        git: GitClient,
        config: Config,
        generator: Optional[MessageGenerator] = None,
    ):
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
            print(f"Rewording {len(hashes)} checkpoint commit(s)...")
        else:
            hashes = self._git.get_hashes(since)
            if not hashes:
                print("No commits to reword.")
                return
            print(f"Rewording {len(hashes)} commit(s)...")

        if self._generator is not None:
            messages = self._auto_mode(hashes)
        else:
            messages = self._interactive_mode(hashes)

        hashes_to_reword = set(h[:7] for h in hashes) if self._config.checkpoint_reword else None
        self._confirm_and_apply(since, hashes, messages, hashes_to_reword=hashes_to_reword)

    def _auto_mode(self, hashes: list[str]) -> list[str]:
        messages = []
        count = len(hashes)
        for i, commit_hash in enumerate(hashes, 1):
            print(f"  [{i}/{count}] {commit_hash[:7]}")
            diff = self._git.get_diff(commit_hash, self._config.context_lines)
            msg = self._generator.generate(commit_hash, diff) or self._git.get_original_message(commit_hash)
            messages.append(msg)
        return messages

    def _interactive_mode(self, hashes: list[str]) -> list[str]:
        messages = []
        for commit_hash in hashes:
            print("\n──────────────────────────────────────────")
            print(f"Commit: {commit_hash[:7]}")
            print(f"Current: {self._git.get_original_message(commit_hash)}")
            print()
            print(self._git.get_stat(commit_hash))
            msg = input("New message (≤5 words, blank = keep): ").strip()
            messages.append(msg or self._git.get_original_message(commit_hash))
        return messages

    def _confirm_and_apply(self, since: str, hashes: list[str], messages: list[str],
                           hashes_to_reword: Optional[set[str]] = None) -> None:
        print("\nGenerated messages:")
        print("───────────────────")
        for commit_hash, msg in zip(hashes, messages):
            print(f"  {commit_hash[:7]}  {msg}")
        print()

        confirm = input("Apply these messages? [Y/n] ").strip().lower()
        if confirm == "n":
            print("Aborted.")
            return

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            messages_file = Path(f.name)
        try:
            self._git.rebase(since, messages, messages_file, hashes_to_reword=hashes_to_reword)
            print(f"\nDone. {len(messages)} commit(s) reworded.")
        finally:
            messages_file.unlink(missing_ok=True)
