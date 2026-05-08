"""Bark engine — local, expressive TTS. Needs GPU."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from bark import SAMPLE_RATE, generate_audio, preload_models

from podcast_playground.engines.base import BaseEngine

VOICE_MAP: dict[str, str] = {
    "host_a": "v2/en_speaker_6",
    "host_b": "v2/en_speaker_9",
    "narrator": "v2/en_speaker_0",
    "casual": "v2/en_speaker_3",
}

MAX_CHUNK_LEN = 100


@dataclass
class BarkEngine(BaseEngine):
    """Expressive TTS with laughs, sighs, emotions."""

    _loaded: bool = field(default=False, repr=False)

    def _load(self) -> None:
        print("Loading Bark models...")
        preload_models()
        self._loaded = True

    def get_voice(self, preset: str) -> str:
        return VOICE_MAP.get(preset, preset)

    def synthesize(
        self,
        text: str,
        voice: str,
    ) -> tuple[np.ndarray, int]:
        if not self._loaded:
            self._load()

        chunks = self._chunk_text(text)
        segments = [
            generate_audio(chunk) for chunk in chunks
        ]
        audio = (
            np.concatenate(segments)
            if len(segments) > 1
            else segments[0]
        )
        return audio, SAMPLE_RATE

    @staticmethod
    def _chunk_text(text: str) -> list[str]:
        """Split text into chunks for Bark."""
        words = text.split()
        chunks: list[str] = []
        current: list[str] = []

        for word in words:
            current.append(word)
            if len(" ".join(current)) > MAX_CHUNK_LEN:
                chunks.append(" ".join(current))
                current = []

        if current:
            chunks.append(" ".join(current))

        return chunks
