import requests
from bs4 import BeautifulSoup

def extract_emails_from_text(text):
    import re
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

def scrape_website(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        return {
            "website_content": soup.get_text()
        }

    except Exception as e:
        print(f"Error scraping website {url}: {e}")
        return {
            "website_content": ""
        }
