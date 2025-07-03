from sqlalchemy import Column, Integer, String, Date, Text, DateTime, Index
from sqlalchemy.sql import func
from openwrite.db.base import Base

class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)

class Home(Base):
    __tablename__ = "home"

    id = Column(Integer, primary_key=True)
    language = Column(String(10))
    name = Column(String(100), nullable=False)
    type = Column(String(30), nullable=False)
    url = Column(String(200))
    content = Column(Text)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(120), nullable=True)
    verified = Column(Integer, nullable=False)
    admin = Column(Integer, nullable=False)

class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True)
    owner = Column(Integer, nullable=False)
    name = Column(String(64), nullable=False)
    title = Column(String(64), nullable=False)
    index = Column(String(10), nullable=False)
    access = Column(String(10), nullable=False)
    description_raw = Column(Text, nullable=False)
    description_html = Column(Text, nullable=False)
    css = Column(Text)
    pub_key = Column(Text, nullable=False)
    priv_key = Column(Text, nullable=False)
    followers = Column(Text)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime)
    theme = Column(String(50), nullable=False)

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    blog = Column(Integer, nullable=False)
    title = Column(String(128), nullable=False)
    link = Column(String(64), nullable=False)
    date = Column(DateTime, default=func.current_date())
    content_raw = Column(Text, nullable=False)
    content_html = Column(Text, nullable=False)
    author = Column(String(10), nullable=False)
    feed = Column(String(10), nullable=False)
    updated = Column(DateTime)

class View(Base):
    __tablename__ = "views"

    id = Column(Integer, primary_key=True)
    hash = Column(String(64), nullable=False)
    blog = Column(Integer, nullable=False)
    post = Column(Integer, nullable=False)
    date = Column(DateTime)
    agent = Column(String(300))

    __table_args__ = (
        Index("ix_views_blog_post", "blog", "post"),
    )

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True)
    hash = Column(String(64), nullable=False)
    blog = Column(Integer, nullable=False)
    post = Column(Integer, nullable=False)
    date = Column(DateTime)

