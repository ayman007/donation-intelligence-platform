import math
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from dip_simulator.catalog import (
    AMOUNT_PARAMS,
    APP_VERSIONS,
    DONOR_CITIES,
    DONOR_COUNTRIES,
    HOUR_WEIGHTS,
    SIGNUP_CHANNELS,
    VIEW_SOURCES,
)
from dip_simulator.config import SimConfig
from dip_simulator.generators import (
    _weighted,
    generate_campaigns,
    generate_donors,
    generate_popularity,
)
from dip_simulator.ids import IdFactory
from dip_simulator.models import Campaign, Donor, Payment

UTC = timezone.utc


@dataclass
class SimResult:
    campaigns: list
    donors: list  # initial donors plus new sign-ups, sorted by created_at
    new_donors: list
    payments: list
    events: list  # dicts, sorted by event_ts


def _amount_minor(rng: random.Random, currency: str) -> int:
    median, low, high = AMOUNT_PARAMS[currency]
    major = rng.lognormvariate(math.log(median), 0.9)
    major = int(round(min(max(major, low), high)))
    return major * 100


def _second_of_day(rng: random.Random) -> int:
    hour = rng.choices(range(24), weights=HOUR_WEIGHTS, k=1)[0]
    return hour * 3600 + rng.randrange(3600)


def _new_donor(rng: random.Random, ids: IdFactory, created_at: datetime) -> Donor:
    country = _weighted(rng, DONOR_COUNTRIES)
    return Donor(
        donor_id=ids.new_id(),
        created_at=created_at,
        country=country,
        city=rng.choice(DONOR_CITIES[country]),
        signup_channel=_weighted(rng, SIGNUP_CHANNELS),
    )


def _run_session(
    cfg: SimConfig,
    rng: random.Random,
    ids: IdFactory,
    donor: Donor,
    platform: str,
    version: str,
    start: datetime,
    active: list,
    weights: list,
    events: list,
    payments: list,
) -> None:
    session_id = ids.new_id()

    def emit(event_type: str, ts: datetime, **extra) -> None:
        events.append(
            {
                "event_id": ids.new_id(),
                "event_type": event_type,
                "event_ts": ts.isoformat(),
                "user_id": donor.donor_id,
                "session_id": session_id,
                "platform": platform,
                "app_version": version,
                **extra,
            }
        )

    t = start
    emit("app_open", t, device_country=donor.country)

    n_views = max(1, min(12, round(rng.gauss(cfg.views_per_session_mean, 2.5))))
    for _ in range(n_views):
        t += timedelta(seconds=rng.randint(5, 60))
        if t.date() != start.date():
            break  # sessions end at midnight UTC
        campaign = rng.choices(active, weights=weights, k=1)[0]
        emit(
            "campaign_view",
            t,
            campaign_id=campaign.campaign_id,
            position_in_feed=rng.randint(1, 10),
            source=_weighted(rng, VIEW_SOURCES),
        )

        if rng.random() >= cfg.view_to_start_rate:
            continue

        t += timedelta(seconds=rng.randint(3, 20))
        amount = _amount_minor(rng, campaign.currency)
        emit(
            "donation_started",
            t,
            campaign_id=campaign.campaign_id,
            amount_minor=amount,
            currency=campaign.currency,
        )

        outcome = rng.random()
        if outcome < cfg.start_to_complete_rate:
            t += timedelta(seconds=rng.randint(10, 90))
            payment = Payment(
                payment_id=ids.new_id(),
                donor_id=donor.donor_id,
                campaign_id=campaign.campaign_id,
                amount_minor=amount,
                currency=campaign.currency,
                status="succeeded",
                created_at=t,
            )
            payments.append(payment)
            emit(
                "donation_completed",
                t,
                campaign_id=campaign.campaign_id,
                payment_id=payment.payment_id,
                amount_minor=amount,
                currency=campaign.currency,
            )
        elif outcome < cfg.start_to_complete_rate + cfg.start_to_failed_rate:
            t += timedelta(seconds=rng.randint(10, 90))
            payments.append(
                Payment(
                    payment_id=ids.new_id(),
                    donor_id=donor.donor_id,
                    campaign_id=campaign.campaign_id,
                    amount_minor=amount,
                    currency=campaign.currency,
                    status="failed",
                    created_at=t,
                )
            )
        # otherwise the donation is abandoned: no payment row, no completed event


def simulate(
    cfg: SimConfig,
    rng: random.Random,
    ids: IdFactory,
    campaigns: list,
    donors: list,
    popularity: dict,
) -> SimResult:
    events: list = []
    payments: list = []
    new_donors: list = []
    all_donors = list(donors)
    profiles: dict = {}

    def profile(donor: Donor):
        if donor.donor_id not in profiles:
            platform = "android" if rng.random() < cfg.android_share else "ios"
            profiles[donor.donor_id] = (platform, rng.choice(APP_VERSIONS))
        return profiles[donor.donor_id]

    first_day = cfg.as_of - timedelta(days=cfg.n_days - 1)
    for offset in range(cfg.n_days):
        day = first_day + timedelta(days=offset)
        active = [
            c for c in campaigns if c.status != "paused" and c.start_date <= day <= c.end_date
        ]
        if not active:
            continue
        weights = [popularity[c.campaign_id] for c in active]
        day_start = datetime(day.year, day.month, day.day, tzinfo=UTC)

        # New users sign up, then open the app at signup time
        for _ in range(cfg.new_users_per_day):
            created = day_start + timedelta(seconds=_second_of_day(rng))
            donor = _new_donor(rng, ids, created)
            new_donors.append(donor)
            all_donors.append(donor)
            platform, version = profile(donor)
            _run_session(
                cfg, rng, ids, donor, platform, version, created,
                active, weights, events, payments,
            )

        # Returning users: a share of everyone who signed up before today
        eligible = [d for d in all_donors if d.created_at.date() < day]
        returning = rng.sample(eligible, int(len(eligible) * cfg.daily_active_rate))
        for donor in returning:
            platform, version = profile(donor)
            n_sessions = rng.choices([1, 2, 3], weights=[0.6, 0.3, 0.1], k=1)[0]
            for _ in range(n_sessions):
                start = day_start + timedelta(seconds=_second_of_day(rng))
                _run_session(
                    cfg, rng, ids, donor, platform, version, start,
                    active, weights, events, payments,
                )

    events.sort(key=lambda e: e["event_ts"])
    payments.sort(key=lambda p: p.created_at)
    return SimResult(
        campaigns=campaigns,
        donors=sorted(all_donors, key=lambda d: d.created_at),
        new_donors=new_donors,
        payments=payments,
        events=events,
    )


def run_simulation(cfg: SimConfig) -> SimResult:
    rng = random.Random(cfg.seed)
    ids = IdFactory(rng)
    campaigns = generate_campaigns(cfg, rng, ids)
    donors = generate_donors(cfg, rng, ids)
    popularity = generate_popularity(campaigns, cfg, rng)
    return simulate(cfg, rng, ids, campaigns, donors, popularity)
