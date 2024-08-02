# Contents of google_maps.py
import aiohttp

async def search_google_maps(query, postal_code, api_key, session):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    businesses = []
    
    params = {
        "query": query,
        "key": api_key,
        "region": "us",
        "language": "en",
        "location": postal_code,
        "radius": 10000  # Adjust the radius as needed
    }

    while True:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                raise Exception(f"Error fetching data from Google Maps API: {await response.text()}")

            data = await response.json()
            places = data.get("results", [])

            for place in places:
                place_id = place.get("place_id")
                details = await get_place_details(place_id, api_key, session)

                business = {
                    "name": place.get("name", "N/A"),
                    "address": place.get("formatted_address", "N/A"),
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

async def get_place_details(place_id, api_key, session):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'place_id': place_id,
        'key': api_key,
        'fields': 'formatted_phone_number,website'
    }
    try:
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            data = await response.json()
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

