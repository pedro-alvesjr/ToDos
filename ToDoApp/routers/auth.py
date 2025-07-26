from typing import Annotated
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session


router = APIRouter()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto') 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


class CreateUserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    role: str


@router.post("/auth", status_code=status.HTTP_201_CREATED)
def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_request = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        role = create_user_request.role,
        is_active = True
    )

    db.add(create_user_request)
    db.commit()