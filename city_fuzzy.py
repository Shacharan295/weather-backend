import csv
import re
from rapidfuzz import fuzz, process

# ------------------------------------------------------
# 🔹 LOAD CITIES FROM world-cities.csv
# ------------------------------------------------------
CITY_LIST = []

with open("world-cities.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row["name"].strip()
        if name and name not in CITY_LIST:
            CITY_LIST.append(name)

# ------------------------------------------------------
# 🔹 NORMALIZE USER INPUT (for typos + gibberish)
# ------------------------------------------------------
def clean_query(q: str) -> str:
    q = q.lower()
    q = re.sub(r"[^a-z ]", "", q)  # remove symbols
    q = re.sub(r"(.)\\1+", r"\\1", q)  # remove repeated letters: "nnneeew" → "new"
    return q.strip()


# ------------------------------------------------------
# 🔹 MAIN SUGGESTION FUNCTION
# ------------------------------------------------------
def get_city_suggestions(query: str, limit: int = 5):
    if not query:
        return []

    q = clean_query(query)

    # 1️⃣ PREFIX MATCH (autocomplete behavior)
    # Fast & strong for typing like "lon", "del", "san"
    prefix_matches = [
        city for city in CITY_LIST
        if city.lower().startswith(q)
    ]
    if prefix_matches:
        return prefix_matches[:limit]

    # 2️⃣ TOKEN-SORT FUZZY MATCH
    # Fixes swapped letters: "Lonodn" → "London"
    token_matches = process.extract(
        q,
        CITY_LIST,
        scorer=fuzz.token_sort_ratio,
        limit=limit
    )
    strong_token_results = [city for city, score, _ in token_matches if score >= 70]
    if strong_token_results:
        return strong_token_results[:limit]

    # 3️⃣ PARTIAL RATIO — catches missing letters: "nwrk" → "new york"
    partial_matches = process.extract(
        q,
        CITY_LIST,
        scorer=fuzz.partial_ratio,
        limit=limit
    )
    strong_partial = [city for city, score, _ in partial_matches if score >= 60]
    if strong_partial:
        return strong_partial[:limit]

    # 4️⃣ BEST GUESS MODE — for hard gibberish
    # Always return something instead of empty list
    best_guess = process.extract(q, CITY_LIST, limit=limit)
    return [city for city, score, _ in best_guess]
