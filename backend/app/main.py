from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
from sqlalchemy.orm import Session
from . import models, schemas, database, auth
from .routers import users, plans, tasks, ai_tasks
from .auth import get_password_hash, get_current_user

app = FastAPI(
    title="MindMatch API",
    description="A task management system with AI-powered task generation",
    version="1.0.0"
)

models.Base.metadata.create_all(bind=database.engine)

# Include routers - Make sure this line is here
app.include_router(auth.router)  # This should give you /auth/token
app.include_router(users.router)
app.include_router(plans.router)
app.include_router(tasks.router)
app.include_router(ai_tasks.router)

@app.get("/")
def root():
    return {"message": "Welcome to MindMatch API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
