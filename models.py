from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.sql import func
from db import Base

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

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    blog = Column(Integer, nullable=False)
    title = Column(String(128), nullable=False)
    link = Column(String(64), nullable=False)
    date = Column(Date, default=func.current_date())
    content_raw = Column(Text, nullable=False)
    content_html = Column(Text, nullable=False)
    author = Column(String(10), nullable=False)
