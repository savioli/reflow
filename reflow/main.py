import os
import re
import sys
import tempfile
from pathlib import Path
from reflow.cli import CLIParser, ConfigFactory
from reflow.generators import BranchNameGenerator, CheckpointGenerator, MessageGenerator
from reflow.git_client import GitClient
from reflow.loaders import GitConfigLoader, ReflowFileLoader
from reflow.prompts import PromptBuilder
from reflow.providers.factory import ProviderFactory
from reflow.reworder import Reworder


def _extract_branch_prefix(branch_name: str) -> str:
    m = re.match(r"^([a-z][a-z0-9-]*)\/", branch_name)
    return m.group(1) if m else ""


def main() -> None:
    invoked_as = os.path.basename(sys.argv[0])
    if invoked_as == "rw":
        sys.argv.insert(1, "reword")
    elif invoked_as == "ck":
        sys.argv.insert(1, "checkpoint")
    # rf and reflow are pass-through aliases

    args = CLIParser().parse()
    git = GitClient()
    git.assert_in_repo()

    config = ConfigFactory(GitConfigLoader(), ReflowFileLoader()).from_args(args)

    if config.checkpoint:
        if config.checkpoint_auto_stage:
            git.stage_all()
        if not git.has_staged_changes():
            print("Error: nothing to commit.", file=sys.stderr)
            sys.exit(1)
        msg = CheckpointGenerator().next_message()
        print(f"Committing as: {msg}")
        git.commit(msg)
        return

    if config.squash:
        since = git.resolve_since(config.since)
        checkpoint_hashes = git.get_checkpoint_hashes(since)
        if not checkpoint_hashes:
            print("No checkpoint commits found on this branch.")
            sys.exit(0)
        print(f"Squashing {len(checkpoint_hashes)} checkpoint commit(s)...")
        provider = ProviderFactory().create(config)
        combined_diff = git.get_combined_diff(checkpoint_hashes, config.context_lines)
        msg = MessageGenerator(provider, PromptBuilder(), config).generate("squash", combined_diff)
        if not msg:
            print("Error: could not generate commit message.", file=sys.stderr)
            sys.exit(1)
        print(f"  Message: {msg}")
        if not config.auto_accept:
            confirm = input("Squash checkpoints? [Y/n] ").strip().lower()
            if confirm == "n":
                print("Aborted.")
                return
        squash_hashes = set(h[:7] for h in checkpoint_hashes)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            messages_file = Path(f.name)
        try:
            git.rebase(since, [msg], messages_file, squash_hashes=squash_hashes)
            print(f"Done. {len(checkpoint_hashes)} checkpoint(s) squashed into: {msg}")
        finally:
            messages_file.unlink(missing_ok=True)
        return

    if config.amend:
        current_msg = git.get_original_message("HEAD")
        diff = git.get_diff("HEAD", config.context_lines)
        provider = ProviderFactory().create(config)
        new_msg = MessageGenerator(provider, PromptBuilder(), config).generate("HEAD", diff)
        if not new_msg:
            print("Error: could not generate commit message.", file=sys.stderr)
            sys.exit(1)
        print(f"  Current:  {current_msg}")
        print(f"  Proposed: {new_msg}")
        if config.auto_accept:
            git.amend(new_msg)
            print(f"Amended: {new_msg}")
        else:
            confirm = input("Amend? [Y/n] ").strip().lower()
            if confirm != "n":
                git.amend(new_msg)
                print(f"Amended: {new_msg}")
        return

    if config.branch:
        current = git.get_current_branch()
        if current == "HEAD":
            print("Error: detached HEAD state.", file=sys.stderr)
            sys.exit(1)
        since = git.resolve_since(config.since)
        provider = ProviderFactory().create(config)
        bare_name = BranchNameGenerator(git, provider, PromptBuilder(), config).generate(since)
        if not bare_name:
            print("Error: could not generate branch name.", file=sys.stderr)
            sys.exit(1)
        prefix = config.branch_prefix or _extract_branch_prefix(current)
        full_name = f"{prefix}/{bare_name}" if prefix else bare_name
        print(f"  Current:   {current}")
        print(f"  Generated: {full_name}")
        if config.auto_accept:
            git.rename_branch(full_name)
            print(f"Branch renamed to: {full_name}")
        else:
            confirm = input("Rename branch? [Y/n] ").strip().lower()
            if confirm != "n":
                git.rename_branch(full_name)
                print(f"Branch renamed to: {full_name}")
        return

    provider = ProviderFactory().create(config)
    generator = MessageGenerator(provider, PromptBuilder(), config)
    Reworder(git, config, generator).run()
