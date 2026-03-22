import subprocess
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]


class GitConfigLoader:
    _KEYS = [
        "provider", "claudeModel", "ollamaModel", "ollamaUrl",
        "openaiModel", "openaiUrl", "commitPrompt", "branchPrompt",
        "contextLines", "branchContextLines", "branchPrefix", "checkpointAutoStage",
    ]

    def load(self) -> dict[str, str]:
        cfg = {}
        for key in self._KEYS:
            result = subprocess.run(
                ["git", "config", "--get", f"reflow.{key}"],
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                cfg[key] = result.stdout.strip()
        return cfg


class ReflowFileLoader:
    def load(self) -> dict[str, str]:
        if tomllib is None:
            return {}
        root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True,
        )
        if root.returncode != 0:
            return {}
        path = Path(root.stdout.strip()) / ".reflow"
        if not path.exists():
            return {}
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return {k: v for k, v in data.items() if k in ("commitPrompt", "branchPrompt")}
