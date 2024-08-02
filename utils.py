# Contents of utils.py
import csv
import pandas as pd

def save_to_csv(businesses, filename):
    if not businesses:
        raise ValueError("No businesses data to save.")

    # Get all possible fieldnames from the first business
    all_fieldnames = set()
    for business in businesses:
        all_fieldnames.update(business.keys())
    
    fieldnames = sorted(list(all_fieldnames))
    
    with open(filename, "w", newline="") as csvfile:
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

