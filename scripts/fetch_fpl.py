import requests
import json
import os
from datetime import datetime

MANAGER_1_ID = os.environ.get("MANAGER_1_ID", "6819004")
MANAGER_2_ID = os.environ.get("MANAGER_2_ID", "6839236")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_manager_info(manager_id):
    url = f"https://fantasy.premierleague.com/api/entry/{manager_id}/"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def fetch_manager_history(manager_id):
    url = f"https://fantasy.premierleague.com/api/entry/{manager_id}/history/"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def main():
    print(f"Fetching data for Manager 1 (ID: {MANAGER_1_ID})...")
    m1_info = fetch_manager_info(MANAGER_1_ID)
    m1_history = fetch_manager_history(MANAGER_1_ID)

    print(f"Fetching data for Manager 2 (ID: {MANAGER_2_ID})...")
    m2_info = fetch_manager_info(MANAGER_2_ID)
    m2_history = fetch_manager_history(MANAGER_2_ID)

    m1_gws = {gw["event"]: gw for gw in m1_history["current"]}
    m2_gws = {gw["event"]: gw for gw in m2_history["current"]}

    # League started after GW1 â subtract GW1 points from all cumulative totals
    m1_gw1 = m1_gws.get(1, {}).get("points", 0)
    m2_gw1 = m2_gws.get(1, {}).get("points", 0)

    all_gws = sorted(gw for gw in set(list(m1_gws.keys()) + list(m2_gws.keys())) if gw > 1)

    gameweeks = []
    for gw in all_gws:
        m1_data = m1_gws.get(gw, {})
        m2_data = m2_gws.get(gw, {})

        m1_total = m1_data.get("total_points", 0) - m1_gw1
        m2_total = m2_data.get("total_points", 0) - m2_gw1

        gameweeks.append({
            "gameweek": gw,
            "manager1_gw_points": m1_data.get("points", 0),
            "manager1_total": m1_total,
            "manager2_gw_points": m2_data.get("points", 0),
            "manager2_total": m2_total,
            "gap": m1_total - m2_total,
        })

    output = {
        "manager1": {
            "id": MANAGER_1_ID,
            "name": f"{m1_info.get('player_first_name', '')} {m1_info.get('player_last_name', '')}".strip(),
            "team_name": m1_info.get("name", "Manager 1"),
            "overall_rank": m1_info.get("summary_overall_rank"),
            "total_points": (m1_info.get("summary_overall_points") or 0) - m1_gw1,
        },
        "manager2": {
            "id": MANAGER_2_ID,
            "name": f"{m2_info.get('player_first_name', '')} {m2_info.get('player_last_name', '')}".strip(),
            "team_name": m2_info.get("name", "Manager 2"),
            "overall_rank": m2_info.get("summary_overall_rank"),
            "total_points": (m2_info.get("summary_overall_points") or 0) - m2_gw1,
        },
        "gameweeks": gameweeks,
        "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    os.makedirs("data", exist_ok=True)
    with open("data/fpl_data.json", "w") as f:
        json.dump(output, f, indent=2)

    print("â Data saved to data/fpl_data.json")

    if gameweeks:
        latest = gameweeks[-1]
        gap = latest["gap"]
        leader = output["manager1"]["team_name"] if gap > 0 else output["manager2"]["team_name"]
        print(f"   GW{latest['gameweek']} gap: {abs(gap)} pts â {leader} leads")

if __name__ == "__main__":
    main()
