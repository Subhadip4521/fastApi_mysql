from fastapi import FastAPI
from routes.auth import auth
from routes.user import user
from routes.note import note
from config.settings import API_VERSION

app = FastAPI(
    title="FastAPI",
    description="API with JWT Authentication",
    version=API_VERSION,
    openapi_url="/fastapi.json",
)


app.include_router(auth)
app.include_router(user)
app.include_router(note)
