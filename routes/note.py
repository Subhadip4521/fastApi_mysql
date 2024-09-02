from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from typing import List
from config.db import SessionLocal
from schemas.note import (
    NoteInDB,
    NoteResponse,
    NoteCreate,
    NoteUpdate,
    NotesListResponse,
    NotesListRequest,
    NoteRequest,
    NoteIdRequest,
    DeleteNoteRequest,
)
from schemas.user import User
from models.note import Note
from routes.user import get_current_user

note = APIRouter(
    prefix="/notes",
    tags=["NOTES"],
)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Route to create a new note
@note.post("/create", response_model=NoteResponse)
def create_note(
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_note = Note(
        title=note_data.title,
        description=note_data.description,
        tag=note_data.tag,
        note_subject=note_data.note_subject,
        timestamp=datetime.utcnow(),
        author_id=current_user.user_id,  # Associate the note with the logged-in user
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    return NoteResponse(status=True, detail="Note created successfully", data=db_note)


# Route to retrieve a single note by note_id (POST request)
@note.post("/find_one", response_model=NoteResponse)
def get_note(
    note_request: NoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        db_note = (
            db.query(Note)
            .filter(
                Note.note_id == note_request.note_id,
                Note.author_id == current_user.user_id,
            )
            .first()
        )

        if not db_note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found or you don't have permission to view this note",
            )

        return NoteResponse(
            status=True, detail="Note retrieved successfully", data=db_note
        )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# Route to update an existing note by note_id (POST request)
@note.post("/update", response_model=NoteResponse)
def update_note(
    note_update_request: NoteIdRequest,
    note_data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # Retrieve the note to be updated
        db_note = (
            db.query(Note)
            .filter(
                Note.note_id == note_update_request.note_id,
                Note.author_id == current_user.user_id,
            )
            .first()
        )

        if not db_note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
            )

        # Update the note with provided data
        update_data = note_data.dict(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_note, key, value)

        db_note.timestamp = datetime.utcnow()  # type: ignore
        db.commit()
        db.refresh(db_note)

        return NoteResponse(
            status=True, detail="Note updated successfully", data=db_note
        )

    except SQLAlchemyError as e:
        # Handle SQLAlchemy-specific errors
        db.rollback()  # Rollback the transaction in case of an error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred: {str(e)}",
        )
    except Exception as e:
        # Handle other general errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


# Route to list all notes for the logged-in user (POST request)
@note.post("/find_all", response_model=NotesListResponse)
def list_notes(
    request: NotesListRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Calculate pagination
    offset = (request.pageNo - 1) * request.pageSize # type: ignore
    limit = request.pageSize

    # Get total count of notes
    total_count = db.query(Note).filter(Note.author_id == current_user.user_id).count()

    # Fetch paginated notes
    notes = (
        db.query(Note)
        .filter(Note.author_id == current_user.user_id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return NotesListResponse(
        status=True,
        detail="Notes retrieved successfully",
        total_count=total_count,
        data=notes, # type: ignore
    )


# Route to delete a note by note_id (POST request)
@note.post("/delete", response_model=NoteResponse)
def delete_note(
    delete_request: DeleteNoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # Fetch the note to be deleted
        db_note = (
            db.query(Note)
            .filter(
                Note.note_id == delete_request.note_id,
                Note.author_id == current_user.user_id,
            )
            .first()
        )

        # Check if the note exists and belongs to the current user
        if not db_note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found or you don't have permission to delete this note",
            )

        # Delete the note
        db.delete(db_note)
        db.commit()

        # Return response
        return NoteResponse(
            status=True,
            detail=f"Note with note_id = {delete_request.note_id} deleted successfully",
            data=NoteInDB(
                **db_note.__dict__
            ),  # Return the deleted note's data or an empty object if appropriate
        )

    except SQLAlchemyError as e:
        # Handle SQLAlchemy errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the note: " + str(e),
        )
    except Exception as e:
        # Handle other possible errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred: " + str(e),
        )
