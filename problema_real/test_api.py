import requests

API_KEY = 'AIzaSyCWA8EOMmd6Gl-PKN7WhH0h7hwRQFaSwys'
url = 'https://maps.googleapis.com/maps/api/distancematrix/json'

params = {
    'origins': '4.4363,-75.2238',  # Bogotá
    'destinations': '4.4442, -75.2256',  # Cerca de la 26
    'key': API_KEY,
    'departure_time': 'now',
    'traffic_model': 'best_guess'
}

response = requests.get(url, params=params)
data = response.json()

print("Status:", data.get("status"))
if data["status"] == "OK":
    tiempo = data["rows"][0]["elements"][0]["duration_in_traffic"]["text"]
    print("Tiempo con tráfico:", tiempo)
else:
    print("Error:", data.get("error_message", "Desconocido"))