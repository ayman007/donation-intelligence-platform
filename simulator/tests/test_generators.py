import random
from datetime import datetime, timezone

from dip_simulator.catalog import DONOR_CITIES, DONOR_COUNTRIES
from dip_simulator.config import SimConfig
from dip_simulator.generators import generate_campaigns, generate_donors, generate_popularity
from dip_simulator.ids import IdFactory


def build(seed: int = 42):
    cfg = SimConfig(seed=seed)
    rng = random.Random(seed)
    ids = IdFactory(rng)
    campaigns = generate_campaigns(cfg, rng, ids)
    donors = generate_donors(cfg, rng, ids)
    popularity = generate_popularity(campaigns, cfg, rng)
    return cfg, campaigns, donors, popularity


def test_same_seed_gives_identical_data():
    _, c1, d1, p1 = build(42)
    _, c2, d2, p2 = build(42)
    assert c1 == c2 and d1 == d2 and p1 == p2


def test_different_seed_gives_different_data():
    assert build(42)[1] != build(43)[1]


def test_counts_match_config():
    cfg, campaigns, donors, _ = build()
    assert len(campaigns) == cfg.n_campaigns
    assert len(donors) == cfg.n_initial_donors


def test_campaign_dates_and_status_are_consistent():
    cfg, campaigns, _, _ = build()
    for c in campaigns:
        assert c.end_date >= c.start_date
        assert c.goal_amount_minor > 0
        assert c.status in {"active", "completed", "paused"}
        if c.status == "completed":
            assert c.end_date < cfg.as_of
        else:
            assert c.end_date >= cfg.as_of


def test_most_campaigns_are_active():
    _, campaigns, _, _ = build()
    active = sum(c.status == "active" for c in campaigns)
    assert 25 <= active <= 48


def test_ids_are_unique():
    _, campaigns, donors, _ = build()
    ids = [c.campaign_id for c in campaigns] + [d.donor_id for d in donors]
    assert len(ids) == len(set(ids))


def test_donors_are_valid():
    cfg, _, donors, _ = build()
    as_of_dt = datetime(cfg.as_of.year, cfg.as_of.month, cfg.as_of.day, tzinfo=timezone.utc)
    for d in donors:
        assert d.created_at <= as_of_dt
        assert d.country in DONOR_COUNTRIES
        assert d.city in DONOR_CITIES[d.country]


def test_popularity_is_skewed():
    _, campaigns, _, popularity = build()
    assert abs(sum(popularity.values()) - 1.0) < 1e-9
    top = sorted(popularity.values(), reverse=True)[: len(campaigns) // 10]
    assert 0.5 <= sum(top) <= 0.7
