import os
import requests
import time

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("API_KEY")
ODDS_KEY = os.getenv("ODDS_KEY")

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_matches():
    url = "https://v3.football.api-sports.io/fixtures?next=10"
    headers = {"x-apisports-key": API_KEY}

    try:
        res = requests.get(url, headers=headers)
        data = res.json()

        matches = []
        for m in data.get("response", []):
            matches.append({
                "home": m["teams"]["home"]["name"],
                "away": m["teams"]["away"]["name"]
            })

        return matches

    except:
        return []

def get_odds():
    url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={ODDS_KEY}&regions=eu&markets=h2h"

    try:
        res = requests.get(url)
        data = res.json()

        odds_map = {}

        for game in data:
            try:
                home = game["home_team"]
                away = game["away_team"]

                bookmakers = game.get("bookmakers", [])
                if not bookmakers:
                    continue

                outcomes = bookmakers[0]["markets"][0]["outcomes"]

                for o in outcomes:
                    odds_map[f"{home} vs {away}"] = o["price"]

            except:
                continue

        return odds_map

    except:
        return {}

def build():
    matches = get_matches()
    odds_map = get_odds()

    msg = "🔥 BOT ANALYSE RÉEL\n\n"

    msg += f"Matchs API: {len(matches)}\n"
    msg += f"Cotes API: {len(odds_map)}\n\n"

    # fallback si API vide
    if not matches or not odds_map:
        msg += "⚠️ API limitée ou vide\n"
        msg += "👉 Vérifie tes clés ou quota API\n"
        return msg

    # associer match + cote
    for m in matches:
        key = f"{m['home']} vs {m['away']}"
        if key in odds_map:
            msg += f"\n⚽ {key}\n💰 {odds_map[key]}\n"
            break

    return msg

def main():
    while True:
        message = build()
        send(message)
        time.sleep(60)

if __name__ == "__main__":
    main()