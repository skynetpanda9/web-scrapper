from ollama import Client
import requests
from bs4 import BeautifulSoup

client = Client(host='http://localhost:11434')

def summarize_article(url: str) -> str:
    try:
        # Fetch article content
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad HTTP status codes

        soup = BeautifulSoup(response.text, 'html.parser')
        content = ' '.join(p.text for p in soup.select('p')[:10])

        # Summarize with Phi-4
        prompt = f"Summarize this in 60 words: {content}"
        model_response = client.generate(model='phi4', prompt=prompt)

        # Safely access the response
        if isinstance(model_response, dict) and 'response' in model_response:
            summary = model_response['response'].strip()
            return summary[:300]
        else:
            return "Error: Unable to generate summary"

    except requests.RequestException as e:
        return f"Error fetching article: {str(e)}"
    except Exception as e:
        return f"Error generating summary: {str(e)}"