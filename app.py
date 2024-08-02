import streamlit as st
import csv
import requests
import pandas as pd
import time

# Function to get place details from Google Maps Places API
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

# Function to search Google Maps and extract business information
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

# Function to call OpenAI API and get postal codes
def get_postal_codes(city, openai_api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"List all postal codes for {city} in a comma-separated list format. Do only respond with the list, nothing else."}
        ],
        "max_tokens": 500
    }
    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    postal_codes = []
    if result.get("choices"):
        postal_codes = result["choices"][0]["message"]["content"]
        postal_codes = postal_codes.strip().split(',')
        postal_codes = [code.strip() for code in postal_codes]
    
    return postal_codes

# Function to save the extracted data to a CSV file
def save_to_csv(businesses, filename):
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["name", "address", "phone", "website", "rating", "user_ratings_total", "lead_score"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for business in businesses:
            writer.writerow(business)

# Function to display the results in a table
def display_results(businesses):
    st.write("## Search Results")
    if businesses:
        df = pd.DataFrame(businesses)
        st.dataframe(df)
    else:
        st.write("No results found.")

# Function to add a contact to GoHighLevel
def add_contact_to_gohighlevel(api_key, contact):
    url = "https://rest.gohighlevel.com/v1/contacts/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=contact, headers=headers)
    return response.json()

# Function to calculate lead score
def calculate_lead_score(business):
    score = 0
    if business["website"]:
        score += 20
    if business["phone"]:
        score += 10
    score += business["rating"] * 10
    if business["user_ratings_total"] > 10:
        score += 20
    if business["user_ratings_total"] > 50:
        score += 30
    return score

# Main function to handle the Streamlit app
def main():
    st.title("Lead Generation Tool")

    st.sidebar.header("Settings")
    google_maps_api_key = st.sidebar.text_input("Google Maps API Key", type="password")
    gohighlevel_api_key = st.sidebar.text_input("GoHighLevel API Key", type="password")
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

    query = st.text_input("Query")
    city = st.text_input("City")

    if st.button("Search"):
        if not google_maps_api_key:
            st.error("Please enter a valid Google Maps API key in the settings.")
        elif not gohighlevel_api_key:
            st.error("Please enter a valid GoHighLevel API key in the settings.")
        elif not openai_api_key:
            st.error("Please enter a valid OpenAI API key in the settings.")
        else:
            postal_codes = get_postal_codes(city, openai_api_key)
            if not postal_codes:
                st.error("Could not retrieve postal codes. Please check your OpenAI API key and city name.")
                return
            
            all_businesses = []

            for postal_code in postal_codes:
                st.write(f"Searching in postal code: {postal_code}")
                businesses = search_google_maps(query, postal_code, google_maps_api_key)
                all_businesses.extend(businesses)
                time.sleep(1)  # Prevent hitting the API rate limit

            # Remove duplicates
            unique_businesses = {b['name'] + b['address']: b for b in all_businesses}.values()

            # Calculate lead score for each business
            for business in unique_businesses:
                business["lead_score"] = calculate_lead_score(business)
            
            save_to_csv(unique_businesses, "businesses.csv")
            st.success(f"Saved {len(unique_businesses)} results to businesses.csv")
            display_results(unique_businesses)
            
            business_names = [f"{business['name']} - {business['address']} (Score: {business['lead_score']})" for business in unique_businesses]
            selected_businesses = st.multiselect("Select businesses to add to GoHighLevel", business_names)
            
            if st.button("Add Selected to GoHighLevel"):
                for business in unique_businesses:
                    business_str = f"{business['name']} - {business['address']} (Score: {business['lead_score']})"
                    if business_str in selected_businesses:
                        contact = {
                            "firstName": business["name"],
                            "address1": business["address"],
                            "phone": business["phone"],
                            "website": business["website"]
                        }
                        response = add_contact_to_gohighlevel(gohighlevel_api_key, contact)
                        st.write(f"Added contact: {response}")

if __name__ == "__main__":
    main()
