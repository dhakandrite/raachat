"""Optional GPT4All client with safe template fallback."""

from __future__ import annotations

import logging

LOGGER = logging.getLogger(__name__)


class GPT4AllClient:
    """Wrapper around GPT4All; gracefully degrades when unavailable."""

    def __init__(self, model_name: str, model_path: str) -> None:
        self.available = False
        self.model = None
        try:
            from gpt4all import GPT4All  # type: ignore

            self.model = GPT4All(model_name=model_name, model_path=model_path)
            self.available = True
            LOGGER.info("GPT4All initialized with model %s", model_name)
        except Exception as exc:  # pragma: no cover - optional dependency
            LOGGER.warning("GPT4All unavailable; template-only mode. Reason: %s", exc)

    def generate_response(self, system_prompt: str, messages: list[dict[str, str]]) -> str:
        """Generate local response from GPT4All model."""
        if not self.available or self.model is None:
            raise RuntimeError("GPT4All not available")
        with self.model.chat_session(system_prompt):
            text = ""
            for msg in messages:
                text = self.model.generate(prompt=msg["content"], temp=0.2, max_tokens=400)
            return str(text).strip()
