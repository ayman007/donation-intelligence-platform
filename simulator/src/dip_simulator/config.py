from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class SimConfig:
    """Simulation parameters. Values mirror docs/data-contracts.md."""

    seed: int = 42
    as_of: date = date(2026, 11, 1)

    # Population
    n_campaigns: int = 50
    n_initial_donors: int = 5000
    new_users_per_day: int = 200
    android_share: float = 0.60

    # Sessions and funnel
    views_per_session_mean: float = 5.0
    view_to_start_rate: float = 0.10
    start_to_complete_rate: float = 0.70
    start_to_failed_rate: float = 0.05

    # Popularity skew: top 10% of campaigns get ~60% of views
    top_campaign_share: float = 0.10
    top_campaign_view_share: float = 0.60
