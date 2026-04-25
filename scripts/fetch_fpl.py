import json
import os
import time
from urllib.request import urlopen

MANAGERS = [
    {"id": "6819004",  "nickname": "Sindri"},
    {"id": "6839236",  "nickname": "Helgi"},
    {"id": "4470214",  "nickname": "Emmi"},
    {"id": "6590777",  "nickname": "Olli"},
    {"id": "9072831",  "nickname": "Högni"},
    {"id": "8305956",  "nickname": "Tommi"},
    {"id": "10576515", "nickname": "Maggi"},
]

BASE = "https://fantasy.premierleague.com/api"
HEADERS = [("User-Agent", "Mozilla/5.0")]


def fetch(url):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def main():
    manager_data = []

    for m in MANAGERS:
        mid = m["id"]
        print(f"Fetching {m['nickname']} (id={mid})…")
        info = fetch(f"{BASE}/entry/{mid}/")
        history = fetch(f"{BASE}/entry/{mid}/history/")

        gws = {gw["event"]: gw for gw in history["current"]}

        # Baseline = everything before GW2 (league started GW2)
        # More reliable than reading GW1 directly (phantom entries exist for late registrations)
        gw2 = gws.get(2, {})
        baseline = gw2.get("total_points", 0) - gw2.get("points", 0)

        manager_data.append({
            "id": mid,
            "nickname": m["nickname"],
            "team_name": info.get("name", "Unknown"),
            "player_name": f"{info.get('player_first_name', '')} {info.get('player_last_name', '')}".strip(),
            "summary_total": (info.get("summary_overall_points") or 0) - baseline,
            "gws": gws,
            "baseline": baseline,
        })
        time.sleep(0.5)

    # All GWs played (GW2+)
    all_gw_nums = sorted(set(
        gw for m in manager_data for gw in m["gws"] if gw > 1
    ))

    gameweeks = []
    for gw_num in all_gw_nums:
        standings = []
        for m in manager_data:
            gw_data = m["gws"].get(gw_num, {})
            total = gw_data.get("total_points", 0) - m["baseline"]
            standings.append({
                "id": m["id"],
                "nickname": m["nickname"],
                "team_name": m["team_name"],
                "gw_points": gw_data.get("points", 0),
                "total_points": total,
            })

        standings.sort(key=lambda x: x["total_points"], reverse=True)

        gap = (
            standings[0]["total_points"] - standings[1]["total_points"]
            if len(standings) >= 2
            else 0
        )

        gameweeks.append({
            "gameweek": gw_num,
            "standings": standings,
            "leader_id": standings[0]["id"] if standings else None,
            "leader_nickname": standings[0]["nickname"] if standings else None,
            "second_nickname": standings[1]["nickname"] if len(standings) >= 2 else None,
            "gap": gap,
        })

    # Current overall standings (from API summary)
    current_standings = sorted(
        [
            {
                "id": m["id"],
                "nickname": m["nickname"],
                "team_name": m["team_name"],
                "player_name": m["player_name"],
                "total_points": m["summary_total"],
            }
            for m in manager_data
        ],
        key=lambda x: x["total_points"],
        reverse=True,
    )

    output = {
        "managers": current_standings,
        "gameweeks": gameweeks,
        "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    os.makedirs("data", exist_ok=True)
    with open("data/fpl_data.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\n✅ Done! Current standings:")
    for i, m in enumerate(current_standings, 1):
        print(f"  {i}. {m['nickname']} ({m['team_name']}): {m['total_points']} pts")


if __name__ == "__main__":
    main()
