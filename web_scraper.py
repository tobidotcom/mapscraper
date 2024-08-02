import requests
from bs4 import BeautifulSoup
import re
import openai

def find_emails(text):
    # Enhanced regex patterns for finding email addresses
    email_patterns = [
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Standard email pattern
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})+',  # Handles some edge cases
    ]
    
    emails = set()
    for pattern in email_patterns:
        emails.update(re.findall(pattern, text))
    
    return emails

def get_best_email_from_openai(emails, page_content, openai_api_key):
    prompt = f"""
    I have extracted the following email addresses from a webpage. 
    The content of the webpage is also provided. 
    Based on this information, which email address is likely the best for reaching out to the business?

    Webpage Content: {page_content}
    
    Email Addresses: {', '.join(emails)}

    Please choose the most relevant email address.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        api_key=openai_api_key
    )
    
    result = response.choices[0].message['content'].strip()
    return result

def scrape_website(url, openai_api_key):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract email addresses
        emails = find_emails(soup.get_text())
        
        # Example: Extract the title and meta description
        title = soup.title.string if soup.title else 'No title'
        meta_description = soup.find('meta', attrs={'name': 'description'})
        description = meta_description['content'] if meta_description else 'No description'
        
        # Extract additional contact info from common tags
        contact_info = soup.find_all('a', href=True)
        contact_links = [a['href'] for a in contact_info if 'mailto:' in a['href']]
        contact_emails = [link.replace('mailto:', '') for link in contact_links]
        
        # Combine all emails found
        all_emails = set(emails | set(contact_emails))
        
        # Get the best email address from OpenAI
        best_email = get_best_email_from_openai(all_emails, soup.get_text(), openai_api_key)
        
        return {
            'title': title,
            'description': description,
            'best_email': best_email,
            'all_emails': ', '.join(all_emails)
        }
    except Exception as e:
        return {
            'error': str(e)
        }
