import requests
from bs4 import BeautifulSoup
import re

def scrape_website(url, openai_api_key):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch website: {str(e)}"}

    soup = BeautifulSoup(response.text, 'html.parser')

    emails = extract_emails(soup)
    best_email = select_best_email(emails, openai_api_key) if emails else None

    return {
        "emails": emails,
        "best_email": best_email
    }

def extract_emails(soup):
    """Extracts email addresses from the HTML soup."""
    emails = set()
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    for script in soup(['script', 'style']):
        script.decompose()
    
    text = soup.get_text()
    emails.update(re.findall(email_pattern, text))
    
    return list(emails)

def select_best_email(emails, openai_api_key):
    """Selects the best email address using OpenAI API."""
    if not emails:
        return None

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    messages = [
        {"role": "system", "content": "You are an email analysis assistant."},
        {"role": "user", "content": f"Given the following list of email addresses, choose the best one to contact: {', '.join(emails)}"}
    ]
    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 50
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        # Ensure 'choices' and 'message' keys exist
        best_email = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        
        if best_email in emails:
            return best_email
        else:
            return emails[0]  # Fallback to the first email if the response is invalid
    except requests.RequestException as e:
        return emails[0]  # Fallback to the first email in case of an error
    except (KeyError, IndexError):
        return emails[0]  # Fallback to the first email if the response structure is not as expected
