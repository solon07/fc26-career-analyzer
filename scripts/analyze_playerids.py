import json
from collections import Counter

# Load the parsed data
with open("parser/output/test_parse.json", encoding="utf-8") as f:
    data = json.load(f)

players = data["players"]

# Check playerid distribution
print("=" * 60)
print("PLAYER ID ANALYSIS")
print("=" * 60)
print()

ids = [p.get("playerid") for p in players]
counter = Counter(ids)

print("Player ID distribution:")
for pid, count in counter.most_common(10):
    print(f"  ID {pid}: {count:,} players")
print()

# Check if there's any other field that could be a unique ID
print("Checking for potential unique ID fields...")
print()

# Sample first player to see all fields
sample_player = players[0]
potential_id_fields = [
    k for k in sample_player.keys() if "id" in k.lower() or k in ["index", "row"]
]

print(f"Potential ID fields: {potential_id_fields}")
print()

# Check each potential field for uniqueness
for field in potential_id_fields:
    values = [p.get(field) for p in players if p.get(field) is not None]
    if values:
        unique_count = len(set(values))
        print(
            f"  {field}: {unique_count:,} unique values out of {len(values):,} non-null values"
        )
print()

# Generate suggestion
print("=" * 60)
print("RECOMMENDATION")
print("=" * 60)
print()
print("The 'playerid' field in the parser output contains duplicate values.")
print("This appears to be a limitation of the FIFA Career Save Parser library")
print("when used with FC 26 save files in FIFA 21 mode.")
print()
print("SOLUTION: Use array index as the unique player ID instead of 'playerid'.")
print("Each player's position in the array can serve as a surrogate key.")
