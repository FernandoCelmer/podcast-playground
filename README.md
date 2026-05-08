# Podcast Playground

Generate podcast-style audio locally with [Parler-TTS](https://github.com/hugging-face/parler-tts). 100% free, no API keys needed.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Single voice

```bash
python generate.py say "Hello, this is a test" --voice narrator
```

### Podcast from script

```bash
python generate.py podcast examples/sample_podcast.txt -o my_podcast.wav
```

### Voice presets

| Preset | Description |
|--------|-------------|
| `host_a` | Male, warm, conversational |
| `host_b` | Female, energetic, friendly |
| `narrator` | Male, calm, professional |
| `casual` | Female, relaxed, natural |

Custom voice description:

```bash
python generate.py say "Hello world" --voice "A deep male voice speaking slowly with a British accent"
```

## Script format

```
HOST_A: Welcome to the show!
HOST_B: Thanks for having me.
HOST_A: Let's talk about AI.
```

## Requirements

- Python 3.10+
- ~2 GB disk (model download on first run)
- GPU optional (works on CPU/MPS, faster with CUDA)
