import random

from dip_simulator.ids import IdFactory


def make_ids(seed: int, n: int = 5) -> list[str]:
    factory = IdFactory(random.Random(seed))
    return [factory.new_id() for _ in range(n)]


def test_same_seed_gives_same_ids():
    assert make_ids(42) == make_ids(42)


def test_different_seed_gives_different_ids():
    assert make_ids(42) != make_ids(43)


def test_ids_are_unique():
    ids = make_ids(1, n=1000)
    assert len(set(ids)) == 1000
