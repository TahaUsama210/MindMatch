from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database
from ..auth import get_current_user

router = APIRouter(
    prefix="/plans",
    tags=["plans"]
)

@router.post("/", response_model=schemas.planResponse)
def create_plan(plan: schemas.planCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    db_plan = db.query(models.Plan).filter(models.Plan.name == plan.name).first()
    if db_plan:
        raise HTTPException(status_code=400, detail="Plan name already exists")
    new_plan = models.Plan(name=plan.name, description=plan.description)
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

@router.get("/", response_model=List[schemas.planResponse])
def read_plans(db: Session = Depends(database.get_db)):
    plans = db.query(models.Plan).all()
    return plans

@router.put("/{plan_id}", response_model=schemas.planResponse)
def update_plan(plan_id: int, plan: schemas.planCreate, db: Session = Depends(database.get_db)):
    db_plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    db_plan.name = plan.name
    db_plan.description = plan.description
    db.commit()
    db.refresh(db_plan)
    return db_plan

@router.delete("/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(database.get_db)):
    db_plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    db.delete(db_plan)
    db.commit()
    return {"detail": "Plan deleted"}