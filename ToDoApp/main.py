from fastapi import FastAPI, Depends
import models
from sqlalchemy.orm import Session
from models import Todos
from database import engine, SessionLocal
from typing import Annotated


app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
def read_all(db: db_dependency):
    return db.query(Todos).all()
