from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Path
from pydantic import BaseModel
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import UTC, timedelta, datetime
from .auth import get_current_user


router = APIRouter(
    prefix='/users',
    tags=['users']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto') 
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/user')
def get_user(db: db_dependency, user: user_dependency):
    return db.query(Users).filter(Users.id == user.get('id')).first()

@router.put('/users/{user_id}')
def change_password(db: db_dependency, 
                    user: user_dependency, 
                    change_password_request: str = Path(min_length=5)):
    user.get('hashed_password') = bcrypt_context.hash(change_password_request)

