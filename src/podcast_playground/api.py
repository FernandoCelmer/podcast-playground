"""FastAPI server for podcast generation."""

from __future__ import annotations

import uuid
from enum import Enum
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from podcast_playground.core import (
    PodcastGenerator,
    create_engine,
)
from podcast_playground.engines import ENGINES
from podcast_playground.script import parse_script

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="Podcast Playground API",
    version="0.1.0",
    description="Generate podcast-style audio with multiple TTS engines.",
)


class EngineEnum(str, Enum):
    edge = "edge"
    bark = "bark"
    parler = "parler"


class VoiceEnum(str, Enum):
    host_a = "host_a"
    host_b = "host_b"
    narrator = "narrator"
    casual = "casual"


class SayRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )
    engine: EngineEnum = EngineEnum.edge
    voice: VoiceEnum = VoiceEnum.narrator


class ScriptLine(BaseModel):
    speaker: str = Field(
        ...,
        pattern=r"^[a-z_]+$",
    )
    text: str = Field(..., min_length=1)


class PodcastRequest(BaseModel):
    script: list[ScriptLine] = Field(
        ...,
        min_length=1,
    )
    engine: EngineEnum = EngineEnum.edge


class ScriptTextRequest(BaseModel):
    script_text: str = Field(
        ...,
        min_length=1,
        max_length=50000,
    )
    engine: EngineEnum = EngineEnum.edge


class GenerateResponse(BaseModel):
    id: str
    download_url: str
    engine: str
    message: str


def _generate_id() -> str:
    return uuid.uuid4().hex[:12]


@app.get("/health")
def health():
    """Health check."""
    return {"status": "ok"}


@app.get("/engines")
def list_engines():
    """List available TTS engines."""
    return {"engines": list(ENGINES.keys())}


@app.post("/say", response_model=GenerateResponse)
def say(req: SayRequest):
    """Generate speech from text."""
    file_id = _generate_id()
    filename = f"{file_id}.wav"
    output_path = OUTPUT_DIR / filename

    engine = create_engine(req.engine.value)
    gen = PodcastGenerator(engine=engine)
    gen.say(req.text, req.voice.value, str(output_path))

    return GenerateResponse(
        id=file_id,
        download_url=f"/download/{file_id}",
        engine=req.engine.value,
        message="Audio generated",
    )


@app.post("/podcast", response_model=GenerateResponse)
def podcast(req: PodcastRequest):
    """Generate podcast from structured script."""
    file_id = _generate_id()
    filename = f"{file_id}.wav"
    output_path = OUTPUT_DIR / filename

    raw_script = "\n".join(
        f"{line.speaker.upper()}: {line.text}"
        for line in req.script
    )
    script_path = OUTPUT_DIR / f"{file_id}.txt"
    script_path.write_text(raw_script, encoding="utf-8")

    engine = create_engine(req.engine.value)
    gen = PodcastGenerator(engine=engine)
    gen.from_script(str(script_path), str(output_path))

    return GenerateResponse(
        id=file_id,
        download_url=f"/download/{file_id}",
        engine=req.engine.value,
        message="Podcast generated",
    )


@app.post(
    "/podcast/text",
    response_model=GenerateResponse,
)
def podcast_from_text(req: ScriptTextRequest):
    """Generate podcast from raw script text."""
    file_id = _generate_id()
    filename = f"{file_id}.wav"
    output_path = OUTPUT_DIR / filename

    script_path = OUTPUT_DIR / f"{file_id}.txt"
    script_path.write_text(
        req.script_text,
        encoding="utf-8",
    )

    dialogue = parse_script(req.script_text)
    if not dialogue:
        raise HTTPException(
            status_code=400,
            detail="No dialogue found in script",
        )

    engine = create_engine(req.engine.value)
    gen = PodcastGenerator(engine=engine)
    gen.from_script(str(script_path), str(output_path))

    return GenerateResponse(
        id=file_id,
        download_url=f"/download/{file_id}",
        engine=req.engine.value,
        message="Podcast generated",
    )


@app.get("/download/{file_id}")
def download(file_id: str):
    """Download generated audio file."""
    filepath = OUTPUT_DIR / f"{file_id}.wav"
    if not filepath.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )
    return FileResponse(
        str(filepath),
        media_type="audio/wav",
        filename=f"{file_id}.wav",
    )
