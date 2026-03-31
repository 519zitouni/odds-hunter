import os
import requests
import time
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("API_KEY")
ODDS_KEY = os.getenv("ODDS_KEY")

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# MATCHS DU JOUR
def get_matches():
    url = "https://v3.football.api-sports.io/fixtures?next=10"
    headers = {"x-apisports-key": API_KEY}

    res = requests.get(url, headers=headers).json()
    matches = []

    for m in res["response"]:
        matches.append({
            "home": m["teams"]["home"]["name"],
            "away": m["teams"]["away"]["name"],
            "league": m["league"]["name"]
        })

    return matches

# COTES
def get_odds():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={ODDS_KEY}&regions=eu&markets=h2h"
    res = requests.get(url).json()

    odds_map = {}

    for game in res:
        home = game["home_team"]
        away = game["away_team"]

        try:
            outcomes = game["bookmakers"][0]["markets"][0]["outcomes"]
            for o in outcomes:
                odds_map[f"{home} vs {away}"] = o["price"]
        except:
            continue

    return odds_map

# ANALYSE
def analyze(match, odds):

    score = 0

    # logique bookmaker
    if odds > 3:
        score += 2

    if 1.8 <= odds <= 2.2:
        score += 2

    # ligues fiables
    top = ["Premier League", "Ligue 1", "La Liga", "Serie A", "Bundesliga"]
    if match["league"] in top:
        score += 1

    # piège favori
    if odds > 2.5:
        score += 1

    prob = 0.40 + (score * 0.07)
    implied = 1 / odds
    value = prob - implied

    return prob, value, score

# SELECTION
def pick(matches, odds_map):

    best_safe = None
    best_value = None

    for m in matches:

        key = f"{m['home']} vs {m['away']}"
        if key not in odds_map:
            continue

        odds = odds_map[key]
        prob, value, score = analyze(m, odds)

        if 1.9 <= odds <= 2.2:
            if not best_safe or score > best_safe["score"]:
                best_safe = {"match": key, "odds": odds, "prob": prob, "score": score}

        if value > 0.07:
            if not best_value or value > best_value["value"]:
                best_value = {"match": key, "odds": odds, "prob": prob, "value": value}

    return best_safe, best_value

# MESSAGE
def build():

    matches = get_matches()
    odds_map = get_odds()

    safe, value = pick(matches, odds_map)

    date = datetime.now().strftime("%d/%m/%Y")

    msg = f"🔥 ODDS HUNTER PRO\n📅 {date}\n\n"

    if safe:
        msg += f"🎯 SAFE\n{safe['match']}\nCote: {safe['odds']}\n\n"

    if value:
        msg += f"💎 VALUE\n{value['match']}\nCote: {value['odds']}\n\n"

    msg += "📊 Analyse basée sur données réelles\n💰 Mise: 1-2% bankroll"

    return msg

# LOOP
def main():
    while True:
        try:
            msg = build()
            send(msg)
            time.sleep(86400)
        except:
            time.sleep(300)

if __name__ == "__main__":
    main()