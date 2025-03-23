import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from models import Article  # Now importing from models
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import traceback

sources = {
    'TechCrunch': 'https://techcrunch.com/',
    'Ars Technica': 'https://arstechnica.com/',
    'The Verge': 'https://www.theverge.com/',
    'Wired': 'https://www.wired.com/',
    'Engadget': 'https://www.engadget.com/'
}

def scrape_articles(db: Session) -> List[Dict[str, str]]:
    articles: List[Dict[str, str]] = []

    # Get existing URLs and print them for debugging
    existing_urls = {article.url for article in db.query(Article.url).all()}
    print(f"Existing URLs in DB: {len(existing_urls)}")
    print(f"Sample existing URLs: {list(existing_urls)[:5]}")  # Print some samples

    for name, url in sources.items():
        print(f"Scraping {name} at {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Save HTML for debugging if needed
            # with open(f"{name.lower()}_debug.html", "w", encoding="utf-8") as f:
            #     f.write(response.text)

            soup = BeautifulSoup(response.text, 'html.parser')

            # Try different selectors for different sites
            selectors = [
                'article h2 a',           # Your original selector
                'h2 a',                   # Simpler selector
                '.article-title a',       # Class-based selector
                '.headline a',            # Another common pattern
                'a.article-link',         # Direct article links
                '.post-block__title a'    # TechCrunch specific
            ]

            # Try each selector until we find something
            links = []
            for selector in selectors:
                links = soup.select(selector)
                if links:
                    print(f"Found {len(links)} links with selector '{selector}' at {name}")
                    break

            if not links:
                print(f"WARNING: No links found at {name} with any selector!")
                # Print the first 1000 chars of HTML to see what we're getting
                print(f"HTML preview: {response.text[:1000]}...")
                continue

            for item in links[:10]:  # Limit to first 10
                try:
                    title = item.text.strip()
                    link = item.get('href', '')

                    # Debug the href attribute
                    print(f"Raw href: {link} (type: {type(link)})")

                    if not isinstance(link, str):
                        print(f"WARNING: href is not a string: {link}")
                        link = link[0] if link else ''

                    # Check if link is relative and join with base URL
                    if not link.startswith(('http://', 'https://')):
                        old_link = link
                        link = urljoin(url, link)
                        print(f"Converted relative URL: {old_link} -> {link}")

                    # Check if this URL is already in the database
                    if link in existing_urls:
                        print(f"Skipping existing article: {title} ({link})")
                    else:
                        articles.append({'title': title, 'url': link})
                        existing_urls.add(link)
                        print(f"Added new article: {title} ({link})")
                except Exception as e:
                    print(f"Error processing link: {e}")
                    traceback.print_exc()

        except requests.RequestException as e:
            print(f"Error scraping {name}: {e}")
            traceback.print_exc()
        except Exception as e:
            print(f"Unexpected error scraping {name}: {e}")
            traceback.print_exc()

    print(f"Total new articles: {len(articles)}")
    return articles