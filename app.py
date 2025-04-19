from flask import Flask, render_template, request
import requests
from datetime import datetime, timezone
from collections import Counter
import os

app = Flask(__name__)

API_KEY = "cfb1803716ad84725f69b7a7478e76e5"  # Cseréld ki a saját kulcsodra, ha kell

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
        url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?regions=eu&markets=h2h&apiKey={API_KEY}&dateFormat=iso"
        response = requests.get(url)

        if response.status_code != 200:
            print("API hiba:", response.text)
            continue

        try:
            events = response.json()
        except Exception as e:
            print("JSON parse hiba:", e)
            continue

        for event in events:
            try:
                if not isinstance(event, dict):
                    continue

                start_time = datetime.fromisoformat(event["commence_time"].replace("Z", "+00:00"))
                if start_time.date() != date_filter:
                    continue

                home = event.get("home_team")
                away = event.get("away_team")
                match = f"{home} vs {away}"

                # Tippgyűjtés
                all_outcomes = []
                odds_by_tip = {}

                for bookmaker in event.get("bookmakers", []):
                    for market in bookmaker.get("markets", []):
                        if market["key"] != "h2h":
                            continue
                        for outcome in market.get("outcomes", []):
                            tip = outcome["name"]
                            price = outcome["price"]
                            all_outcomes.append(tip)
                            odds_by_tip.setdefault(tip, []).append(price)

                if not all_outcomes:
                    continue

                most_common_tip = Counter(all_outcomes).most_common(1)[0][0]
                avg_odds_list = odds_by_tip.get(most_common_tip, [])
                avg_odds = round(sum(avg_odds_list) / len(avg_odds_list), 2) if avg_odds_list else None

                link = f"https://www.superbet.ro/pariuri-sportive/cauta/{match.lower().replace(' ', '%20')}"

                tips.append({
                    "match": match,
                    "sport": event.get("sport_title", sport),
                    "time": start_time.strftime("%Y-%m-%d %H:%M"),
                    "prediction": most_common_tip,
                    "avg_odds": avg_odds,
                    "link": link
                })

            except Exception as err:
                print("Meccs feldolgozási hiba:", err)
                continue

    # Szétválasztás duplázás nélkül
    suspicious_tips = [tip for tip in tips if tip["avg_odds"] and tip["avg_odds"] >= 6]
    suspicious_matches = {tip["match"] for tip in suspicious_tips}

    smart_tips = [
        tip for tip in sorted(tips, key=lambda x: x["avg_odds"] or 0, reverse=True)
        if tip["match"] not in suspicious_matches
    ][:10]

    return render_template(
        "index.html",
        smart_tips=smart_tips,
        suspicious_tips=suspicious_tips,
        selected_date=date_filter.isoformat()
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
