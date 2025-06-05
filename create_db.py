from db import Base, engine
from models import User

Base.metadata.create_all(bind=engine)
