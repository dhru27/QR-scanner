from __future__ import annotations

import os
from dataclasses import dataclass

from google import genai


@dataclass(frozen=True)
class GeminiConfig:
    model: str = "gemini-2.5-flash"


def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "Missing GEMINI_API_KEY. Create a .env file (see .env.example) and set GEMINI_API_KEY."
        )
    return genai.Client(api_key=api_key)


def generate_text(*, prompt: str, config: GeminiConfig | None = None) -> str:
    cfg = config or GeminiConfig()
    client = get_client()
    resp = client.models.generate_content(model=cfg.model, contents=prompt)
    text = (resp.text or "").strip()
    return text
