"""Static lookup data for the simulator."""

CATEGORIES = {
    "education": {
        "titles": [
            "School supplies for {n} children in {place}",
            "Scholarships for {n} students in {place}",
            "A new classroom in {place}",
        ],
        "needs": [
            "books, uniforms and stationery",
            "tuition for a full school year",
            "a safe and well-equipped learning space",
        ],
    },
    "health": {
        "titles": [
            "Medical care for {n} families in {place}",
            "A mobile clinic for {place}",
            "Life-saving surgeries in {place}",
        ],
        "needs": [
            "essential medicines and check-ups",
            "equipment and trained medical staff",
            "treatment for patients who cannot afford it",
        ],
    },
    "relief": {
        "titles": [
            "Food packages for {n} families in {place}",
            "Winter relief for {n} households in {place}",
            "Emergency aid for {place}",
        ],
        "needs": [
            "food, blankets and basic supplies",
            "shelter and warm clothing",
            "urgent help for families in crisis",
        ],
    },
    "water": {
        "titles": [
            "Clean water wells for {place}",
            "Water filters for {n} homes in {place}",
        ],
        "needs": [
            "access to safe drinking water",
            "pumps, filters and maintenance",
        ],
    },
    "orphan_care": {
        "titles": [
            "Sponsor {n} orphans in {place}",
            "Care and education for orphans in {place}",
        ],
        "needs": [
            "monthly care, schooling and healthcare",
            "a stable home and mentoring",
        ],
    },
}

CAMPAIGN_COUNTRIES = {"AE": 0.30, "EG": 0.30, "JO": 0.15, "PK": 0.15, "BD": 0.10}

PLACES = {
    "AE": ["Sharjah", "Ajman", "Fujairah"],
    "EG": ["Upper Egypt", "Aswan", "Alexandria"],
    "JO": ["Amman", "Zarqa", "Irbid"],
    "PK": ["Sindh", "Punjab", "Peshawar"],
    "BD": ["Dhaka", "Sylhet", "Khulna"],
}

DONOR_COUNTRIES = {"AE": 0.45, "EG": 0.40, "SA": 0.10, "JO": 0.05}

DONOR_CITIES = {
    "AE": ["Dubai", "Abu Dhabi", "Sharjah"],
    "EG": ["Cairo", "Alexandria", "Giza"],
    "SA": ["Riyadh", "Jeddah"],
    "JO": ["Amman"],
}

SIGNUP_CHANNELS = {"organic": 0.60, "referral": 0.25, "ad": 0.15}

CURRENCIES = {"AED": 0.80, "USD": 0.20}
