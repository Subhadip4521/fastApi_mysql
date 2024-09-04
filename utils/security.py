from fastapi.security import OAuth2PasswordBearer
from config.settings import TOKEN_URL


# Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)
