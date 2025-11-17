from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database
from ..auth import get_current_user

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

@router.post("/", response_model=schemas.taskResponse)
def create_task(task: schemas.taskCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    db_user = db.query(models.User).filter(models.User.id == task.user_id).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="User does not exist")
    
    db_plan = db.query(models.Plan).filter(models.Plan.id == task.plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=400, detail="Plan does not exist")
    
    new_task = models.Task(title=task.title, description=task.description, user_id=task.user_id, plan_id=task.plan_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/", response_model=List[schemas.taskResponse])
def read_tasks(db: Session = Depends(database.get_db)):
    tasks = db.query(models.Task).all()
    return tasks

@router.put("/{task_id}", response_model=schemas.taskResponse)
def update_task(task_id: int, task: schemas.taskCreate, db: Session = Depends(database.get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_user = db.query(models.User).filter(models.User.id == task.user_id).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="User does not exist")
    
    db_plan = db.query(models.Plan).filter(models.Plan.id == task.plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=400, detail="Plan does not exist")
    
    db_task.title = task.title
    db_task.description = task.description
    db_task.user_id = task.user_id
    db_task.plan_id = task.plan_id
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(database.get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return {"detail": "Task deleted"}