# reflow

Reflow is a git extension designed to help you stay focused by reducing friction during vibe coding.

Reflow was built for developers who get into a flow state and do not want to stop to think about commit messages and branch names. Instead of interrupting your momentum, you can save quick checkpoints of what you have staged and let AI organize them later into clear, consistent, and useful commits.

## Installation

```sh
pip install .
```

### Installation


### Reword

Rewrites commit messages for all commits on the current branch using AI.

```sh
reflow reword
```
alias: **rw**

Rewrites commit messages for the last N commits using AI.

```sh
reflow reword 5
```
Note: **5** is shorthand for **HEAD~5**. 


### Checkpoint

Saves a checkpoint commit of the currently staged changes.

```sh
reflow checkpoint
```
alias: **ck**


### Reword Checkpoints

Rewrites commit messages only for checkpoint commits on the current branch using AI.

```sh
reflow reword checkpoint
```
alias: **rw ck**


### Squash

Squashes all checkpoint commits into a single commit.

```sh
reflow --squash
```
alias: **rw -s**


### Amend

Rewrites the last commit message using AI via amend.

```sh
reflow --amend
```
alias: **rf -a**


### Branch

Generates and renames the current branch based on the diff using AI.

```sh
reflow --branch
```
alias: **rf -b**


## Configuration

All settings are stored as git config keys under the `reflow` namespace.

```sh
git config reflow.<key> <value>
```

**reflow.provider**
AI provider to use
**default**: none
**options**: claude, openai, ollama

**reflow.claudeModel**
Claude model to use
**default**: claude-haiku-4-5-20251001

**reflow.openaiModel**
OpenAI model to use
**default**: gpt-4o-mini

**reflow.ollamaModel**
Ollama model to use
**default**: llama3.2

**reflow.ollamaUrl**
Ollama server URL
**default**: http://localhost:11434

**reflow.contextLines**
Lines of diff context sent to AI for commit messages
**default**: 3

**reflow.branchContextLines**
Lines of diff context sent to AI for branch names
**default**: 3

**reflow.branchPrefix**
Default prefix for generated branch names
**default**: none

**reflow.autoAccept**
Skip confirmation prompts before applying changes
**default**: true
**options**: true, false

**reflow.checkpointAutoStage**
Automatically stage all changes before creating a checkpoint
**default**: true
**options**: true, false

**reflow.commitPrompt**
Custom prompt template for commit messages, use `{diff}` as placeholder
**default**: none

**reflow.branchPrompt**
Custom prompt template for branch names, use `{diff}` as placeholder
**default**: none

Per-repo prompts can also be set in a `.reflow` TOML file:

```toml
commitPrompt = "Your prompt with {diff}"
branchPrompt = "Your prompt with {diff}"
```

## API Keys

```sh
export REFLOW_ANTHROPIC_API_KEY=sk-ant-...
export REFLOW_OPENAI_API_KEY=sk-...
export REFLOW_OLLAMA_API_KEY=...
```
