#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/bin"

echo "Installing git-reword..."

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
cp "$SCRIPT_DIR/git-reword" "$BIN_DIR/git-reword"
chmod +x "$BIN_DIR/git-reword"
echo "  Installed to $BIN_DIR/git-reword"

# Short aliases as symlinks
for alias in git-rw git-ck; do
    ln -sf "$BIN_DIR/git-reword" "$BIN_DIR/$alias"
    echo "  Linked $BIN_DIR/$alias → git-reword"
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
echo "    git reword                          reword branch commits interactively"
echo "    git reword HEAD~5                   reword last 5 commits interactively"
echo ""
echo "  Auto mode (requires a provider flag or reword.provider git config):"
echo "    git reword --auto --claude          auto-generate via Claude"
echo "    git reword --auto --openai          auto-generate via OpenAI"
echo "    git reword --auto --ollama          auto-generate via Ollama"
echo "    git reword HEAD~5 --auto --claude   auto mode on explicit range"
echo ""
echo "  Branch rename:"
echo "    git reword --branch --claude        generate and rename current branch via Claude"
echo "    git rw -b --openai                  short form"
echo "    git rw -b --claude --prefix feature force a branch prefix"
echo ""
echo "  Checkpoint (commit staged changes with sequential message):"
echo "    git reword checkpoint               commit staged as Checkpoint #N"
echo "    git ck                              short alias"
echo ""
echo "  Flags:"
echo "    --auto                              auto-generate messages via AI"
echo "    --branch / -b                       generate and rename current branch"
echo "    --prefix PREFIX                     prefix for branch name (e.g. feature, fix, chore)"
echo "    -v / -vvv                           verbosity (AI output / + prompts)"
echo ""
echo "  Provider model overrides:"
echo "    --claude-model MODEL                Claude model name"
echo "    --openai-model MODEL                OpenAI model name"
echo "    --ollama-model MODEL                Ollama model name"
echo ""
echo "  Git config (per-repo defaults):"
echo "    git config reword.provider claude|openai|ollama"
echo "    git config reword.claudeModel claude-haiku-4-5-20251001"
echo "    git config reword.openaiModel gpt-4o-mini"
echo "    git config reword.ollamaModel llama3.2"
echo "    git config reword.ollamaUrl http://localhost:11434"
echo "    git config reword.contextLines 10"
echo "    git config reword.branchContextLines 3"
echo "    git config reword.branchPrefix feature"
echo "    git config reword.checkpointAutoStage false"
echo "    git config reword.prompt \"Your prompt with {diff}\""
echo ""
echo "  API keys (env vars):"
echo "    export ANTHROPIC_API_KEY=sk-ant-...  (for --claude)"
echo "    export OPENAI_API_KEY=sk-...         (for --openai)"
