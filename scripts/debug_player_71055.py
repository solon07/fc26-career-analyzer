import json


def debug():
    with open("parser/output/test_parse.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Flatten tables
    tables = {}
    if isinstance(data, list):
        for db in data:
            for name, rows in db.items():
                tables[name] = rows
    else:
        tables = data

    dcnames = tables.get("dcplayernames", [])
    name_map = {r["nameid"]: r["name"] for r in dcnames}

    print(f"Total names in dcplayernames: {len(name_map)}")
    print(f"Sample names: {list(name_map.items())[:5]}")

    # Check youth players
    youth = tables.get("career_youthplayers", [])
    print(f"Total youth players: {len(youth)}")

    if youth:
        yp = youth[0]
        y_fid = yp.get("firstnameid")
        y_lid = yp.get("lastnameid")
        print(
            f"Youth Player {yp.get('playerid')}: Firstname ID {y_fid} -> {name_map.get(y_fid, 'NOT FOUND')}"
        )
        print(
            f"Youth Player {yp.get('playerid')}: Lastname ID {y_lid} -> {name_map.get(y_lid, 'NOT FOUND')}"
        )

    # Check matches in players table
    players = tables.get("players", [])
    matches = 0
    for p in players[:100]:
        if p.get("firstnameid") in name_map:
            matches += 1

    print(f"Matches in first 100 players: {matches}")


if __name__ == "__main__":
    debug()
