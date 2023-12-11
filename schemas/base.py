from pydantic import BaseModel


class BaseComplaint(BaseModel):
    title: str
    description: str
    photo_url: str
    amount: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: str

    class Config:
        orm_mode = True
