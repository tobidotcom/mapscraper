import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from google_maps import search_google_maps
from openai import get_postal_codes
from gohighlevel import add_contact_to_gohighlevel
from utils import save_to_csv, display_results, calculate_lead_score
from web_scraper import scrape_website, get_business_reviews, get_best_email_from_openai

def process_postal_code(postal_code, query, api_key):
    st.write(f"Searching in postal code: {postal_code}")
    businesses = search_google_maps(query, postal_code, api_key)
    return businesses

def enrich_data(businesses, google_maps_api_key, openai_api_key):
    enriched_businesses = []
    for business in businesses:
        if "place_id" in business and business.get("website"):
            try:
                scrape_data = scrape_website(business["website"], openai_api_key)
                reviews = get_business_reviews(business["place_id"], google_maps_api_key)
                best_email = get_best_email_from_openai(scrape_data["website_content"], reviews, openai_api_key)
                business.update(scrape_data)
                business["best_email"] = best_email
            except Exception as e:
                st.error(f"Error enriching data for business {business['name']}: {e}")
        else:
            st.error(f"Business {business['name']} does not have a place_id or website.")
        enriched_businesses.append(business)
    return enriched_businesses

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

            # Calculate lead score for each business
            for business in unique_businesses:
                business["lead_score"] = calculate_lead_score(business)
            
            save_to_csv(unique_businesses, "businesses.csv")
            st.success(f"Saved {len(unique_businesses)} results to businesses.csv")
            display_results(unique_businesses, st)

            st.session_state.businesses = unique_businesses

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
                            "website": business["website"],
                            "email": business.get('best_email', '')
                        }
                        response = add_contact_to_gohighlevel(gohighlevel_api_key, contact)
                        st.write(f"Added contact: {response}")

    if st.button("Enrich Data"):
        if 'businesses' not in st.session_state:
            st.error("No businesses found. Please perform a search first.")
        else:
            try:
                enriched_businesses = enrich_data(st.session_state.businesses, google_maps_api_key, openai_api_key)
                save_to_csv(enriched_businesses, "enriched_businesses.csv")
                st.success(f"Saved enriched data to enriched_businesses.csv")
                display_results(enriched_businesses, st)
            except Exception as e:
                st.error(f"Error enriching data: {e}")

if __name__ == "__main__":
    main()


