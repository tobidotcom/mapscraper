import requests
import time

def get_place_details(place_id, api_key):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number,website",
        "key": api_key
    }
    response = requests.get(url, params=params)
    details_data = response.json()
    
    if details_data.get("result"):
        phone = details_data["result"].get("formatted_phone_number", "")
        website = details_data["result"].get("website", "")
    else:
        phone = ""
        website = ""
    
    return phone, website

def search_google_maps(query, location, api_key):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{query} in {location}",
        "key": api_key
    }

    businesses = []
    while True:
        response = requests.get(url, params=params)
        data = response.json()
        
        for result in data["results"]:
            name = result["name"]
            address = result["formatted_address"]
            place_id = result["place_id"]
            rating = result.get("rating", 0)
            user_ratings_total = result.get("user_ratings_total", 0)
            
            # Get additional details for each place
            phone, website = get_place_details(place_id, api_key)
            
            businesses.append({
                "name": name, 
                "address": address, 
                "phone": phone, 
                "website": website,
                "rating": rating,
                "user_ratings_total": user_ratings_total
            })

        if 'next_page_token' not in data:
            break

        next_page_token = data['next_page_token']
        params['pagetoken'] = next_page_token

        # Google Maps Places API enforces a short delay before fetching the next page
        time.sleep(2)

    return businesses
