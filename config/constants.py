from config.settings import API_VERSION

# Error Messages
ERROR_SIGNUP = "An error occurred during signup."
ERROR_LOGIN = "Incorrect email or password."
ERROR_LOGIN_PROCESS = "An error occurred during login."
ERROR_USER_NOT_FOUND = "User not found."
ERROR_UNAUTHORIZED = "Unauthorized access."
ERROR_USERS_FETCHING = "An error occurred while fetching users."
ERROR_USER_FETCHING = (
    "An error occurred while fetching user with user_id = {user_id}."
)
ERROR_CREATE_USER = "An error occurred during user creation."
ERROR_UPDATE_USER = "An error occurred during user update."
ERROR_DELETE_USER = "An error occurred during user deletion."
ERROR_NOTES_FETCHING = "An error occurred while fetching notes."
ERROR_NOTE_FETCHING = "An error occurred while fetching note with note_id = {note_id}."
ERROR_NOTE_NOT_FOUND = "Note not found or you don't have permission to access it."
ERROR_CREATE_NOTE = "Failed to create note."
ERROR_UPDATE_NOTE = "Failed to update note."
ERROR_DELETE_NOTE = "Failed to delete note."
ERROR_INTERNAL_SERVER = "An internal server error occurred."
ERROR_DATABASE_ERROR = "A database error occurred."
ERROR_UNEXPECTED_ERROR = "An unexpected error occurred."


# Success Messages
SUCCESS_SIGNUP = "User Signed Up Successfully."
SUCCESS_LOGIN = "User Logged In Successfully."
SUCCESS_LOGOUT = "Logged out successfully."
SUCCESS_USER_CREATED = "User with user_id = {user_id} has been created."
SUCCESS_USER_UPDATED = "User with user_id = {user_id} has been updated successfully."
SUCCESS_USER_DELETED = "User with user_id = {user_id} deleted successfully."
SUCCESS_USERS_FETCHED = "All the users fetched from database."
SUCCESS_USER_FETCHED = "User with user_id = {user_id} fetched from database."
SUCCESS_NOTE_FETCHED = "Note retrieved successfully."
SUCCESS_NOTE_CREATED = "Note created successfully."
SUCCESS_NOTE_UPDATED = "Note updated successfully."
SUCCESS_NOTE_DELETED = "Note deleted successfully."
SUCCESS_NOTES_FETCHED = "Notes retrieved successfully."

# API-related constants
API_PREFIX = f"/api/{API_VERSION}"
