import requests
from bs4 import BeautifulSoup
import re

def extract_emails_from_text(text):
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_regex, text)

def extract_emails_from_soup(soup):
    emails = set()
    text_content = ' '.join(element.get_text() for element in soup.find_all(text=True))
    emails.update(extract_emails_from_text(text_content))
    for tag in soup.find_all(['a', 'p', 'span', 'li']):
        if tag.has_attr('href'):
            href = tag['href']
            if 'mailto:' in href:
                emails.add(href.split('mailto:')[1])
    return list(emails)

def scrape_website(url, openai_api_key=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        emails = extract_emails_from_soup(soup)
        best_email = emails[0] if emails else None
        
        return {
            "emails": emails,
            "best_email": best_email,
            "website_content": soup.get_text()
        }

    except Exception as e:
        print(f"Error scraping website {url}: {e}")
        return {
            "emails": [],
            "best_email": None,
            "website_content": ""
        }

def get_business_reviews(place_id, google_maps_api_key):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "reviews",
        "key": google_maps_api_key
    }

    response = requests.get(url, params=params)
    details_data = response.json()

    reviews = []
    if details_data.get("result") and "reviews" in details_data["result"]:
        reviews = [review["text"] for review in details_data["result"]["reviews"]]
    
    return reviews

def get_best_email_from_openai(website_content, reviews, openai_api_key):
    import openai

    openai.api_key = openai_api_key

    prompt = (f"Given the following content from a website and customer reviews, "
              "craft a personalized cold email to sell our services. "
              "Include the best email address to contact. \n\n"
              f"Website Content: {website_content}\n\n"
              f"Reviews: {' '.join(reviews)}")
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )
    
    email = response.choices[0].message["content"].strip()
    return email if email else None

