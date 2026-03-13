# git-reword

A git subcommand to reword commit messages interactively or automatically via the Claude API.

## Installation

```bash
cd git-reword
./install.sh
```

This copies `git-reword` to `~/bin/` and ensures `~/bin` is in your `$PATH`.

## Usage

```bash
# Reword all commits interactively (prompts for each one)
git reword

# Reword the last 5 commits interactively
git reword HEAD~5

# Auto-generate all messages using Claude API
git reword --auto

# Auto-generate messages for the last 5 commits
git reword HEAD~5 --auto
```

## Modes

### Interactive mode (default)

For each commit, shows the current message and changed files, then prompts for a new message. Press Enter to keep the existing message.

```
──────────────────────────────────────────
Commit: a04550b
Current: Fix settings and URL config

 config/settings.py | 2 +-
 tracker/urls.py    | 3 +-

New message (≤5 words, blank = keep): _
```

### Auto mode (`--auto`)

Sends the full commit log and file stats to the Claude API (`claude-haiku-4-5`). Claude generates a concise, imperative message (≤5 words) for each commit based on the files changed. You review the proposed messages before they are applied.

Requires `ANTHROPIC_API_KEY` and `curl` to be available.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
git reword --auto
```

Also requires `jq` for JSON handling:
```bash
brew install jq      # macOS
apt install jq       # Debian/Ubuntu
```

## Requirements

| Feature | Requires |
|---------|----------|
| Interactive mode | bash 4+ |
| Auto mode | bash 4+, curl, jq, `ANTHROPIC_API_KEY` |

## How it works

1. Collects commits oldest-to-newest in the given range
2. Builds a messages file (one message per line, in order)
3. Runs `git rebase -i` with two injected scripts:
   - `GIT_SEQUENCE_EDITOR` marks every commit as `reword`
   - `GIT_EDITOR` supplies the next message from the file each time git opens an editor
4. Cleans up all temp files on exit
