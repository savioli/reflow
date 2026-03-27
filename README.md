# reflow

Reflow is a git extension designed to help you stay focused by reducing Git friction during vibe coding.

Reflow was built for developers who get into a flow state and do not want to stop to think about commit messages. Instead of interrupting your momentum, you can save quick checkpoints of what you have staged and let AI organize them later into clear, consistent, and useful commits.

## Installation

```sh
pip install .
```

## Reword

```sh
reflow reword                        # alias: rw
```

## Reword Checkpoints

```sh
reflow reword checkpoint             # alias: rw ck
```

## Checkpoint

```sh
reflow checkpoint                    # alias: ck
```

## Squash

```sh
reflow --squash                      # alias: rf -s
```

## Amend

```sh
reflow --amend                       # alias: rf -a
```

## Branch

```sh
reflow --branch                      # alias: rf -b
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
