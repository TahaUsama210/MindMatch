from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, Field
from .. import models, schemas, database
from ..auth import get_current_user
from ..userhelp import ai_task_generator

router = APIRouter(
    prefix="/ai",
    tags=["AI Task Generation"]
)

class GenerateTasksRequest(BaseModel):
    goal: str = Field(..., description="The goal or objective to achieve", min_length=10, max_length=1000)
    plan_id: int = Field(..., description="ID of the plan to associate tasks with")
    num_tasks: int = Field(default=5, description="Number of tasks to generate", ge=1, le=10)

class TaskSuggestionRequest(BaseModel):
    goal: str = Field(..., description="The goal to get suggestions for", min_length=10, max_length=1000)

class TaskSuggestionResponse(BaseModel):
    suggestions: str

@router.post("/generate-tasks", response_model=List[schemas.taskResponse])
def generate_tasks(
    request: GenerateTasksRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Generate AI-powered tasks based on a user's goal.
    
    - **goal**: The objective or goal you want to achieve
    - **plan_id**: The ID of the plan to associate these tasks with
    - **num_tasks**: Number of tasks to generate (1-10, default 5)
    """
    try:
        plan = db.query(models.Plan).filter(models.Plan.id == request.plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        tasks = ai_task_generator.generate_tasks_for_goal(
            goal=request.goal,
            user_id=current_user.id,
            plan_id=request.plan_id,
            db=db,
            num_tasks=request.num_tasks
        )
        
        return tasks
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate tasks: {str(e)}")

@router.post("/suggestions", response_model=TaskSuggestionResponse)
def get_suggestions(
    request: TaskSuggestionRequest,
    current_user: models.User = Depends(get_current_user)
):
    """
    Get AI-powered suggestions for achieving a goal without creating tasks.
    
    - **goal**: The objective or goal you want suggestions for
    """
    try:
        suggestions = ai_task_generator.get_task_suggestions(request.goal)
        return TaskSuggestionResponse(suggestions=suggestions)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

@router.post("/plans/{plan_id}/generate-tasks", response_model=List[schemas.taskResponse])
def generate_tasks_for_plan(
    plan_id: int,
    num_tasks: int = 5,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Generate AI tasks based on an existing plan's name and description.
    
    - **plan_id**: The ID of the plan
    - **num_tasks**: Number of tasks to generate (1-10, default 5)
    """
    try:
        plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        goal = f"{plan.name}. {plan.description or ''}"
        
        tasks = ai_task_generator.generate_tasks_for_goal(
            goal=goal,
            user_id=current_user.id,
            plan_id=plan_id,
            db=db,
            num_tasks=num_tasks
        )
        
        return tasks
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate tasks: {str(e)}")