import math
import random
from datetime import datetime, timedelta, timezone

from dip_simulator.catalog import (
    CAMPAIGN_COUNTRIES,
    CATEGORIES,
    CURRENCIES,
    DONOR_CITIES,
    DONOR_COUNTRIES,
    PLACES,
    SIGNUP_CHANNELS,
)
from dip_simulator.config import SimConfig
from dip_simulator.ids import IdFactory
from dip_simulator.models import Campaign, Donor


def _weighted(rng: random.Random, options: dict[str, float]) -> str:
    return rng.choices(list(options), weights=list(options.values()), k=1)[0]


def generate_campaigns(cfg: SimConfig, rng: random.Random, ids: IdFactory) -> list[Campaign]:
    campaigns = []
    for _ in range(cfg.n_campaigns):
        category = rng.choice(sorted(CATEGORIES))
        country = _weighted(rng, CAMPAIGN_COUNTRIES)
        place = rng.choice(PLACES[country])
        spec = CATEGORIES[category]

        n = rng.choice([20, 50, 100, 200])
        title = rng.choice(spec["titles"]).format(n=n, place=place)
        need = rng.choice(spec["needs"])
        description = (
            f"{title}. Your donation helps provide {need} in {place}. "
            f"Every contribution, large or small, brings this campaign closer to its goal."
        )

        age_days = rng.randint(0, 45)
        duration_days = rng.randint(14, 60)
        start = cfg.as_of - timedelta(days=age_days)
        end = start + timedelta(days=duration_days)

        goal_major = max(5000, int(round(rng.lognormvariate(math.log(30000), 0.6), -3)))

        if end < cfg.as_of:
            status = "completed"
        elif rng.random() < 0.03:
            status = "paused"
        else:
            status = "active"

        campaigns.append(
            Campaign(
                campaign_id=ids.new_id(),
                title=title,
                description=description,
                category=category,
                country=country,
                goal_amount_minor=goal_major * 100,
                currency=_weighted(rng, CURRENCIES),
                start_date=start,
                end_date=end,
                status=status,
            )
        )
    return campaigns


def generate_popularity(
    campaigns: list[Campaign], cfg: SimConfig, rng: random.Random
) -> dict[str, float]:
    """Skewed view weights: the top share of campaigns get most of the attention."""
    n = len(campaigns)
    k = max(1, math.ceil(n * cfg.top_campaign_share))
    shuffled = list(campaigns)
    rng.shuffle(shuffled)

    weights = {}
    for i, campaign in enumerate(shuffled):
        if i < k:
            base = cfg.top_campaign_view_share / k
        else:
            base = (1 - cfg.top_campaign_view_share) / max(n - k, 1)
        weights[campaign.campaign_id] = base * rng.uniform(0.8, 1.2)

    total = sum(weights.values())
    return {cid: w / total for cid, w in weights.items()}


def generate_donors(cfg: SimConfig, rng: random.Random, ids: IdFactory) -> list[Donor]:
    as_of_dt = datetime(cfg.as_of.year, cfg.as_of.month, cfg.as_of.day, tzinfo=timezone.utc)
    donors = []
    for _ in range(cfg.n_initial_donors):
        country = _weighted(rng, DONOR_COUNTRIES)
        donors.append(
            Donor(
                donor_id=ids.new_id(),
                created_at=as_of_dt - timedelta(seconds=rng.randrange(365 * 86400)),
                country=country,
                city=rng.choice(DONOR_CITIES[country]),
                signup_channel=_weighted(rng, SIGNUP_CHANNELS),
            )
        )
    donors.sort(key=lambda d: d.created_at)
    return donors
