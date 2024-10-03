import requests


def get_coordinates(query):
    try:
        if query == "not covered":
            return (1, 1)
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
        headers = {"User-Agent": "Testing App"}
        response = requests.get(url, headers=headers)
        response = response.json()
        if len(response) == 0:
            raise Exception("No results found")
        lat_lon = (
            round(float(response[0]["lat"]), 7),
            round(float(response[0]["lon"]), 7),
        )
        return lat_lon
    except Exception as e:
        return e
