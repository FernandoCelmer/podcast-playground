"""Script generation via Ollama (free, local LLM)."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

SYSTEM_PROMPT = (
    "You are a podcast script writer."
    " Given source material, create an engaging"
    " two-host podcast dialogue.\n\n"
    "Rules:\n"
    "- HOST_A explains, HOST_B asks questions and reacts\n"
    "- Conversational, natural, with occasional humor\n"
    "- Include natural speech patterns (hmm, right, exactly)\n"
    "- Cover key points from the source material\n"
    "- Output ONLY the dialogue, one line per turn\n"
    "- Format: HOST_A: text\n"
    "- Write in the same language as the source material"
)


@dataclass
class DialogueLine:
    speaker: str
    text: str


def generate_script(
    source: str | Path,
    model: str = "llama3",
) -> list[DialogueLine]:
    """Generate podcast script from text or file."""
    if isinstance(source, Path) or Path(source).exists():
        source = Path(source).read_text(encoding="utf-8")

    prompt = f"{SYSTEM_PROMPT}\n\nSource material:\n{source}"
    print(f"Generating script with {model}...")

    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt,
        capture_output=True,
        text=True,
        check=True,
    )

    return parse_script(result.stdout)


def parse_script(raw: str) -> list[DialogueLine]:
    """Parse raw script text into DialogueLine list."""
    dialogue: list[DialogueLine] = []

    for line in raw.strip().splitlines():
        if ":" not in line:
            continue
        speaker, text = line.split(":", 1)
        speaker = speaker.strip().lower().replace(" ", "_")
        text = text.strip()
        if text:
            dialogue.append(
                DialogueLine(speaker=speaker, text=text),
            )

    return dialogue


def parse_script_file(path: Path) -> list[DialogueLine]:
    """Parse a pre-written script file."""
    if not path.exists():
        raise FileNotFoundError(f"Script not found: {path}")
    return parse_script(path.read_text(encoding="utf-8"))
