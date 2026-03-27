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

All settings are stored as git config keys under the `reflow` namespace and apply per repository.

```sh
git config reflow.<key> <value>
```

**reflow.provider**
AI provider to use
default: none | options: `claude`, `openai`, `ollama`

**reflow.claudeModel**
Claude model to use
default: `claude-haiku-4-5-20251001`

**reflow.openaiModel**
OpenAI model to use
default: `gpt-4o-mini`

**reflow.ollamaModel**
Ollama model to use
default: `llama3.2`

**reflow.ollamaUrl**
Ollama server URL
default: `http://localhost:11434`

**reflow.contextLines**
Lines of diff context sent to AI for commit messages
default: `3`

**reflow.branchContextLines**
Lines of diff context sent to AI for branch names
default: `3`

**reflow.branchPrefix**
Default prefix for generated branch names
default: none

**reflow.autoAccept**
Skip confirmation prompts before applying changes
default: `true` | options: `true`, `false`

**reflow.checkpointAutoStage**
Automatically stage all changes before creating a checkpoint
default: `true` | options: `true`, `false`

**reflow.commitPrompt**
Custom prompt template for commit messages. Use `{diff}` as placeholder.
default: none

**reflow.branchPrompt**
Custom prompt template for branch names. Use `{diff}` as placeholder.
default: none

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
