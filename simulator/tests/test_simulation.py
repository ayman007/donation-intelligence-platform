from datetime import date
from functools import lru_cache

from dip_simulator.config import SimConfig
from dip_simulator.simulation import run_simulation

ENVELOPE = {"event_id", "event_type", "event_ts", "user_id", "session_id", "platform", "app_version"}
TYPES = {"app_open", "campaign_view", "donation_started", "donation_completed"}


@lru_cache(maxsize=None)
def sim(seed: int = 42):
    return run_simulation(SimConfig(seed=seed))


def of_type(result, event_type):
    return [e for e in result.events if e["event_type"] == event_type]


def test_same_seed_gives_identical_output():
    a, b = run_simulation(SimConfig(seed=5)), run_simulation(SimConfig(seed=5))
    assert a.events == b.events and a.payments == b.payments


def test_different_seed_gives_different_output():
    assert sim(42).events != sim(43).events


def test_events_have_envelope_and_known_types():
    for e in sim().events:
        assert ENVELOPE <= e.keys()
        assert e["event_type"] in TYPES


def test_event_ids_are_unique():
    ids = [e["event_id"] for e in sim().events]
    assert len(ids) == len(set(ids))


def test_events_are_sorted_by_time():
    stamps = [e["event_ts"] for e in sim().events]
    assert stamps == sorted(stamps)


def test_new_users_signed_up_every_day():
    cfg = SimConfig()
    assert len(sim().new_donors) == cfg.new_users_per_day * cfg.n_days


def test_funnel_rates_are_close_to_config():
    result = sim()
    views = len(of_type(result, "campaign_view"))
    started = len(of_type(result, "donation_started"))
    completed = len(of_type(result, "donation_completed"))
    assert 0.08 <= started / views <= 0.12
    assert 0.62 <= completed / started <= 0.78


def test_completed_events_match_succeeded_payments():
    result = sim()
    succeeded = {p.payment_id: p for p in result.payments if p.status == "succeeded"}
    completed = of_type(result, "donation_completed")
    assert {e["payment_id"] for e in completed} == set(succeeded)
    for e in completed:
        p = succeeded[e["payment_id"]]
        assert (e["campaign_id"], e["amount_minor"], e["currency"]) == (
            p.campaign_id, p.amount_minor, p.currency)
        assert e["user_id"] == p.donor_id


def test_failed_payments_have_no_completed_event():
    result = sim()
    completed_ids = {e["payment_id"] for e in of_type(result, "donation_completed")}
    failed = [p for p in result.payments if p.status == "failed"]
    assert failed
    assert not any(p.payment_id in completed_ids for p in failed)


def test_views_only_reference_live_campaigns():
    result = sim()
    by_id = {c.campaign_id: c for c in result.campaigns}
    for e in of_type(result, "campaign_view"):
        c = by_id[e["campaign_id"]]
        day = date.fromisoformat(e["event_ts"][:10])
        assert c.status != "paused"
        assert c.start_date <= day <= c.end_date


def test_money_is_integer_and_positive():
    for e in of_type(sim(), "donation_started"):
        assert isinstance(e["amount_minor"], int) and e["amount_minor"] > 0
    for p in sim().payments:
        assert isinstance(p.amount_minor, int) and p.amount_minor > 0


def test_views_are_skewed_toward_popular_campaigns():
    views = of_type(sim(), "campaign_view")
    counts = {}
    for e in views:
        counts[e["campaign_id"]] = counts.get(e["campaign_id"], 0) + 1
    top5 = sum(sorted(counts.values(), reverse=True)[:5])
    assert top5 / len(views) > 0.20
