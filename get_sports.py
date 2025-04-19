import requests

API_KEY = "cfb1803716ad84725f69b7a7478e76e5"

url = f"https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}"

try:
    response = requests.get(url)
    sports = response.json()

    print("Elérhető sportágak:\n")
    for sport in sports:
        print(f"{sport['key']} - {sport['title']}")

except Exception as e:
    print("Hiba a lekérés során:", e)
