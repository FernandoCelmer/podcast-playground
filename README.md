# Podcast Playground

Generate podcast-style audio locally with multiple free TTS engines. No API keys required. Inspired by Google NotebookLM.

## Engines

| Engine | Cost | GPU | Quality | Install |
|--------|------|-----|---------|---------|
| edge | Free (cloud) | No | Good | `pip install -e ".[edge]"` |
| bark | Free (local) | Yes (4-6 GB) | Excellent | `pip install -e ".[bark]"` |
| parler | Free (local) | Optional | Very good | `pip install -e ".[parler]"` |

## Setup

```bash
python -m venv venv
source venv/bin/activate

pip install -e ".[edge]"
```

For the full pipeline (source text to script to audio), install Ollama:

```bash
ollama pull llama3
```

## Usage

### CLI

```bash
python -m podcast_playground say "Hello world" --engine edge

python -m podcast_playground script examples/sample_script.txt --engine edge

python -m podcast_playground generate examples/sample_source.txt --engine edge --model llama3
```

### Python API

```python
from podcast_playground import PodcastGenerator, create_engine

engine = create_engine("edge")
gen = PodcastGenerator(engine=engine)

gen.say("Hello world", voice="narrator")

gen.from_script("examples/sample_script.txt")

gen.from_source("examples/sample_source.txt", model="llama3")
```

## Voice Presets

| Preset | Description |
|--------|-------------|
| host_a | Male, warm, conversational |
| host_b | Female, energetic, friendly |
| narrator | Male, calm, professional |
| casual | Female, relaxed, natural |

## Script Format

```
HOST_A: Welcome to the show!
HOST_B: Thanks for having me.
HOST_A: Let's talk about AI.
```

## Project Structure

```
src/podcast_playground/
    __init__.py
    __main__.py
    core.py
    script.py
    engines/
        __init__.py
        base.py
        edge.py
        bark.py
        parler.py
```

## Requirements

- Python 3.10+
- 2 GB disk (model download on first run)
- GPU optional (works on CPU and Apple Silicon MPS)

## License

MIT
