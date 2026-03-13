#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/bin"

echo "Installing git-reword..."

# Create ~/bin if it doesn't exist
mkdir -p "$BIN_DIR"

# Copy and make executable
cp "$SCRIPT_DIR/git-reword" "$BIN_DIR/git-reword"
chmod +x "$BIN_DIR/git-reword"
echo "  Installed to $BIN_DIR/git-reword"

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
echo "  git reword                  reword all commits interactively"
echo "  git reword HEAD~5           reword last 5 commits interactively"
echo "  git reword --auto           auto-generate messages via Claude API"
echo "  git reword HEAD~5 --auto    auto mode on a range"
echo ""
echo "For --auto mode, set your API key:"
echo "  export ANTHROPIC_API_KEY=sk-ant-..."
