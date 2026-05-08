"""Parler-TTS engine — local, voice via text description."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer

from podcast_playground.engines.base import BaseEngine

VOICE_MAP: dict[str, str] = {
    "host_a": (
        "A male speaker with a warm, conversational tone"
        " and moderate pace."
        " Clear enunciation in a studio setting."
    ),
    "host_b": (
        "A female speaker with an energetic, friendly"
        " tone."
        " Slightly faster pace with natural enthusiasm."
    ),
    "narrator": (
        "A calm, professional male voice with slow,"
        " deliberate pacing."
        " Deep tone suitable for narration."
    ),
    "casual": (
        "A young female speaker with a casual, relaxed"
        " tone."
        " Natural speech with occasional pauses."
    ),
}

MODEL_ID = "parler-tts/parler-tts-mini-v1"


@dataclass
class ParlerEngine(BaseEngine):
    """TTS with voice control via text description."""

    model_id: str = MODEL_ID
    device: str = "auto"
    _model: ParlerTTSForConditionalGeneration | None = (
        field(default=None, repr=False)
    )
    _tokenizer: AutoTokenizer | None = field(
        default=None,
        repr=False,
    )

    def _resolve_device(self) -> str:
        if self.device != "auto":
            return self.device
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _load(self) -> None:
        self.device = self._resolve_device()
        print(f"Loading Parler-TTS on {self.device}...")
        self._model = (
            ParlerTTSForConditionalGeneration.from_pretrained(
                self.model_id,
            ).to(self.device)
        )
        self._tokenizer = AutoTokenizer.from_pretrained(
            self.model_id,
        )

    def get_voice(self, preset: str) -> str:
        return VOICE_MAP.get(preset, preset)

    def synthesize(
        self,
        text: str,
        voice: str,
    ) -> tuple[np.ndarray, int]:
        if self._model is None:
            self._load()

        voice_desc = self.get_voice(voice)
        input_ids = self._tokenizer(
            voice_desc,
            return_tensors="pt",
        ).input_ids.to(self.device)
        prompt_ids = self._tokenizer(
            text,
            return_tensors="pt",
        ).input_ids.to(self.device)

        with torch.no_grad():
            generation = self._model.generate(
                input_ids=input_ids,
                prompt_input_ids=prompt_ids,
            )

        audio = generation.cpu().numpy().squeeze()
        return audio, self._model.config.sampling_rate
