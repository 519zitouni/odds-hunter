import os
import requests
import random
import time

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

def generate_bet():
    matches = [
        "PSG vs Lyon",
        "Real Madrid vs Sevilla",
        "Man City vs Chelsea",
        "Inter vs Milan",
        "Bayern vs Dortmund"
    ]

    bets = [
        "Victoire domicile",
        "Plus de 2.5 buts",
        "Les deux équipes marquent",
        "Victoire extérieure",
        "Moins de 3.5 buts"
    ]

    match = random.choice(matches)
    bet = random.choice(bets)
    cote = round(random.uniform(1.80, 2.20), 2)

    return f"""
🔥 ODDS HUNTER IA

⚽ Match : {match}
🎯 Pari : {bet}
💰 Cote : {cote}

🧠 Analyse :
Forme récente solide, dynamique positive.
Lecture du match favorable avec bon pressentiment.

💎 Value détectée
"""

def main():
    message = generate_bet()
    send_telegram(message)

if __name__ == "__main__":
    main()
