"""Engine registry with lazy loading."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from podcast_playground.engines.base import BaseEngine

ENGINES: dict[str, str] = {
    "edge": "podcast_playground.engines.edge.EdgeEngine",
    "bark": "podcast_playground.engines.bark.BarkEngine",
    "parler": (
        "podcast_playground.engines.parler.ParlerEngine"
    ),
}


def get_engine_class(name: str) -> type[BaseEngine]:
    """Load engine class by name."""
    from importlib import import_module

    dotted = ENGINES.get(name)
    if dotted is None:
        raise ValueError(
            f"Unknown engine '{name}'."
            f" Options: {list(ENGINES.keys())}"
        )

    module_path, class_name = dotted.rsplit(".", 1)
    module = import_module(module_path)
    return getattr(module, class_name)


__all__ = ["ENGINES", "get_engine_class"]
