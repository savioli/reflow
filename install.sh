#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing git-reflow..."

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required." >&2
    exit 1
fi

# Install package (entry points are created automatically)
pip3 install --quiet --user "$SCRIPT_DIR" 2>/dev/null || \
    pip3 install --quiet --break-system-packages "$SCRIPT_DIR"

# Add pip user scripts dir to PATH if needed
SCRIPTS_DIR="$(python3 -m site --user-scripts 2>/dev/null || echo "$HOME/.local/bin")"
if [[ ":$PATH:" != *":$SCRIPTS_DIR:"* ]]; then
    add_to_path() {
        local rc_file="$1"
        if [ -f "$rc_file" ] && ! grep -q "$SCRIPTS_DIR" "$rc_file"; then
            echo '' >> "$rc_file"
            echo '# git extensions' >> "$rc_file"
            echo "export PATH=\"$SCRIPTS_DIR:\$PATH\"" >> "$rc_file"
            echo "  Added $SCRIPTS_DIR to PATH in $rc_file"
        fi
    }
    add_to_path "$HOME/.zprofile"
    add_to_path "$HOME/.zshrc"
    add_to_path "$HOME/.bashrc"
    export PATH="$SCRIPTS_DIR:$PATH"
    echo "  Note: restart your shell (or run: export PATH=\"$SCRIPTS_DIR:\$PATH\")"
fi

echo ""
echo "Installation complete. Usage:"
echo ""
echo "  Interactive (branch commits only by default):"
echo "    git reflow                            reword branch commits interactively"
echo "    git reflow HEAD~5                     reword last 5 commits interactively"
echo ""
echo "  Auto mode (requires a provider flag or reflow.provider git config):"
echo "    git reflow --auto --claude            auto-generate via Claude"
echo "    git reflow --auto --openai            auto-generate via OpenAI"
echo "    git reflow --auto --ollama            auto-generate via Ollama"
echo "    git reflow HEAD~5 --auto --claude     auto mode on explicit range"
echo ""
echo "  Checkpoint reword (reword only checkpoint commits):"
echo "    git rw ck                             reword checkpoint commits interactively"
echo "    git rw ck --claude                    reword checkpoint commits via AI"
echo ""
echo "  Squash checkpoints into one commit:"
echo "    git reflow squash --claude            squash all checkpoints into one AI-named commit"
echo "    git sq                                short alias"
echo ""
echo "  Amend last commit message:"
echo "    git reflow --amend --claude           AI rewrite last commit via amend"
echo "    git ra                                short alias"
echo ""
echo "  Branch rename:"
echo "    git reflow --branch --claude          generate and rename current branch via Claude"
echo "    git rb                                short alias"
echo "    git rb --prefix feature               force a branch prefix"
echo ""
echo "  Checkpoint (commit staged changes with sequential message):"
echo "    git reflow checkpoint                 commit staged as Checkpoint #N"
echo "    git ck                                short alias"
echo ""
echo "  Flags:"
echo "    --auto                                auto-generate messages via AI"
echo "    --branch / -b                         generate and rename current branch"
echo "    --amend / -a                          AI rewrite last commit message via amend"
echo "    --prefix PREFIX                       prefix for branch name (e.g. feature, fix, chore)"
echo "    -v / -vvv                             verbosity (AI output / + prompts)"
echo ""
echo "  Provider model overrides:"
echo "    --claude-model MODEL                  Claude model name"
echo "    --openai-model MODEL                  OpenAI model name"
echo "    --ollama-model MODEL                  Ollama model name"
echo ""
echo "  Git config (per-repo defaults):"
echo "    git config reflow.provider claude|openai|ollama"
echo "    git config reflow.claudeModel claude-haiku-4-5-20251001"
echo "    git config reflow.openaiModel gpt-4o-mini"
echo "    git config reflow.ollamaModel llama3.2"
echo "    git config reflow.ollamaUrl http://localhost:11434"
echo "    git config reflow.contextLines 10"
echo "    git config reflow.branchContextLines 3"
echo "    git config reflow.branchPrefix feature"
echo "    git config reflow.checkpointAutoStage false"
echo "    git config reflow.commitPrompt \"Your commit prompt with {diff}\""
echo "    git config reflow.branchPrompt \"Your branch prompt with {diff}\""
echo ""
echo "  API keys (env vars):"
echo "    export ANTHROPIC_API_KEY=sk-ant-...  (for --claude)"
echo "    export OPENAI_API_KEY=sk-...         (for --openai)"
