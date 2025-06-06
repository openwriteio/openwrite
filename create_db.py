from db import Base, engine
from models import User, Blog, Post

Base.metadata.create_all(bind=engine)
