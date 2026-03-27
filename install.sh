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
    echo "  Note: restart your shell or run: export PATH=\"$SCRIPTS_DIR:\$PATH\""
fi

echo ""
echo "Installation complete. Usage:"
echo ""
echo "  Reword branch commits:"
echo "    reflow reword --claude                alias: rw --claude"
echo "    reflow reword HEAD~5 --claude"
echo ""
echo "  Reword checkpoint commits:"
echo "    reflow reword checkpoint --claude     alias: rw ck --claude"
echo ""
echo "  Checkpoint:"
echo "    reflow checkpoint                     alias: ck"
echo ""
echo "  Squash checkpoints into one commit:"
echo "    reflow --squash --claude              alias: rf -s --claude"
echo ""
echo "  Amend last commit:"
echo "    reflow --amend --claude               alias: rf -a --claude"
echo ""
echo "  Rename branch:"
echo "    reflow --branch --claude              alias: rf -b --claude"
echo "    reflow --branch --claude --prefix feature"
echo ""
echo "  Flags:"
echo "    --squash / -s                         squash checkpoint commits"
echo "    --branch / -b                         generate and rename current branch"
echo "    --amend / -a                          AI rewrite last commit message via amend"
echo "    --prefix PREFIX                       prefix for branch name"
echo "    -v / -vv                              verbosity"
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
echo "    git config reflow.autoAccept false"
echo "    git config reflow.checkpointAutoStage false"
echo "    git config reflow.commitPrompt \"Your commit prompt with {diff}\""
echo "    git config reflow.branchPrompt \"Your branch prompt with {diff}\""
echo ""
echo "  API keys (env vars):"
echo "    export GIT_REFLOW_ANTHROPIC_API_KEY=sk-ant-..."
echo "    export GIT_REFLOW_OPENAI_API_KEY=sk-..."
echo "    export GIT_REFLOW_OLLAMA_API_KEY=...        uses ollama.com by default"
