from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models import Article, get_db  # Importing from models
from scrapper import scrape_articles
from summarizer import summarize_article  # Assuming you have this module
from typing import List, Dict, Any

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/summaries", response_model=List[Dict[str, str]])
def get_summaries(db: Session = Depends(get_db)):
    articles = db.query(Article).all()
    return [{"title": a.title, "url": a.url, "summary": a.summary} for a in articles]

@app.post("/scrape-and-summarize", response_model=Dict[str, Any])
def scrape_and_summarize(db: Session = Depends(get_db)):
    try:
        articles = scrape_articles(db)

        if len(articles) == 0:
            return {
                "status": "No new articles found",
                "details": "The scraper didn't find any new articles that aren't already in the database."
            }

        added_articles = []
        for article in articles:
            try:
                summary = summarize_article(article['url'])
                db_article = Article(title=article['title'], url=article['url'], summary=summary)
                db.add(db_article)
                added_articles.append({"title": article['title'], "url": article['url']})
            except Exception as e:
                print(f"Error processing article {article['url']}: {str(e)}")

        db.commit()
        return {
            "status": f"Scraping and summarization complete",
            "added_count": len(added_articles),
            "added_articles": added_articles
        }
    except Exception as e:
        db.rollback()  # Rollback on error
        import traceback
        traceback.print_exc()
        return {"status": "Error", "message": str(e)}