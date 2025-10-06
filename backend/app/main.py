from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
from sqlalchemy.orm import Session
from . import models, schemas, database, auth
from .auth import get_password_hash, get_current_user

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

# Include auth router
app.include_router(auth.router)



#USER ENDPOINTS

@app.post("/users/", response_model=schemas.userResponse)
def create_user(user: schemas.userCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(email=user.email, name=user.name, hashed_password=get_password_hash(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get ("/users/", response_model=List[schemas.userResponse])
def read_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    return users

@app.put("/users/{user_id}", response_model=schemas.userResponse)
def update_user(user_id: int, user: schemas.userCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.email = user.email
    db_user.name = user.name

    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}




#PLAN ENDPOINTS

@app.post("/plans/", response_model=schemas.planResponse)
def create_plan(plan: schemas.planCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    db_plan = db.query(models.Plan).filter(models.Plan.name == plan.name).first()
    if db_plan:
        raise HTTPException(status_code=400, detail="Plan name already exists")
    new_plan = models.Plan(name=plan.name, description=plan.description)
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

@app.get("/plans/", response_model=List[schemas.planResponse])
def read_plans(db: Session = Depends(database.get_db)):
    plans = db.query(models.Plan).all()
    return plans

@app.put("/plans/{plan_id}", response_model=schemas.planResponse)
def update_plan(plan_id: int, plan: schemas.planCreate, db: Session = Depends
(database.get_db)):
    db_plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    db_plan.name = plan.name
    db_plan.description = plan.description

    db.commit()
    db.refresh(db_plan)
    return db_plan

@app.delete("/plans/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(database.get_db)):
    db_plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    db.delete(db_plan)
    db.commit()
    return {"detail": "Plan deleted"}





#TASK ENDPOINTS
@app.post("/tasks/", response_model=schemas.taskResponse)
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

@app.get("/tasks/", response_model=List[schemas.taskResponse])
def read_tasks(db: Session = Depends(database.get_db)):
    tasks = db.query(models.Task).all()
    return tasks

@app.put("/tasks/{task_id}", response_model=schemas.taskResponse)
def update_task(task_id: int, task: schemas.taskCreate, db: Session = Depends
(database.get_db)):
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

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(database.get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return {"detail": "Task deleted"}



