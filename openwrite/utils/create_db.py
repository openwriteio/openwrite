from .db import init_engine
from .models import User, Blog, Post, View, Settings, Home, Like, Settings
from openwrite.db.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os
import json



def init_db(dbtype, dbpath):
    engine = init_engine(dbtype, dbpath)
    Base.metadata.create_all(bind=engine)
    
