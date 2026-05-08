"""Core podcast generator."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf

from podcast_playground.engines import ENGINES, BaseEngine
from podcast_playground.script import (
    DialogueLine,
    generate_script,
    parse_script_file,
)

PAUSE_SECONDS = 0.5


def create_engine(
    name: str = "edge",
    **kwargs,
) -> BaseEngine:
    """Create TTS engine by name."""
    engine_cls = ENGINES.get(name)
    if engine_cls is None:
        raise ValueError(
            f"Unknown engine '{name}'."
            f" Options: {list(ENGINES.keys())}",
        )
    return engine_cls(**kwargs)


@dataclass
class PodcastGenerator:
    """Combines script generation + TTS rendering."""

    engine: BaseEngine
    pause: float = PAUSE_SECONDS

    def from_script(
        self,
        script_path: str | Path,
        output: str = "podcast.wav",
    ) -> Path:
        """Generate podcast from pre-written script."""
        dialogue = parse_script_file(Path(script_path))
        return self._render(dialogue, output)

    def from_source(
        self,
        source: str | Path,
        output: str = "podcast.wav",
        model: str = "llama3",
    ) -> Path:
        """Generate podcast from source text/file."""
        dialogue = generate_script(source, model)
        if not dialogue:
            raise ValueError(
                "Failed to generate dialogue from source",
            )

        script_out = Path(output).with_suffix(".script.txt")
        with open(script_out, "w", encoding="utf-8") as f:
            for line in dialogue:
                f.write(
                    f"{line.speaker.upper()}: {line.text}\n",
                )
        print(f"Script saved to {script_out}")

        return self._render(dialogue, output)

    def say(
        self,
        text: str,
        voice: str = "narrator",
        output: str = "output.wav",
    ) -> Path:
        """Single voice synthesis."""
        print(f"Generating with voice '{voice}'...")
        audio, sr = self.engine.synthesize(text, voice)
        out_path = Path(output)
        sf.write(str(out_path), audio, sr)
        print(f"Saved to {out_path}")
        return out_path

    def _render(
        self,
        dialogue: list[DialogueLine],
        output: str,
    ) -> Path:
        segments: list[np.ndarray] = []
        sr = None
        total = len(dialogue)

        for i, line in enumerate(dialogue, 1):
            print(
                f"[{i}/{total}] {line.speaker}:"
                f" {line.text[:50]}...",
            )
            audio, sr = self.engine.synthesize(
                line.text,
                line.speaker,
            )
            segments.append(audio)
            segments.append(
                np.zeros(int(sr * self.pause)),
            )

        full_audio = np.concatenate(segments)
        out_path = Path(output)
        sf.write(str(out_path), full_audio, sr)
        print(f"Podcast saved to {out_path}")
        return out_path
