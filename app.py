import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from google_maps import search_google_maps
from openai_api import get_postal_codes
from gohighlevel import add_contact_to_gohighlevel
from utils import save_to_csv, display_results, calculate_lead_score

def get_postal_codes_for_area(city, openai_api_key):
    return get_postal_codes(city, openai_api_key)

def process_postal_code(postal_code, query, api_key):
    st.write(f"Searching in postal code: {postal_code}")
    businesses = search_google_maps(query, postal_code, api_key)
    return businesses

def main():
    st.title("Lead Generation App")

    st.sidebar.header("Settings")
    google_maps_api_key = st.sidebar.text_input("Google Maps API Key", type="password")
    gohighlevel_api_key = st.sidebar.text_input("GoHighLevel API Key", type="password")
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

    search_query = st.text_input("Search Query", placeholder="e.g., 'Plumbers'")
    city = st.text_input("City", placeholder="e.g., 'New York'")

    if st.button("Generate Leads"):
        if not google_maps_api_key:
            st.error("Please enter a valid Google Maps API key.")
        elif not gohighlevel_api_key:
            st.error("Please enter a valid GoHighLevel API key.")
        elif not openai_api_key:
            st.error("Please enter a valid OpenAI API key.")
        elif not search_query:
            st.error("Please enter a search query.")
        elif not city:
            st.error("Please enter a city.")
        else:
            # Get postal codes for the city
            st.write("Retrieving postal codes...")
            postal_codes = get_postal_codes_for_area(city, openai_api_key)
            if not postal_codes:
                st.error("Could not retrieve postal codes. Please check your OpenAI API key and city.")
                return

            # Construct the query based on user input
            all_businesses = []
            business_ids = set()
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_postal_code = {executor.submit(process_postal_code, postal_code, search_query, google_maps_api_key): postal_code for postal_code in postal_codes}
                for future in as_completed(future_to_postal_code):
                    postal_code = future_to_postal_code[future]
                    try:
                        businesses = future.result()
                        for business in businesses:
                            # Create a unique identifier for each business
                            business_id = f"{business['name']} - {business['address']}"
                            if business_id not in business_ids:
                                business_ids.add(business_id)
                                all_businesses.append(business)
                    except Exception as exc:
                        st.error(f"Error occurred while processing postal code {postal_code}: {exc}")

            if not all_businesses:
                st.error("No businesses found. Please refine your search.")
                return

            # Calculate lead scores
            for business in all_businesses:
                business["lead_score"] = calculate_lead_score(business)
            
            # Sort businesses by lead score
            sorted_businesses = sorted(all_businesses, key=lambda x: x["lead_score"], reverse=True)

            # Save to CSV and display all results
            save_to_csv(sorted_businesses, "all_businesses.csv")
            st.success(f"Saved {len(sorted_businesses)} leads to all_businesses.csv")
            display_results(sorted_businesses, st)

            # Adding selected businesses to GoHighLevel
            business_names = [f"{business['name']} - {business['address']} (Score: {business['lead_score']})" for business in sorted_businesses]
            selected_businesses = st.multiselect("Select businesses to add to GoHighLevel", business_names)
            
            if st.button("Add Selected to GoHighLevel"):
                for business in sorted_businesses:
                    business_str = f"{business['name']} - {business['address']} (Score: {business['lead_score']})"
                    if business_str in selected_businesses:
                        contact = {
                            "firstName": business["name"],
                            "address1": business["address"],
                            "phone": business["phone"],
                            "website": business["website"],
                            "email": business.get('best_email', '')
                        }
                        response = add_contact_to_gohighlevel(gohighlevel_api_key, contact)
                        st.write(f"Added contact: {response}")

if __name__ == "__main__":
    main()


