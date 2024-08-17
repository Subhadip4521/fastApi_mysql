from fastapi import FastAPI  # type: ignore
from routes.user import user

app= FastAPI()

app.include_router(user)
