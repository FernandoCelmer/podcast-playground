"""
Podcast Playground - Generate podcast-style audio with Parler-TTS.
Supports single voice generation and two-host podcast dialogue.
100% free, runs locally.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer


VOICES = {
    "host_a": "A male speaker with a warm, conversational tone and moderate pace. Clear enunciation in a studio setting.",
    "host_b": "A female speaker with an energetic, friendly tone. Slightly faster pace with natural enthusiasm.",
    "narrator": "A calm, professional male voice with slow, deliberate pacing. Deep tone suitable for narration.",
    "casual": "A young female speaker with a casual, relaxed tone. Natural speech with occasional pauses.",
}

MODEL_ID = "parler-tts/parler-tts-mini-v1"


def load_model(device: str = "auto"):
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

    print(f"Loading model on {device}...")
    model = ParlerTTSForConditionalGeneration.from_pretrained(MODEL_ID).to(device)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    return model, tokenizer, device


def generate_speech(model, tokenizer, text: str, voice_description: str, device: str) -> tuple[np.ndarray, int]:
    input_ids = tokenizer(voice_description, return_tensors="pt").input_ids.to(device)
    prompt_ids = tokenizer(text, return_tensors="pt").input_ids.to(device)

    with torch.no_grad():
        generation = model.generate(input_ids=input_ids, prompt_input_ids=prompt_ids)

    audio = generation.cpu().numpy().squeeze()
    return audio, model.config.sampling_rate


def generate_single(text: str, voice: str, output: str):
    model, tokenizer, device = load_model()
    voice_desc = VOICES.get(voice, voice)

    print(f"Generating speech with voice '{voice}'...")
    audio, sr = generate_speech(model, tokenizer, text, voice_desc, device)
    sf.write(output, audio, sr)
    print(f"Saved to {output}")


def generate_podcast(script_file: str, output: str):
    """
    Generate podcast from a script file.

    Script format (one line per turn):
        HOST_A: Hello and welcome to the show!
        HOST_B: Thanks! Great to be here.
    """
    script_path = Path(script_file)
    if not script_path.exists():
        print(f"Script file not found: {script_file}")
        sys.exit(1)

    lines = script_path.read_text().strip().splitlines()
    dialogue = []
    for line in lines:
        if ":" not in line:
            continue
        speaker, text = line.split(":", 1)
        speaker = speaker.strip().lower().replace(" ", "_")
        text = text.strip()
        if text:
            dialogue.append((speaker, text))

    if not dialogue:
        print("No dialogue found in script file.")
        sys.exit(1)

    model, tokenizer, device = load_model()

    segments = []
    silence = np.zeros(int(model.config.sampling_rate * 0.5))

    for i, (speaker, text) in enumerate(dialogue):
        voice_desc = VOICES.get(speaker, VOICES["host_a"])
        print(f"[{i+1}/{len(dialogue)}] {speaker}: {text[:50]}...")
        audio, sr = generate_speech(model, tokenizer, text, voice_desc, device)
        segments.append(audio)
        segments.append(silence)

    full_audio = np.concatenate(segments)
    sf.write(output, full_audio, model.config.sampling_rate)
    print(f"Podcast saved to {output}")


def main():
    parser = argparse.ArgumentParser(description="Podcast Playground - Free local TTS")
    subparsers = parser.add_subparsers(dest="command")

    single = subparsers.add_parser("say", help="Generate speech from text")
    single.add_argument("text", help="Text to speak")
    single.add_argument("--voice", default="narrator", help=f"Voice preset or custom description. Presets: {list(VOICES.keys())}")
    single.add_argument("--output", "-o", default="output.wav", help="Output file path")

    podcast = subparsers.add_parser("podcast", help="Generate podcast from script file")
    podcast.add_argument("script", help="Path to script file")
    podcast.add_argument("--output", "-o", default="podcast.wav", help="Output file path")

    args = parser.parse_args()

    if args.command == "say":
        generate_single(args.text, args.voice, args.output)
    elif args.command == "podcast":
        generate_podcast(args.script, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
