# reflow

CLI tool that rewrites git commit messages using AI.

## Install

```sh
./install.sh
```

## Usage

```sh
# Reword branch commits
reflow reword --claude               # alias: rw --claude
reflow reword HEAD~5 --claude

# Reword only checkpoint commits
reflow reword checkpoint --claude    # alias: rw ck --claude

# Create a checkpoint commit
reflow checkpoint                    # alias: ck

# Squash checkpoints into one commit
reflow --squash --claude             # alias: rf -s --claude

# Amend last commit
reflow --amend --claude              # alias: rf -a --claude

# Rename current branch
reflow --branch --claude             # alias: rf -b --claude
reflow --branch --claude --prefix feature
```

## Configuration

```sh
# Provider
git config reflow.provider claude|openai|ollama

# Models
git config reflow.claudeModel claude-haiku-4-5-20251001
git config reflow.openaiModel gpt-4o-mini
git config reflow.ollamaModel llama3.2
git config reflow.ollamaUrl http://localhost:11434

# Behavior
git config reflow.autoAccept false          # prompt before applying (default: true)
git config reflow.checkpointAutoStage false # don't auto-stage on checkpoint (default: true)
git config reflow.contextLines 10
git config reflow.branchContextLines 3
git config reflow.branchPrefix feature

# Custom prompts
git config reflow.commitPrompt "Your prompt with {diff}"
git config reflow.branchPrompt "Your prompt with {diff}"
```

Per-repo prompts can also be set in a `.reflow` TOML file:

```toml
commitPrompt = "Your prompt with {diff}"
branchPrompt = "Your prompt with {diff}"
```

## API Keys

```sh
export GIT_REFLOW_ANTHROPIC_API_KEY=sk-ant-...
export GIT_REFLOW_OPENAI_API_KEY=sk-...
export GIT_REFLOW_OLLAMA_API_KEY=...      # uses ollama.com by default
```
