import streamlit as st
import csv
import requests
import pandas as pd

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

    response = requests.get(url, params=params)
    data = response.json()

    businesses = []
    for result in data["results"]:
        name = result["name"]
        address = result["formatted_address"]
        place_id = result["place_id"]
        
        # Get additional details for each place
        phone, website = get_place_details(place_id, api_key)
        
        businesses.append({"name": name, "address": address, "phone": phone, "website": website})

    return businesses

# Function to save the extracted data to a CSV file
def save_to_csv(businesses, filename):
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["name", "address", "phone", "website"]
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

# Main function to handle the Streamlit app
def main():
    st.title("Lead Generation Tool")

    st.sidebar.header("Settings")
    api_key = st.sidebar.text_input("Google Maps API Key", type="password")

    query = st.text_input("Query")
    location = st.text_input("Location")

    if st.button("Search"):
        if not api_key:
            st.error("Please enter a valid API key in the settings.")
        else:
            businesses = search_google_maps(query, location, api_key)
            save_to_csv(businesses, "businesses.csv")
            st.success(f"Saved {len(businesses)} results to businesses.csv")
            display_results(businesses)

if __name__ == "__main__":
    main()
