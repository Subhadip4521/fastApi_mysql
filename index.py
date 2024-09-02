from fastapi import FastAPI
from routes.user import user
from routes.note import note

app = FastAPI(
    title="My API",
    description="API with JWT Authentication",
    version="1.0.0",
    openapi_tags=[
        {"name": "AUTH", "description": "Operations with authentication"},
        {"name": "USERS", "description": "Operations with users"},
    ],
    openapi_url="/openapi.json",
)


app.include_router(user)
app.include_router(note)
