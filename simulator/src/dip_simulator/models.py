from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class Campaign:
    campaign_id: str
    title: str
    description: str
    category: str
    country: str
    goal_amount_minor: int
    currency: str
    start_date: date
    end_date: date
    status: str


@dataclass(frozen=True)
class Donor:
    donor_id: str
    created_at: datetime
    country: str
    city: str
    signup_channel: str


@dataclass(frozen=True)
class Payment:
    payment_id: str
    donor_id: str
    campaign_id: str
    amount_minor: int
    currency: str
    status: str
    created_at: datetime
