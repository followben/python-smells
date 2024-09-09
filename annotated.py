from datetime import datetime
from typing import Any
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import uvicorn
import time

# Talking point: use of hardcoded sqlite database
engine = create_engine("sqlite:///./test.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Issue: Global variable for configuration (should use environment variables or config files)
DEBUG = True

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    # Issue: user and password should be unique
    username = Column(String, index=True) 
    email = Column(String, index=True)
    # Error: Using String for password (should use specialized password hashing)
    password = Column(String)
    # Issue: Inefficient use of Boolean for status
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)
    created_at = Column(DateTime)
    # Issue: Redundant column (can be calculated)
    age = Column(Integer)
    # Issue: Using inefficient Text type for a potentially short field
    bio = Column(Text)
    articles = relationship("Article", back_populates="author")

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    # Issue: Using inefficient Text type for content
    content = Column(Text)
    # Error: Using String for date (should use DateTime)
    published_at = Column(String)
    # Error: Incorrect data type for view count (should be Integer)
    view_count = Column(String)
    # Issue: Boolean for category (limited to two options)
    is_featured = Column(Boolean, default=False)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="articles")


# Talking point: Would you auto-create schema
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Error: Incorrect dependency injection (should use contextlib.contextmanager or yield and close the connection)
def get_db():
    db = SessionLocal()
    return db

# Issue: Needs annotated type hints
# Issue: Missing validation/ serialization for both requests and responses
@app.post("/users/")
def create_user(username: Any, email: Any, password: Any, db: SessionLocal = Depends(get_db)):
    try:
        # Issue: use of datetime.now() instead of utcnow()
        # Error: storing password in plaintext
        db_user = User(username=username, email=email, password=password, created_at=datetime.now())
        db.add(db_user)
        # Issue: use of commit as you go instead of beginning up a trasaction and using flush()
        db.commit()
        return {"id": db_user.id, "username": db_user.username, "email": db_user.email}
    except Exception as e:
        return {"error": str(e)}  # Error: Not handling exceptions correctly (potentially leaking sensitive info)


@app.get("/users/{username}")
def get_user(username: str, db: SessionLocal = Depends(get_db)):
    # Error: Using string interpolation instead of parameters (SQL injection risk)
    # Issue: Use the ORM (or query builder) to return a model object instead of raw SQL/ rows
    user = db.execute(f"SELECT * FROM users WHERE username = '{username}'").first()
    if user is None:
        raise Exception("User not found") # Error: Not raising HTTPException/ 404
    # Issue: Inconsistent response shape
    # Talking point: Use on natural keys
    # Error: Leaking sensitive information
    return {"username": user.username, "email": user.email, "password": user.password} 

# Issue: Not using type hints consistently
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/users")
def get_all_users(db: SessionLocal = Depends(get_db)):
    # Error: Use of SQLAlchemy 1.x
    users = db.query(User).all()
    result = []
    for user in users:
        articles = db.query(Article).filter(Article.author_id == user.id).all()  # Issue: Inefficient database querying (N+1 problem)
        processed_articles = []
        for article in articles:
            processed_articles.append({
                "id": article.id,
                "title": article.title,
                "content": article.content[:100]  # Inefficient processing
            })
        # Issue: Inconsistent response shape
        result.append({
            "id": user.id,
            "username": user.username,
            "articles": processed_articles
        })
    return result

# Issue: Not using async where appropriate
@app.get("/slow")
def slow_operation():
    time.sleep(5)  # Just faking a slow, long-running operation
    return {"result": "Done"}

# Talking point: hardcoded uvicorn command/ config
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=DEBUG)