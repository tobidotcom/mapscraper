import streamlit as st
import csv
import requests

# Function to search Google Maps and extract business information
def search_google_maps(query, location, api_key):
    # Construct the URL for the Google Maps Places API search request
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{query} in {location}",
        "key": api_key
    }

    # Send an HTTP request to the URL and get the JSON response
    response = requests.get(url, params=params)
    data = response.json()

    # Extract the business information from the JSON response
    businesses = []
    for result in data["results"]:
        name = result["name"]
        address = result["formatted_address"]
        phone = result.get("formatted_phone_number", "")
        website = result.get("website", "")
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
    import pandas as pd
    main()
