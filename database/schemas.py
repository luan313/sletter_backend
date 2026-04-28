from sqlalchemy import Column, Integer, String, Date, Boolean
from database import Base 

class MovieDB(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, index=True, nullable=False)    
    title = Column(String, nullable=False)
    release_date = Column(Date, nullable=True)    
    poster_path = Column(String, nullable=True)
    watched = Column(Boolean, default=False)