# Contents of app.py
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from google_maps import search_google_maps
from openai_api import get_postal_codes, evaluate_businesses
from gohighlevel import add_contact_to_gohighlevel
from utils import save_to_csv, display_results

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

            # Save results to CSV
            csv_file_path = "businesses.csv"
            try:
                save_to_csv(unique_businesses, csv_file_path)
                st.success(f"Saved {len(unique_businesses)} results to {csv_file_path}")
            except ValueError as ve:
                st.error(str(ve))
                return
            
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
                            "website": business["website"]
                        }
                        response = add_contact_to_gohighlevel(gohighlevel_api_key, contact)
                        st.write(f"Added contact: {response}")

    if st.button("Evaluate Best Leads"):
        if 'businesses' not in st.session_state:
            st.error("No businesses found. Please perform a search first.")
        else:
            try:
                evaluation_result = evaluate_businesses("businesses.csv", openai_api_key)
                st.write("## Evaluation Result")
                st.write(evaluation_result)
            except Exception as e:
                st.error(f"Error evaluating businesses: {e}")

if __name__ == "__main__":
    main()
