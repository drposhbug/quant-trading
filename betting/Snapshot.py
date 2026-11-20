import requests
import pandas as pd
import json
import time
import os

def fetch_open_sports_markets():
    rows = []
    offset = 0
    for _ in range(20):
        params = {"limit": 100, "offset": offset, "closed": "false"}
        r = requests.get("https://gamma-api.polymarket.com/markets", params=params)
        batch = r.json()
        if not batch:
            break
        rows.extend(batch)
        offset += 100
        time.sleep(0.2)
    df = pd.DataFrame(rows)

    # Strict: must mention an actual league/sport name, not just "win the..."
    sports_pattern = r"\b(NBA|NFL|NHL|MLB|UFC|MLS|WNBA|World Cup|Premier League|UEFA|Champions League|Europa League|La Liga|Bundesliga|Serie A|Olympics)\b"
    return df[df["question"].str.contains(sports_pattern, case=False, na=False, regex=True)]

def save_price_snapshot(df, filename="price_snapshots.csv"):
    if os.path.exists(filename):
        df.to_csv(filename, mode="a", header=False, index=False)
    else:
        df.to_csv(filename, mode="w", header=True, index=False)
    print(f"Saved {len(df)} new rows at {time.ctime()}")

def main():
    open_sports_df = fetch_open_sports_markets()
    snapshot_rows = []
    for _, m in open_sports_df.head(50).iterrows():
        try:
            token_ids = json.loads(m["clobTokenIds"])
            r = requests.get("https://clob.polymarket.com/prices-history", params={
                "market": token_ids[0], "interval": "1h", "fidelity": 5
            })
            data = r.json().get("history", [])
            if data:
                latest = data[-1]
                snapshot_rows.append({
                    "question": m["question"],
                    "token_id": token_ids[0],
                    "price": latest["p"],
                    "pulled_at": int(time.time())
                })
        except Exception:
            pass
        time.sleep(0.1)

    snapshot_df = pd.DataFrame(snapshot_rows)
    save_price_snapshot(snapshot_df)

if __name__ == "__main__":
    main()