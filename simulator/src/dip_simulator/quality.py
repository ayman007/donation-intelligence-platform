import fastavro
from fastavro.validation import ValidationError

from dip_simulator.avro_io import check_contract, to_record


def validate_event(event: dict, schema) -> list[str]:
    """Return reason codes for everything wrong with an event ([] means valid).

    The same codes will later label records in the Dead Letter Queue.
    """
    reasons = []

    if not event.get("event_id"):
        reasons.append("empty_event_id")
    if not event.get("user_id"):
        reasons.append("missing_user_id")

    amount = event.get("amount_minor")
    if isinstance(amount, (int, float)) and not isinstance(amount, bool) and amount <= 0:
        reasons.append("non_positive_amount")

    try:
        check_contract(event)
    except (KeyError, ValueError):
        reasons.append("contract_violation")

    try:
        fastavro.validate(to_record(event), schema, raise_errors=True)
    except (KeyError, ValueError, TypeError, ValidationError):
        reasons.append("schema_violation")

    return reasons
