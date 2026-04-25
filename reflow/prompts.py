import sys
from typing import Optional

COMMIT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "message": {"type": "string", "minLength": 1},
    },
    "required": ["message"],
}

BRANCH_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {"name": {"type": "string", "minLength": 1}},
    "required": ["name"],
}


class PromptBuilder:
    def __init__(self) -> None:
        self._warned_diff = False
        self._warned_branch_diff = False

    _DEFAULT = (
        "Generate a git commit message for the diff below.\n"
        "\n"
        "Rules (follow strictly):\n"
        "1. Start with an imperative verb: Add, Fix, Update, Remove, Refactor, Extract, Move, Rename, etc.\n"
        "2. Maximum 5 words total\n"
        "3. Describe the intent or effect, not the mechanism\n"
        "4. No filenames, variable names, function names, or code tokens\n"
        "5. No punctuation at the end\n"
        "\n"
        "Good examples:\n"
        "  Add user authentication\n"
        "  Fix null pointer crash\n"
        "  Remove deprecated endpoint\n"
        "  Refactor payment processing\n"
        "  Update error handling logic\n"
        "\n"
        "Diff:\n{diff}"
    )

    _BRANCH = (
        "Generate a git branch name for the following diff.\n"
        "\n"
        "Rules (follow strictly):\n"
        "1. kebab-case: lowercase letters, numbers, and hyphens only\n"
        "2. 2 to 5 words\n"
        "3. Describes the purpose of the changes (e.g. add-user-auth, fix-payment-crash, refactor-api-layer)\n"
        "4. No special characters except hyphens\n"
        "\n"
        "Diff:\n{diff}"
    )

    def build(self, diff: str, template: Optional[str] = None) -> str:
        if (
            template
            and "{diff}" not in template
            and not self._warned_diff
        ):
            print(
                "Warning: reflow.commitPrompt does not contain {diff} — the diff will not be included in the prompt.",
                file=sys.stderr,
            )
            self._warned_diff = True
        return (template or self._DEFAULT).replace("{diff}", diff)

    def build_branch(self, diff: str, template: Optional[str] = None) -> str:
        if (
            template
            and "{diff}" not in template
            and not self._warned_branch_diff
        ):
            print(
                "Warning: reflow.branchPrompt does not contain {diff} — the diff will not be included in the prompt.",
                file=sys.stderr,
            )
            self._warned_branch_diff = True
        return (template or self._BRANCH).replace("{diff}", diff)
