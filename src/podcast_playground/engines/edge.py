"""edge-tts engine — free Microsoft Neural voices."""

from __future__ import annotations

import asyncio
import io
from dataclasses import dataclass

import edge_tts
import numpy as np
from pydub import AudioSegment

from podcast_playground.engines.base import BaseEngine

VOICE_MAP: dict[str, str] = {
    "host_a": "pt-BR-AntonioNeural",
    "host_b": "pt-BR-FranciscaNeural",
    "narrator": "pt-BR-AntonioNeural",
    "casual": "pt-BR-ThalitaNeural",
}


@dataclass
class EdgeEngine(BaseEngine):
    """Free TTS via Microsoft Azure Neural voices."""

    def get_voice(self, preset: str) -> str:
        return VOICE_MAP.get(preset, preset)

    def synthesize(
        self,
        text: str,
        voice: str,
    ) -> tuple[np.ndarray, int]:
        voice_id = self.get_voice(voice)

        async def _stream() -> bytes:
            communicate = edge_tts.Communicate(
                text,
                voice_id,
            )
            chunks = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    chunks += chunk["data"]
            return chunks

        mp3_data = asyncio.run(_stream())
        segment = AudioSegment.from_mp3(io.BytesIO(mp3_data))
        samples = np.array(
            segment.get_array_of_samples(),
            dtype=np.float32,
        )
        samples /= 2**15
        return samples, segment.frame_rate
