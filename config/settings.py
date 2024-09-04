from decouple import config

# Environment-specific constants
SECRET_KEY = config("SECRET_KEY", default="your_secret_key")
ALGORITHM = config("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = config(
    "ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int
)
DATABASE_URL = config("DATABASE_URL")

# Other configuration variables
HOST = config("HOST", default="http://localhost:8000")
API_VERSION = "v1"
TOKEN_URL= "/login"
