from __future__ import annotations

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion


class DynamicCompleter(Completer):
    def __init__(self, words_provider) -> None:
        self.words_provider = words_provider

    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor().lower()
        for candidate in self.words_provider():
            if candidate.lower().startswith(word):
                yield Completion(candidate, start_position=-len(word))


class CommandInput:
    def __init__(self, words_provider) -> None:
        self._session = PromptSession(completer=DynamicCompleter(words_provider))

    def prompt(self, prompt_text: str) -> str:
        try:
            return self._session.prompt(prompt_text)
        except Exception:
            return input(prompt_text)
