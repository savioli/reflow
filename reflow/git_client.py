import os
import re
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional


class GitClient:
    def __init__(self, dry_run: bool = False) -> None:
        self._dry_run = dry_run

    def assert_in_repo(self) -> None:
        result = subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True)
        if result.returncode != 0:
            print("Error: not inside a git repository.", file=sys.stderr)
            sys.exit(1)

    def _get_branch_base(self) -> str:
        """Return merge-base commit hash where current branch diverged, or '' if undetermined."""
        up = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
            capture_output=True,
            text=True,
        )
        if up.returncode == 0 and up.stdout.strip():
            base = subprocess.run(
                ["git", "merge-base", "HEAD", up.stdout.strip()],
                capture_output=True,
                text=True,
            )
            if base.returncode == 0:
                merge_base = base.stdout.strip()
                head = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                if merge_base != head.stdout.strip():
                    return merge_base

        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
        current = self.get_current_branch()
        refs = (
            subprocess.run(
                [
                    "git",
                    "for-each-ref",
                    "--format=%(refname:short)",
                    "refs/heads/",
                    "refs/remotes/",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            .stdout.strip()
            .splitlines()
        )

        best_base = ""
        best_count = None
        for ref in refs:
            if ref == current or ref.endswith("/HEAD"):
                continue
            mb = subprocess.run(
                ["git", "merge-base", "HEAD", ref], capture_output=True, text=True
            )
            if mb.returncode != 0:
                continue
            merge_base = mb.stdout.strip()
            if merge_base == head:
                continue
            count_result = subprocess.run(
                ["git", "rev-list", "--count", f"{merge_base}..HEAD"],
                capture_output=True,
                text=True,
            )
            if count_result.returncode != 0:
                continue
            count = int(count_result.stdout.strip())
            if count > 0 and (best_count is None or count < best_count):
                best_base = merge_base
                best_count = count

        return best_base

    def resolve_since(self, since: str) -> str:
        """Resolve '--root' to the branch merge-base, falling back to '--root' if none found."""
        if since != "--root":
            return since
        base = self._get_branch_base()
        return base if base else "--root"

    def get_hashes(self, since: str) -> list[str]:
        cmd = ["git", "log", "--reverse", "--format=%H"]
        if since != "--root":
            cmd.append(f"{since}..HEAD")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return [h for h in result.stdout.strip().splitlines() if h]

    def get_diff(self, commit_hash: str, context_lines: int) -> str:
        result = subprocess.run(
            [
                "git",
                "diff-tree",
                "--no-commit-id",
                "-p",
                f"-U{context_lines}",
                commit_hash,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    def get_current_branch(self) -> str:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()

    def get_range_diff(self, since: str, context_lines: int = 3) -> str:
        ctx = f"-U{context_lines}"
        if since == "--root":
            root = subprocess.run(
                ["git", "rev-list", "--max-parents=0", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            result = subprocess.run(
                ["git", "diff", ctx, f"{root}..HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
        else:
            result = subprocess.run(
                ["git", "diff", ctx, f"{since}..HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
        return result.stdout

    def rename_branch(self, name: str) -> None:
        if self._dry_run:
            print(f"[dry run] would rename branch to: {name}")
            return
        subprocess.run(["git", "branch", "-m", name], check=True)

    def get_stat(self, commit_hash: str) -> str:
        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "-r", "--stat", commit_hash],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    def get_checkpoint_hashes(self, since: str) -> list[str]:
        pattern = re.compile(r"^Checkpoint #\d+$", re.IGNORECASE)
        return [
            h
            for h in self.get_hashes(since)
            if pattern.match(self.get_original_message(h))
        ]

    def get_combined_diff(self, hashes: list[str], context_lines: int) -> str:
        return "".join(self.get_diff(h, context_lines) for h in hashes)

    def amend(self, message: str) -> None:
        if self._dry_run:
            print(f"[dry run] would amend: {message}")
            return
        subprocess.run(["git", "commit", "--amend", "-m", message], check=True)

    def stage_all(self) -> None:
        if self._dry_run:
            print("[dry run] would run: git add -A")
            return
        subprocess.run(["git", "add", "-A"], check=True)

    def has_staged_changes(self) -> bool:
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"], capture_output=True
        )
        return result.returncode != 0

    def commit(self, message: str) -> None:
        if self._dry_run:
            print(f"[dry run] would commit: {message}")
            return
        subprocess.run(["git", "commit", "-m", message], check=True)

    def get_short_hash(self, ref: str = "HEAD") -> str:
        result = subprocess.run(
            ["git", "rev-parse", "--short", ref],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()

    def get_original_message(self, commit_hash: str) -> str:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%s", commit_hash],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()

    def rebase(
        self,
        since: str,
        messages: list[str],
        messages_file: Path,
        hashes_to_reword: Optional[set[str]] = None,
        squash_hashes: Optional[set[str]] = None,
    ) -> None:
        if self._dry_run:
            print(f"[dry run] would apply {len(messages)} commit message(s)")
            return
        messages_file.write_text("\n".join(messages) + "\n")

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as cf:
            cf.write("0")
        counter_file = Path(cf.name)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as sf:
            pass
        seq_editor = Path(sf.name)
        if squash_hashes is not None:
            seq_editor.write_text(
                "#!/usr/bin/env python3\n"
                "import sys\n"
                f"cp_hashes = {repr(squash_hashes)}\n"
                "p = sys.argv[1]\n"
                "lines = open(p).read().splitlines()\n"
                "cp_lines, other_lines = [], []\n"
                "for line in lines:\n"
                "    parts = line.split(None, 2)\n"
                "    if parts and parts[0] == 'pick' and len(parts) >= 2 and parts[1][:7] in cp_hashes:\n"
                "        cp_lines.append(line)\n"
                "    else:\n"
                "        other_lines.append(line)\n"
                "result = []\n"
                "for i, line in enumerate(cp_lines):\n"
                "    parts = line.split(None, 2)\n"
                "    if i == 0:\n"
                "        result.append('reword ' + ' '.join(parts[1:]))\n"
                "    else:\n"
                "        result.append('fixup ' + ' '.join(parts[1:]))\n"
                "result.extend(other_lines)\n"
                "open(p, 'w').write('\\n'.join(result) + '\\n')\n"
            )
        elif hashes_to_reword is not None:
            seq_editor.write_text(
                "#!/usr/bin/env python3\n"
                "import sys\n"
                f"hashes = {repr(hashes_to_reword)}\n"
                "p = sys.argv[1]\n"
                "lines = []\n"
                "for line in open(p).read().splitlines():\n"
                "    parts = line.split(None, 2)\n"
                "    if parts and parts[0] == 'pick' and len(parts) >= 2 and parts[1][:7] in hashes:\n"
                "        line = 'reword ' + ' '.join(parts[1:])\n"
                "    lines.append(line)\n"
                "open(p, 'w').write('\\n'.join(lines) + '\\n')\n"
            )
        else:
            seq_editor.write_text(
                "#!/usr/bin/env python3\n"
                "import sys, re\n"
                "p = sys.argv[1]\n"
                "content = open(p).read()\n"
                "open(p, 'w').write(re.sub(r'^pick\\b', 'reword', content, flags=re.MULTILINE))\n"
            )
        seq_editor.chmod(seq_editor.stat().st_mode | stat.S_IEXEC)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as mf:
            pass
        msg_editor = Path(mf.name)
        msg_editor.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            f"cf, mf = '{counter_file}', '{messages_file}'\n"
            "n = int(open(cf).read().strip()) + 1\n"
            "open(cf, 'w').write(str(n))\n"
            "lines = open(mf).read().splitlines()\n"
            "open(sys.argv[1], 'w').write((lines[n - 1] if n <= len(lines) else '') + '\\n')\n"
        )
        msg_editor.chmod(msg_editor.stat().st_mode | stat.S_IEXEC)

        try:
            cmd = ["git", "rebase", "-i"] + (
                ["--root"] if since == "--root" else [since]
            )
            subprocess.run(
                cmd,
                env={
                    **os.environ,
                    "GIT_SEQUENCE_EDITOR": str(seq_editor),
                    "GIT_EDITOR": str(msg_editor),
                },
                check=True,
            )
        finally:
            for f in [counter_file, seq_editor, msg_editor]:
                f.unlink(missing_ok=True)
