import requests
import time

def get_place_details(place_id, api_key):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number,website,rating,user_ratings_total,reviews",
        "key": api_key
    }
    response = requests.get(url, params=params)
    details_data = response.json()
    
    if details_data.get("result"):
        phone = details_data["result"].get("formatted_phone_number", "")
        website = details_data["result"].get("website", "")
        rating = details_data["result"].get("rating", 0)
        user_ratings_total = details_data["result"].get("user_ratings_total", 0)
        reviews = details_data["result"].get("reviews", [])
        review_texts = [review.get("text", "") for review in reviews]
        return {
            "phone": phone,
            "website": website,
            "rating": rating,
            "user_ratings_total": user_ratings_total,
            "reviews": review_texts
        }
    return {}

def search_google_maps(query, postal_code, api_key):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": api_key,
        "region": postal_code
    }
    businesses = []
    next_page_token = None
    while True:
        if next_page_token:
            params["pagetoken"] = next_page_token
        response = requests.get(url, params=params)
        data = response.json()
        
        for result in data.get("results", []):
            place_id = result.get("place_id")
            business_details = get_place_details(place_id, api_key)
            business = {
                "name": result.get("name"),
                "address": result.get("formatted_address"),
                "phone": business_details.get("phone"),
                "website": business_details.get("website"),
                "rating": business_details.get("rating"),
                "user_ratings_total": business_details.get("user_ratings_total"),
                "reviews": business_details.get("reviews")
            }
            businesses.append(business)
        
        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break
        
        time.sleep(2)  # Wait a bit before requesting the next page
    
    return businesses
