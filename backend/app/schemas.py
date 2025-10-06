from pydantic import BaseModel

class userBase(BaseModel):
    email: str
    name: str

class userCreate(userBase):
    password: str  # Extra field for creation

class userResponse(userBase):
    id: int

    class Config:
        from_attributes = True



class planBase(BaseModel):
    name: str
    description: str | None = None
    goal : str | None = None    

class planCreate(planBase):
    pass

class planResponse(planBase):
    id: int
    user_id: int | None = None

    class Config:
        from_attributes = True



class taskBase(BaseModel):  
    title: str
    description: str | None = None
    user_id: int
    plan_id: int

class taskCreate(taskBase):
    pass

class taskResponse(taskBase):
    id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str

