from abc import ABC, abstractmethod


class AIProvider(ABC):
    @property
    @abstractmethod
    def generate_system(self) -> str:
        """System message used for commit generation."""

    @property
    @abstractmethod
    def branch_system(self) -> str:
        """System message used for branch name generation."""

    @abstractmethod
    def generate(self, prompt: str) -> dict:
        """Return structured commit message dict."""

    @abstractmethod
    def generate_branch(self, prompt: str) -> dict:
        """Return structured branch name dict."""
