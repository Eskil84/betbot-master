from flask import Flask, render_template, request
import requests
from datetime import datetime, timezone
from collections import Counter

app = Flask(__name__)

API_KEY = "cfb1803716ad84725f69b7a7478e76e5"

SPORTS = [
    "soccer_uefa_europa_league",
    "soccer_germany_bundesliga",
    "soccer_france_ligue_one",
    "soccer_spain_la_liga",
    "soccer_italy_serie_a"
]

@app.route("/")
def home():
    selected_date = request.args.get("date")
    if selected_date:
        date_filter = datetime.fromisoformat(selected_date).date()
    else:
        date_filter = datetime.now(timezone.utc).date()

    tips = []
    for sport in SPORTS:
        url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?regions=eu&markets=h2h,totals&apiKey={API_KEY}&dateFormat=iso"
        response = requests.get(url)
        if response.status_code != 200:
            continue
        events = response.json()

        for event in events:
            start_time = datetime.fromisoformat(event["commence_time"].replace("Z", "+00:00"))
            if start_time.date() != date_filter:
                continue

            home = event.get("home_team")
            away = event.get("away_team")
            match = f"{home} vs {away}"

            h2h_counter = Counter()
            total_counter = Counter()
            avg_odds_h2h = {}
            avg_odds_total = {}

            for bookmaker in event.get("bookmakers", []):
                for market in bookmaker.get("markets", []):
                    if market["key"] == "h2h":
                        for outcome in market.get("outcomes", []):
                            h2h_counter[outcome["name"]] += 1
                            avg_odds_h2h.setdefault(outcome["name"], []).append(outcome["price"])
                    elif market["key"] == "totals":
                        for outcome in market.get("outcomes", []):
                            total_counter[outcome["name"]] += 1
                            avg_odds_total.setdefault(outcome["name"], []).append(outcome["price"])

            # 1. Ésszerű Tipp
            if h2h_counter:
                top_h2h = h2h_counter.most_common(1)[0][0]
                odds_list = avg_odds_h2h.get(top_h2h, [])
                avg_odds = round(sum(odds_list) / len(odds_list), 2) if odds_list else None
                tips.append({
                    "match": match,
                    "sport": event.get("sport_title", sport),
                    "time": start_time.strftime("%Y-%m-%d %H:%M"),
                    "prediction": top_h2h,
                    "avg_odds": avg_odds,
                    "type": "reasonable"
                })

            # 2. Over/Under Tipp (ha magas odds)
            for outcome, count in total_counter.items():
                if count >= 2:
                    odds_list = avg_odds_total.get(outcome, [])
                    avg_odds = round(sum(odds_list) / len(odds_list), 2) if odds_list else None
                    if avg_odds and avg_odds >= 2.5:
                        tips.append({
                            "match": match,
                            "sport": event.get("sport_title", sport),
                            "time": start_time.strftime("%Y-%m-%d %H:%M"),
                            "prediction": outcome,
                            "avg_odds": avg_odds,
                            "type": "special"
                        })

    smart_tips = [tip for tip in tips if tip["type"] == "reasonable"]
    special_tips = [tip for tip in tips if tip["type"] == "special"]

    return render_template("index.html", smart_tips=smart_tips, special_tips=special_tips, selected_date=date_filter.isoformat())

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
