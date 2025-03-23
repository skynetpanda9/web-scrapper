import requests
from bs4 import BeautifulSoup

sources = {
    'TechCrunch': 'https://techcrunch.com/',
    'Ars Technica': 'https://arstechnica.com/',
    'The Verge': 'https://www.theverge.com/',
    'Wired': 'https://www.wired.com/',
    'Engadget': 'https://www.engadget.com/'
}

def scrape_articles():
    articles = []
    for name, url in sources.items():
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for item in soup.select('article h2 a')[:5]:  # Top 5 per site
            title = item.text.strip()
            link = item['href']
            if isinstance(link, list):
                link = link[0]
            if not link.startswith('http'):
                link = url + link
            articles.append({'title': title, 'url': link})
    return articles