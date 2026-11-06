import random
import uuid


class IdFactory:
    """Generates UUIDs from a seeded RNG, so the same seed gives the same IDs."""

    def __init__(self, rng: random.Random) -> None:
        self._rng = rng

    def new_id(self) -> str:
        return str(uuid.UUID(int=self._rng.getrandbits(128), version=4))
