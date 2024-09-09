
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

engine = create_engine("sqlite:///./test.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

DEBUG = True

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)
    created_at = Column(DateTime)
    age = Column(Integer)
    bio = Column(Text)
    articles = relationship("Article", back_populates="author")

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    published_at = Column(String)
    view_count = Column(String)
    is_featured = Column(Boolean, default=False)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="articles")


Base.metadata.create_all(bind=engine)