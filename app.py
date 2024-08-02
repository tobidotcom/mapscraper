import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from google_maps import search_google_maps
from openai_api import get_postal_codes, evaluate_businesses
from gohighlevel import add_contact_to_gohighlevel
from utils import save_to_csv, display_results, calculate_lead_score

def get_postal_codes_for_area(user_address, openai_api_key):
    # Generate postal codes for the user’s area using OpenAI
    return get_postal_codes(user_address, openai_api_key)

def process_postal_code(postal_code, query, api_key):
    st.write(f"Searching in postal code: {postal_code}")
    businesses = search_google_maps(query, postal_code, api_key)
    return businesses

def main():
    st.title("1001Leads - Cold Calling Challenge")

    st.sidebar.header("Settings")
    google_maps_api_key = st.sidebar.text_input("Google Maps API Key", type="password")
    gohighlevel_api_key = st.sidebar.text_input("GoHighLevel API Key", type="password")
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

    business_description = st.text_area("Describe Your Business and Services")
    user_website = st.text_input("Optional: Your Website")
    user_address = st.text_input("Your Business Address")

    if st.button("Generate Leads"):
        if not google_maps_api_key:
            st.error("Please enter a valid Google Maps API key.")
        elif not gohighlevel_api_key:
            st.error("Please enter a valid GoHighLevel API key.")
        elif not openai_api_key:
            st.error("Please enter a valid OpenAI API key.")
        elif not user_address:
            st.error("Please enter your business address.")
        else:
            # Get the postal codes for the user’s area
            postal_codes = get_postal_codes_for_area(user_address, openai_api_key)
            if not postal_codes:
                st.error("Could not retrieve postal codes. Please check your OpenAI API key and business address.")
                return

            # Construct the query based on user input
            query = f"{business_description} in {user_address}"

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

            if not all_businesses:
                st.error("No businesses found. Please refine your search.")
                return

            # Calculate lead scores
            for business in all_businesses:
                business["lead_score"] = calculate_lead_score(business)
            
            # Sort businesses by lead score and pick top 1001
            top_businesses = sorted(all_businesses, key=lambda x: x["lead_score"], reverse=True)[:1001]

            # Save to CSV and display results
            save_to_csv(top_businesses, "top_businesses.csv")
            st.success(f"Saved {len(top_businesses)} top leads to top_businesses.csv")
            display_results(top_businesses, st)

            # Adding selected businesses to GoHighLevel
            business_names = [f"{business['name']} - {business['address']} (Score: {business['lead_score']})" for business in top_businesses]
            selected_businesses = st.multiselect("Select businesses to add to GoHighLevel", business_names)
            
            if st.button("Add Selected to GoHighLevel"):
                for business in top_businesses:
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
