import pandas as pd

def save_to_csv(businesses, file_path):
    if not businesses:
        raise ValueError("No businesses data to save.")
    
    df = pd.DataFrame(businesses)
    df.to_csv(file_path, index=False)

def display_results(businesses, streamlit_instance):
    streamlit_instance.write("## Search Results")
    if businesses:
        df = pd.DataFrame(businesses)
        streamlit_instance.dataframe(df)
    else:
        streamlit_instance.write("No results found.")
