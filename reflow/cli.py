import argparse
import os
import sys
from typing import Optional

from reflow.config import Config
from reflow.loaders import GitConfigLoader, ReflowFileLoader


class CLIParser:
    def parse(self, argv: Optional[list[str]] = None) -> argparse.Namespace:
        if argv is None:
            argv = sys.argv[1:]

        reword = bool(argv) and argv[0] in ("reword", "rw")
        if reword:
            argv = argv[1:]
            checkpoint_reword = bool(argv) and argv[0] in ("checkpoint", "ck")
            if checkpoint_reword:
                argv = argv[1:]
        else:
            checkpoint_reword = False

        checkpoint = bool(argv) and argv[0] in ("checkpoint", "ck")
        if checkpoint:
            argv = argv[1:]

        parser = argparse.ArgumentParser(
            prog="reflow",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument(
            "since",
            nargs="?",
            default=None,
            help="Commit range base; defaults to branch commits only",
        )
        parser.add_argument("--claude", action="store_true", help="Use Claude")
        parser.add_argument(
            "--claude-model", default=None, metavar="MODEL", help="Claude model name"
        )
        parser.add_argument("--ollama", action="store_true", help="Use Ollama")
        parser.add_argument(
            "--ollama-model", default=None, metavar="MODEL", help="Ollama model name"
        )
        parser.add_argument("--openai", action="store_true", help="Use OpenAI")
        parser.add_argument(
            "--openai-model", default=None, metavar="MODEL", help="OpenAI model name"
        )
        parser.add_argument(
            "--branch",
            "-b",
            action="store_true",
            help="Generate and rename current branch name based on diff",
        )
        parser.add_argument(
            "--amend",
            "-a",
            action="store_true",
            help="AI rewrite last commit message via amend",
        )
        parser.add_argument(
            "--squash",
            "-s",
            action="store_true",
            help="Squash checkpoint commits into one",
        )
        parser.add_argument(
            "--prefix",
            default=None,
            metavar="PREFIX",
            help="Prefix to prepend to generated branch name",
        )
        parser.add_argument(
            "--dry-run",
            "-n",
            action="store_true",
            help="Preview changes without applying any git mutations",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="count",
            default=0,
            help="Verbosity: -v AI output, -vv prompts",
        )
        args = parser.parse_args(argv)
        args.reword = reword
        args.checkpoint = checkpoint
        args.checkpoint_reword = checkpoint_reword
        return args


class ConfigFactory:
    def __init__(self, loader: GitConfigLoader, file_loader: ReflowFileLoader):
        self._loader = loader
        self._file_loader = file_loader

    def from_args(self, args: argparse.Namespace) -> Config:
        git_cfg = self._loader.load()
        file_cfg = self._file_loader.load()
        default_provider = git_cfg.get("provider", "")

        use_ollama = (
            args.ollama or "ollamaModel" in git_cfg or "ollamaUrl" in git_cfg or default_provider == "ollama"
        )
        use_openai = (
            args.openai or "openaiModel" in git_cfg or "openaiUrl" in git_cfg or default_provider == "openai"
        )
        use_claude = (
            args.claude or "claudeModel" in git_cfg or "claudeUrl" in git_cfg or default_provider == "claude"
        )

        # Auto-detect provider from env vars (priority: Claude > OpenAI > Ollama)
        if not (use_ollama or use_openai or use_claude):
            if os.environ.get("REFLOW_ANTHROPIC_API_KEY"):
                use_claude = True
            elif os.environ.get("REFLOW_OPENAI_API_KEY"):
                use_openai = True
            elif os.environ.get("REFLOW_OLLAMA_API_KEY"):
                use_ollama = True

        since_raw = args.since or "--root"
        if since_raw.isdigit():
            since_raw = f"HEAD~{since_raw}"

        return Config(
            since=since_raw,
            checkpoint=args.checkpoint,
            checkpoint_reword=args.checkpoint_reword,
            branch=args.branch,
            verbosity=args.verbose,
            use_claude=use_claude,
            claude_model=args.claude_model
            or git_cfg.get("claudeModel", "claude-haiku-4-5-20251001"),
            claude_url=git_cfg.get("claudeUrl") or None,
            use_ollama=use_ollama,
            ollama_model=args.ollama_model or git_cfg.get("ollamaModel", "llama3.2"),
            ollama_url=git_cfg.get("ollamaUrl")
            or (
                "https://ollama.com"
                if os.environ.get("REFLOW_OLLAMA_API_KEY")
                else "http://localhost:11434"
            ),
            ollama_api_key=os.environ.get("REFLOW_OLLAMA_API_KEY", ""),
            use_openai=use_openai,
            openai_model=args.openai_model or git_cfg.get("openaiModel", "gpt-4o-mini"),
            openai_url=git_cfg.get("openaiUrl") or None,
            openai_api_key=os.environ.get("REFLOW_OPENAI_API_KEY", ""),
            context_lines=int(git_cfg.get("contextLines", 3)),
            branch_context_lines=int(git_cfg.get("branchContextLines", 3)),
            branch_prefix=args.prefix or git_cfg.get("branchPrefix", ""),
            auto_accept=git_cfg.get("autoAccept", "true").lower() != "false",
            checkpoint_auto_stage=git_cfg.get("checkpointAutoStage", "true").lower()
            != "false",
            squash=args.squash,
            amend=args.amend,
            dry_run=args.dry_run,
            prompt_template=file_cfg.get("commitPrompt") or git_cfg.get("commitPrompt"),
            branch_prompt_template=file_cfg.get("branchPrompt")
            or git_cfg.get("branchPrompt"),
            anthropic_api_key=os.environ.get("REFLOW_ANTHROPIC_API_KEY", ""),
        )
