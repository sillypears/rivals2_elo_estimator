import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("STEAM_WEB_API_KEY")
APP_ID = os.environ.get("STEAM_APP_ID")
LEADERBOARD_ID = os.environ.get("STEAM_LEADERBOARD_ID")

url = 'https://partner.steam-api.com/ISteamLeaderboards/GetLeaderboardEntries/v1/'
params = {
    'key': API_KEY,
    'appid': APP_ID,
    'leaderboardid': LEADERBOARD_ID,
    'rangestart': 1,
    'rangeend': 100,
    'range_start': 1,
    'range_end': 100,
    'datarequest': 0  # 0 = Global, 1 = Global Around User, 2 = Friends
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    for entry in data['response']['entries']:
        print(entry['steamid'], entry['score'], entry['rank'])
else:
    print(f"Error: {response.status_code} - {response.text}")