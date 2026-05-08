"""Abstract base engine interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class BaseEngine(ABC):
    """Base TTS engine interface."""

    @abstractmethod
    def synthesize(
        self,
        text: str,
        voice: str,
    ) -> tuple[np.ndarray, int]:
        """Return (audio_array, sample_rate)."""

    @abstractmethod
    def get_voice(self, preset: str) -> str:
        """Resolve preset to engine-specific voice."""
