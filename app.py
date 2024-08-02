import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from google_maps import search_google_maps
from openai_api import get_postal_codes, evaluate_businesses
from gohighlevel import add_contact_to_gohighlevel
from utils import save_to_csv, display_results
from web_scraper import scrape_website, get_business_reviews

def process_postal_code(postal_code, query, api_key):
    st.write(f"Searching in postal code: {postal_code}")
    businesses = search_google_maps(query, postal_code, api_key)
    return businesses

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
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_postal_code = {executor.submit(process_postal_code, postal_code, query, google_maps_api_key): postal_code for postal_code in postal_codes}
                for future in as_completed(future_to_postal_code):
                    postal_code = future_to_postal_code[future]
                    try:
                        businesses = future.result()
                        all_businesses.extend(businesses)
                    except Exception as exc:
                        st.error(f"Error occurred while processing postal code {postal_code}: {exc}")

            # Remove duplicates
            unique_businesses = {b['name'] + b['address']: b for b in all_businesses}.values()
            unique_businesses = list(unique_businesses)  # Convert to list if needed

            # Debugging: Print the unique_businesses to see its content
            st.write("Unique businesses:", unique_businesses)
            
            # Check if unique_businesses is empty
            if not unique_businesses:
                st.error("No businesses found. Please try different search criteria.")
                return

            # Save businesses to CSV for evaluation
            csv_file_path = "businesses.csv"
            try:
                save_to_csv(unique_businesses, csv_file_path)
                st.success(f"Saved {len(unique_businesses)} results to {csv_file_path}")
            except ValueError as e:
                st.error(f"Error saving data to CSV: {e}")
                return

            # Evaluate businesses using OpenAI
            evaluation_result = evaluate_businesses(csv_file_path, openai_api_key)
            st.write(f"**Evaluation Result:** {evaluation_result}")

            # Display results
            display_results(unique_businesses, st)

            st.session_state.businesses = unique_businesses

            business_names = [f"{business['name']} - {business['address']}" for business in unique_businesses]
            selected_businesses = st.multiselect("Select businesses to add to GoHighLevel", business_names)
            
            if st.button("Add Selected to GoHighLevel"):
                for business in unique_businesses:
                    business_str = f"{business['name']} - {business['address']}"
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

