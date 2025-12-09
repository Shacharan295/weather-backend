from rapidfuzz import process

# 🔹 You can expand this list later
CITY_LIST = [
    "London",
    "Los Angeles",
    "Lodz",
    "Lome",
    "Lahore",
    "Lisbon",
    "Lyon",
    "Lucknow",
    "Lille",
    "Lviv",
    "New York",
    "Paris",
    "Tokyo",
    "Dubai",
    "Delhi",
    "Mumbai",
    "Bengaluru",
    "Hyderabad",
    "Chennai",
    "Kolkata",
    "Singapore",
    "Hong Kong",
    "Bangkok",
    "Seoul",
    "San Francisco",
    "Chicago",
    "Berlin",
    "Rome",
    "Madrid",
    "Istanbul",
    "Riyadh",
    "Doha",
    "Sydney",
    "Melbourne",
    "Toronto",
    "Vancouver",
]

def get_city_suggestions(query: str, limit: int = 7):
    """Return best matching city names for a user’s input."""
    if not query:
        return []

    q = query.lower()

    # 1️⃣ Prefer cities that START with the typed text (for 'lo' → London, Los Angeles...)
    prefix_matches = [
        city for city in CITY_LIST
        if city.lower().startswith(q)
    ]

    if prefix_matches:
        return prefix_matches[:limit]

    # 2️⃣ If no good prefix match, fall back to fuzzy match (for typos like 'Lonodn')
    results = process.extract(query, CITY_LIST, limit=limit)
    return [city for city, score, _ in results if score >= 60]
