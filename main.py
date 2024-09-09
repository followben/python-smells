from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from typing import Any
import uvicorn
import time

from models import Article, SessionLocal, User

DEBUG = True

app = FastAPI()

def get_db():
    db = SessionLocal()
    return db

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.put("/users/")
def create_user(username: Any, email: Any, password: Any, db: SessionLocal = Depends(get_db)):
    try:
        db_user = User(username=username, email=email, password=password, created_at=datetime.now())
        db.add(db_user)
        db.commit()
        return {"id": db_user.id, "username": db_user.username, "email": db_user.email}
    except Exception as e:
        return {"error": str(e)}

@app.get("/users/{username}")
def get_user(username: str, db: SessionLocal = Depends(get_db)):
    user = db.execute(f"SELECT * FROM users WHERE username = '{username}'").first()
    if user is None:
        raise Exception("User not found")
    return {"id": user.id, "username": user.username, "email": user.email, "password": user.password}

@app.get("/users")
def get_all_users(db: SessionLocal = Depends(get_db)):
    users = db.query(User).all()
    result = []
    for user in users:
        articles = db.query(Article).filter(Article.author_id == user.id).all()
        processed_articles = []
        for article in articles:
            processed_articles.append({
                "id": article.id,
                "title": article.title,
                "content": article.content[:100]
            })
        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "articles": processed_articles
        })
    return result

@app.get("/slow")
def slow_operation():
    time.sleep(5)
    return {"result": "Done"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=DEBUG)