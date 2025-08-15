from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from models import Todos
from database import SessionLocal
from typing import Annotated
from pydantic import BaseModel, Field
from .auth import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=1, max_length=25)
    description: str = Field(min_length=1, max_length=50)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@router.get("/", status_code=status.HTTP_200_OK)
def read_all(user: user_dependency, db: db_dependency):
    """
    Retrieve all todos for the authenticated user.
    """
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
def read_todo(user: user_dependency, 
              db: db_dependency, 
              todo_id: int = Path(gt=0)):
    """
    Retrieve a specific todo by its ID for the authenticated user.
    Raises 404 if the todo does not exist or does not belong to the user.
    """
    if user is None:
        return HTTPException(status_code=401, detail='User not authenticated.')
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    
    if todo_model:
        return todo_model
    
    raise HTTPException(status_code=404, detail='ID not found')


@router.post("/todo", status_code=status.HTTP_201_CREATED)
def create_todo(user: user_dependency, 
                db: db_dependency, 
                todo_request: TodoRequest):
    """
    Create a new todo item for the authenticated user.
    """
    if user is None:
        raise HTTPException(status_code=401, detail='User not authenticated.')
    
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))

    db.add(todo_model)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_todo(user: user_dependency, 
                db: db_dependency, 
                todo_request: TodoRequest,
                todo_id: int = Path(gt=0)):
    """
    Update an existing todo by ID for the authenticated user.
    Raises 404 if the todo does not exist or does not belong to the user.
    """
    if user is None:
        return HTTPException(status_code=401, detail='User not authenticated.')

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    
    if todo_model is None:
        raise HTTPException(status_code=404, detail='ID not found.')
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(user: user_dependency, 
                db: db_dependency,
                todo_id: int = Path(gt=0)):
    """
    Delete a todo by ID for the authenticated user.
    Raises 404 if the todo does not exist or does not belong to the user.
    """
    if user is None:
        return HTTPException(status_code=401, detail='User not authenticated.')

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    
    if todo_model is None:
        raise HTTPException(status_code=404, detail='ID not found.')
    
    db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).delete()
    db.commit()
