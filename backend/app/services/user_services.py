from sqlalchemy.orm import Session
from fastapi import HTTPException
from .. import models, schemas
from ..auth import get_password_hash

class UserService:
    @staticmethod
    def create_user(user: schemas.userCreate, db: Session):
        # Check if user exists
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        new_user = models.User(
            email=user.email, 
            name=user.name, 
            hashed_password=get_password_hash(user.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    
    @staticmethod
    def get_all_users(db: Session):
        return db.query(models.User).all()
    
    @staticmethod
    def get_user_by_id(user_id: int, db: Session):
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    @staticmethod
    def update_user(user_id: int, user_data: schemas.userCreate, db: Session):
        user = UserService.get_user_by_id(user_id, db)
        user.email = user_data.email
        user.name = user_data.name
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(user_id: int, db: Session):
        user = UserService.get_user_by_id(user_id, db)
        db.delete(user)
        db.commit()
        return {"detail": "User deleted"}