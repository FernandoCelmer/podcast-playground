from podcast_playground.engines.bark import BarkEngine
from podcast_playground.engines.base import BaseEngine
from podcast_playground.engines.edge import EdgeEngine
from podcast_playground.engines.parler import ParlerEngine

ENGINES: dict[str, type[BaseEngine]] = {
    "edge": EdgeEngine,
    "bark": BarkEngine,
    "parler": ParlerEngine,
}

__all__ = [
    "ENGINES",
    "BarkEngine",
    "BaseEngine",
    "EdgeEngine",
    "ParlerEngine",
]
