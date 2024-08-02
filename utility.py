import csv

def save_to_csv(businesses, filename):
    keys = businesses[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(businesses)

def display_results(businesses, st):
    for business in businesses:
        st.write(f"Name: {business['name']}")
        st.write(f"Address: {business['address']}")
        st.write(f"Rating: {business['rating']}")
        st.write(f"Reviews: {business['user_ratings_total']}")
        st.write(f"Website: {business.get('website', 'N/A')}")
        st.write(f"Phone: {business.get('phone', 'N/A')}")
        st.write(f"Lead Score: {business['lead_score']}")
        st.write("---")

def calculate_lead_score(business):
    score = 0
    if business.get("rating"):
        score += business["rating"] * 10
    if business.get("user_ratings_total"):
        score += business["user_ratings_total"] * 0.1
    if business.get("phone"):
        score += 10
    if business.get("website"):
        score += 10
    return score
