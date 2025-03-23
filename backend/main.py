from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from scrapper import scrape_articles
from summarizer import summarize_article
import os

app = FastAPI()

# Test DB URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5433/technews_test")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False)
    summary = Column(String(500))

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency as a function
def get_db() -> Session:
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

@app.get("/summaries")
def get_summaries(db: Session = Depends(get_db)):
    articles = db.query(Article).all()
    return [{"title": a.title, "url": a.url, "summary": a.summary} for a in articles]

@app.post("/scrape-and-summarize")
def scrape_and_summarize(db: Session = Depends(get_db)):
    articles = scrape_articles()
    for article in articles:
        summary = summarize_article(article['url'])
        db_article = Article(title=article['title'], url=article['url'], summary=summary)
        db.add(db_article)
    db.commit()
    return {"status": "Scraping and summarization complete"}