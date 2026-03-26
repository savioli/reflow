import sys

from reflow.config import Config
from reflow.output import error, hint
from reflow.providers.base import AIProvider
from reflow.providers.claude import ClaudeProvider
from reflow.providers.ollama import OllamaProvider
from reflow.providers.openai import OpenAIProvider


class ProviderFactory:
    def create(self, config: Config) -> AIProvider:
        if config.use_openai:
            return OpenAIProvider(config.openai_api_key, config.openai_model, config.openai_url)
        if config.use_ollama:
            provider = OllamaProvider(config.ollama_url, config.ollama_model)
            provider.check()
            return provider
        if config.use_claude:
            return ClaudeProvider(config.anthropic_api_key, config.claude_model)
        error("no AI provider defined")
        hint("use --claude, --openai, or --ollama")
        hint("or set: git config reflow.provider claude|openai|ollama")
        sys.exit(1)
