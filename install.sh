#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/bin"

echo "Installing git-reflow..."

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required." >&2
    exit 1
fi

install_pkg() {
    pip3 install --quiet --user "$1" 2>/dev/null || pip3 install --quiet --break-system-packages "$1"
}

# Install required packages if missing
if ! python3 -c "import anthropic" &> /dev/null; then
    echo "  Installing anthropic..."
    install_pkg anthropic
fi
if ! python3 -c "import openai" &> /dev/null; then
    echo "  Installing openai..."
    install_pkg openai
fi
if ! python3 -c "import ollama" &> /dev/null; then
    echo "  Installing ollama..."
    install_pkg ollama
fi

# Create ~/bin if it doesn't exist
mkdir -p "$BIN_DIR"

# Copy and make executable
cp "$SCRIPT_DIR/git-reflow" "$BIN_DIR/git-reflow"
chmod +x "$BIN_DIR/git-reflow"
echo "  Installed to $BIN_DIR/git-reflow"

# Short aliases as symlinks
for alias in git-rf git-rw git-ck git-rb git-sq git-ra; do
    ln -sf "$BIN_DIR/git-reflow" "$BIN_DIR/$alias"
    echo "  Linked $BIN_DIR/$alias → git-reflow"
done

# Add ~/bin to PATH if not already there
add_to_path() {
    local rc_file="$1"
    if [ -f "$rc_file" ] && ! grep -q 'export PATH="$HOME/bin' "$rc_file"; then
        echo '' >> "$rc_file"
        echo '# git extensions' >> "$rc_file"
        echo 'export PATH="$HOME/bin:$PATH"' >> "$rc_file"
        echo "  Added \$HOME/bin to PATH in $rc_file"
    fi
}


if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    add_to_path "$HOME/.zprofile"
    add_to_path "$HOME/.zshrc"
    add_to_path "$HOME/.bashrc"
    export PATH="$BIN_DIR:$PATH"
    echo "  Note: restart your shell (or run: export PATH=\"\$HOME/bin:\$PATH\")"
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
echo "    git rw ck                           reword checkpoint commits interactively"
echo "    git rw ck --claude                  reword checkpoint commits via AI"
echo ""
echo "  Squash checkpoints into one commit:"
echo "    git reflow squash --claude            squash all checkpoints into one AI-named commit"
echo "    git sq                              short alias"
echo ""
echo "  Amend last commit message:"
echo "    git reflow --amend --claude           AI rewrite last commit via amend"
echo "    git ra                              short alias"
echo ""
echo "  Branch rename:"
echo "    git reflow --branch --claude          generate and rename current branch via Claude"
echo "    git rb                              short alias"
echo "    git rb --prefix feature             force a branch prefix"
echo ""
echo "  Checkpoint (commit staged changes with sequential message):"
echo "    git reflow checkpoint                 commit staged as Checkpoint #N"
echo "    git ck                              short alias"
echo ""
echo "  Flags:"
echo "    --auto                              auto-generate messages via AI"
echo "    --branch / -b                       generate and rename current branch"
echo "    --amend / -a                        AI rewrite last commit message via amend"
echo "    --prefix PREFIX                     prefix for branch name (e.g. feature, fix, chore)"
echo "    -v / -vvv                           verbosity (AI output / + prompts)"
echo ""
echo "  Provider model overrides:"
echo "    --claude-model MODEL                Claude model name"
echo "    --openai-model MODEL                OpenAI model name"
echo "    --ollama-model MODEL                Ollama model name"
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
echo "    git config reflow.prompt \"Your prompt with {diff}\""
echo ""
echo "  API keys (env vars):"
echo "    export ANTHROPIC_API_KEY=sk-ant-...  (for --claude)"
echo "    export OPENAI_API_KEY=sk-...         (for --openai)"
