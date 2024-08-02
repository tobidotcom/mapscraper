import csv
import pandas as pd

def save_to_csv(businesses, filename):
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["name", "address", "phone", "website", "rating", "user_ratings_total", "lead_score"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for business in businesses:
            writer.writerow(business)

def display_results(businesses, streamlit_instance):
    streamlit_instance.write("## Search Results")
    if businesses:
        df = pd.DataFrame(businesses)
        streamlit_instance.dataframe(df)
    else:
        streamlit_instance.write("No results found.")

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
