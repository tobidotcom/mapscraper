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
                business = {
                    "name": place.get("name"),
                    "address": place.get("formatted_address"),
                    "rating": place.get("rating", 0),
                    "user_ratings_total": place.get("user_ratings_total", 0),
                    "website": place.get("website", ""),
                    "phone": place.get("formatted_phone_number", "")
                }
                businesses.append(business)

            # Check for next page
            next_page_token = data.get("next_page_token")
            if next_page_token:
                params["pagetoken"] = next_page_token
            else:
                break
    
    return businesses
