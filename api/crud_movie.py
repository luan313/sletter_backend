import requests
import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from database.schemas import MovieDB

from api.models import Movie

load_dotenv()

TOKEN_TMDB = os.getenv("TOKEN_TMDB", "DEFAULT_TOKEN_TMDB")

router = APIRouter()

@router.post("/add_movie")
def add_movie(movie: Movie, db: Session = Depends(get_db)):
    existent_movie = db.query(MovieDB).filter(MovieDB.tmdb_id == movie.tmdb_id).first()

    if existent_movie:
        raise HTTPException(
            status_code=400, 
            detail="Este filme já está na sua biblioteca!"
        )
    
    new_movie = MovieDB(
        tmdb_id=movie.tmdb_id,
        title=movie.title,
        release_date=movie.release_date,
        poster_path=movie.poster_path,
        watched=movie.watched,
    )

    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)

    return {
        "status": "success",
        "message": "Filme adicionado com sucesso!",
        "movie": new_movie,
    }

@router.get("/search_movie")
def search_movie(query: str):
    url = f"https://api.themoviedb.org/3/search/movie?query={query}&language=pt-BR"
    headers = {"Authorization": "Bearer SEU_TOKEN_SECRETO_AQUI"}
    
    resposta = requests.get(url, headers=headers)
    return resposta.json()["results"]