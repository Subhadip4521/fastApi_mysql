from pydantic import BaseModel  # type: ignore

class User(BaseModel):
    name: str
    email: str
    password: str
