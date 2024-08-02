import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from google_maps import search_google_maps
from openai_api import get_postal_codes
from gohighlevel import add_contact_to_gohighlevel
from utils import save_to_csv, display_results, calculate_lead_score

def fetch_businesses_for_postal_code(search_query, postal_code, google_maps_api_key):
    try:
        return search_google_maps(search_query, postal_code, google_maps_api_key)
    except Exception as e:
        st.error(f"Error fetching data for postal code {postal_code}: {e}")
        return []

def main():
    st.title("1001Leads - Cold Calling Challenge")

    st.sidebar.header("Settings")
    google_maps_api_key = st.sidebar.text_input("Google Maps API Key", type="password", key="google_maps_api_key")
    gohighlevel_api_key = st.sidebar.text_input("GoHighLevel API Key", type="password", key="gohighlevel_api_key")
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password", key="openai_api_key")

    search_query = st.text_input("Enter your search query (e.g., plumbers, landscapers)", key="search_query")
    user_city = st.text_input("Enter your city", key="user_city")

    if st.button("Generate Leads", key="generate_leads"):
        if not google_maps_api_key:
            st.error("Please enter a valid Google Maps API key.")
        elif not gohighlevel_api_key:
            st.error("Please enter a valid GoHighLevel API key.")
        elif not openai_api_key:
            st.error("Please enter a valid OpenAI API key.")
        elif not user_city:
            st.error("Please enter your city.")
        else:
            # Get postal codes
            postal_codes = get_postal_codes(user_city, openai_api_key)
            if not postal_codes:
                st.error("Could not retrieve postal codes. Please check your OpenAI API key and city.")
                return

            all_businesses = []

            # Create a progress bar
            progress_bar = st.progress(0)
            total_postal_codes = len(postal_codes)
            progress_step = 100 / total_postal_codes if total_postal_codes else 1

            # Process postal codes with multithreading
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures_to_postal_code = {executor.submit(fetch_businesses_for_postal_code, search_query, postal_code, google_maps_api_key): postal_code for postal_code in postal_codes}

                for i, future in enumerate(as_completed(futures_to_postal_code)):
                    postal_code = futures_to_postal_code[future]
                    try:
                        businesses = future.result()
                        all_businesses.extend(businesses)
                        progress = (i + 1) * progress_step
                        progress_bar.progress(progress)
                    except Exception as exc:
                        st.error(f"Error occurred while processing postal code {postal_code}: {exc}")

            # Ensure progress bar completes
            progress_bar.progress(100)

            if not all_businesses:
                st.error("No businesses found. Please refine your search.")
                return

            # Calculate lead scores
            for business in all_businesses:
                business["lead_score"] = calculate_lead_score(business)

            # Sort businesses by lead score
            all_businesses_sorted = sorted(all_businesses, key=lambda x: x["lead_score"], reverse=True)

            # Save to CSV and display results
            save_to_csv(all_businesses_sorted, "all_businesses.csv")
            st.success(f"Saved {len(all_businesses_sorted)} leads to all_businesses.csv")
            display_results(all_businesses_sorted, st)

            # Adding selected businesses to GoHighLevel
            business_names = [f"{business['name']} - {business['address']} (Score: {business['lead_score']})" for business in all_businesses_sorted]
            selected_businesses = st.multiselect("Select businesses to add to GoHighLevel", business_names, key="selected_businesses")

            if st.button("Add Selected to GoHighLevel", key="add_to_gohighlevel"):
                for business in all_businesses_sorted:
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

