"""CLI entrypoint."""

import argparse

from podcast_playground.core import (
    PodcastGenerator,
    create_engine,
)
from podcast_playground.engines import ENGINES


def main() -> None:
    """Parse args and run podcast generation."""
    parser = argparse.ArgumentParser(
        prog="podcast-playground",
        description=(
            "Generate podcast-style audio"
            " with multiple TTS engines."
        ),
    )
    parser.add_argument(
        "--engine",
        choices=list(ENGINES.keys()),
        default="edge",
        help=(
            "TTS engine: edge (free, cloud),"
            " bark (local, GPU),"
            " parler (local, GPU)"
        ),
    )
    subparsers = parser.add_subparsers(dest="command")

    say_cmd = subparsers.add_parser(
        "say",
        help="Generate speech from text",
    )
    say_cmd.add_argument("text", help="Text to speak")
    say_cmd.add_argument(
        "--voice",
        default="narrator",
        help=(
            "Voice preset:"
            " host_a, host_b, narrator, casual"
        ),
    )
    say_cmd.add_argument(
        "--output",
        "-o",
        default="output.wav",
    )

    script_cmd = subparsers.add_parser(
        "script",
        help="Generate podcast from script file",
    )
    script_cmd.add_argument(
        "file",
        help="Path to script file (HOST_A: text format)",
    )
    script_cmd.add_argument(
        "--output",
        "-o",
        default="podcast.wav",
    )

    gen_cmd = subparsers.add_parser(
        "generate",
        help="Source text -> LLM script -> podcast audio",
    )
    gen_cmd.add_argument("file", help="Source text file")
    gen_cmd.add_argument(
        "--model",
        default="llama3",
        help="Ollama model for script generation",
    )
    gen_cmd.add_argument(
        "--output",
        "-o",
        default="podcast.wav",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    engine = create_engine(args.engine)
    gen = PodcastGenerator(engine=engine)

    if args.command == "say":
        gen.say(args.text, args.voice, args.output)
    elif args.command == "script":
        gen.from_script(args.file, args.output)
    elif args.command == "generate":
        gen.from_source(
            args.file,
            args.output,
            args.model,
        )


if __name__ == "__main__":
    main()
