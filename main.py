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
    url = "https://v3.football.api-sports.io/fixtures?next=5"
    headers = {"x-apisports-key": API_KEY}

    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return []

    data = res.json()

    matches = []
    for m in data.get("response", []):
        matches.append({
            "home": m["teams"]["home"]["name"],
            "away": m["teams"]["away"]["name"]
        })

    return matches

def get_odds():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={ODDS_KEY}&regions=eu&markets=h2h"
    res = requests.get(url)

    if res.status_code != 200:
        return {}

    data = res.json()

    odds_map = {}

    for game in data:
        try:
            home = game["home_team"]
            away = game["away_team"]

            outcomes = game["bookmakers"][0]["markets"][0]["outcomes"]

            for o in outcomes:
                odds_map[f"{home} vs {away}"] = o["price"]

        except:
            continue

    return odds_map

def build():
    try:
        matches = get_matches()
        odds_map = get_odds()

        msg = "🔎 TEST BOT\n\n"

        msg += f"Matchs trouvés: {len(matches)}\n"
        msg += f"Cotes trouvées: {len(odds_map)}\n\n"

        if not matches:
            msg += "❌ Aucun match API FOOTBALL\n"

        if not odds_map:
            msg += "❌ Aucune cote ODDS API\n"

        # afficher 1 match exemple
        if matches:
            m = matches[0]
            key = f"{m['home']} vs {m['away']}"
            msg += f"\nExemple match:\n{key}\n"

            if key in odds_map:
                msg += f"Cote trouvée: {odds_map[key]}"
            else:
                msg += "⚠️ Pas de cote pour ce match"

        return msg

    except Exception as e:
        return f"❌ ERREUR: {str(e)}"

def main():
    while True:
        message = build()
        send(message)
        time.sleep(60)  # envoie toutes les 60 secondes pour test

if __name__ == "__main__":
    main()