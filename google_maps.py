import requests

def search_google_maps(query, postal_code, api_key):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": api_key,
        "region": "us",
        "language": "en"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching data from Google Maps API: {response.text}")

    places = response.json().get("results", [])
    businesses = []

    for place in places:
        business = {
            "name": place.get("name"),
            "address": place.get("formatted_address"),
            "rating": place.get("rating", 0),
            "user_ratings_total": place.get("user_ratings_total", 0),
            "website": place.get("website", ""),
            "phone": place.get("formatted_phone_number", "")
        }
        businesses.append(business)
    
    return businesses

