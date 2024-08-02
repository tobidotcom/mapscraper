import requests

def search_google_maps(query, postal_codes, api_key):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    businesses = []

    for postal_code in postal_codes:
        params = {
            "query": query,
            "key": api_key,
            "region": "us",
            "language": "en",
            "pagetoken": None
        }
        while True:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                raise Exception(f"Error fetching data from Google Maps API: {response.text}")

            data = response.json()
            places = data.get("results", [])

            for place in places:
                place_id = place.get("place_id")
                details = get_place_details(place_id, api_key)

                business = {
                    "name": place.get("name"),
                    "address": place.get("formatted_address"),
                    "rating": place.get("rating", 0),
                    "user_ratings_total": place.get("user_ratings_total", 0),
                    "website": details.get("website", ""),
                    "phone": details.get("phone", "")
                }
                businesses.append(business)

            # Check for next page
            next_page_token = data.get("next_page_token")
            if next_page_token:
                params["pagetoken"] = next_page_token
            else:
                break

    return businesses

def get_place_details(place_id, api_key):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'place_id': place_id,
        'key': api_key,
        'fields': 'formatted_phone_number,website'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        result = data.get('result', {})
        return {
            "phone": result.get("formatted_phone_number", ""),
            "website": result.get("website", "")
        }
    except Exception as e:
        print(f"Error fetching details for place_id {place_id}: {e}")
        return {
            "phone": "",
            "website": ""
        }
