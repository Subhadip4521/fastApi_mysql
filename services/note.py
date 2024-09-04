from typing import Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from config.constants import (
    ERROR_CREATE_NOTE,
    ERROR_NOTE_FETCHING,
    ERROR_UPDATE_NOTE,
    ERROR_DELETE_NOTE,
    ERROR_DATABASE_ERROR,
)
from schemas.note import NoteUpdate


def find_all_notes(db: Session, page_no: int, page_size: int):
    try:
        offset = (page_no - 1) * page_size
        result = db.execute(
            text("CALL FindAllNotes(:offset, :limit)"),
            {"offset": offset, "limit": page_size},
        )
        notes = result.fetchall()

        # To get total_count
        total_count_result = db.execute(text("CALL CountAllNotes()"))
        total_count = total_count_result.scalar()

        return notes, total_count
    except SQLAlchemyError as e:
        raise Exception(ERROR_DATABASE_ERROR + ": " + str(e))


def find_note_by_id(db: Session, note_id: int):
    try:
        result = db.execute(text("CALL FindOneNote(:note_id)"), {"note_id": note_id})

        # Fetch one record from the result
        note = result.fetchone()

        # Check if the note exists
        if note is None:
            raise Exception(ERROR_NOTE_FETCHING)

        # Convert tuple to dictionary manually if needed
        note_dict = {
            "note_id": note[
                0
            ],  # Indexes should correspond to the order of fields in the procedure's result
            "title": note[1],
            "description": note[2],
            "tag": note[3],
            "note_subject": note[4],
            "timestamp": note[5],
            "author_id": note[6],
        }

        return note_dict

    except SQLAlchemyError as e:
        raise Exception(ERROR_DATABASE_ERROR + ": " + str(e))
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def create_note(db: Session, note_data: dict, author_id: int):
    try:
        # Call CreateNote procedure
        result = db.execute(
            text(
                "CALL CreateNote(:title, :description, :tag, :note_subject, :author_id)"
            ),
            {
                "title": note_data["title"],
                "description": note_data["description"],
                "tag": note_data.get("tag"),
                "note_subject": note_data.get("note_subject"),
                "author_id": author_id,
            },
        )
        db.commit()

        # Retrieve the ID of the newly created note
        note_id = result.fetchone()[0]  # type: ignore # Ensure this matches your stored procedure output

        # Get the full details of the newly created note
        result = db.execute(text("CALL GetNoteById(:note_id)"), {"note_id": note_id})
        created_note = result.fetchone()

        if created_note:
            # Convert the result to a dictionary and return
            return dict(
                zip(
                    [
                        "note_id",
                        "title",
                        "description",
                        "tag",
                        "note_subject",
                        "timestamp",
                        "author_id",
                    ],
                    created_note,
                )
            )
        else:
            return None

    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(ERROR_CREATE_NOTE + ": " + str(e))


def update_note(db: Session, note_update_data: dict):
    try:
        # Call the UpdateNote stored procedure
        result = db.execute(
            text(
                "CALL UpdateNote(:note_id, :title, :description, :tag, :note_subject, :author_id)"
            ),
            {
                "note_id": note_update_data["note_id"],
                "title": note_update_data.get("title"),
                "description": note_update_data.get("description"),
                "tag": note_update_data.get("tag"),
                "note_subject": note_update_data.get("note_subject"),
                "author_id": note_update_data[
                    "author_id"
                ],  # Ensure this is present and correct
            },
        )
        db.commit()

        # Fetch the updated note details
        result = db.execute(
            text("CALL GetNoteById(:note_id)"), {"note_id": note_update_data["note_id"]}
        )
        updated_note = result.fetchone()

        if updated_note:
            # Map the result to a dictionary if necessary
            updated_note_dict = dict(
                zip(
                    [
                        "note_id",
                        "title",
                        "description",
                        "tag",
                        "note_subject",
                        "timestamp",
                        "author_id",
                    ],
                    updated_note,
                )
            )
            return updated_note_dict
        return None
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Failed to update note: {str(e)}")


def delete_note(db: Session, note_id: int, author_id: int) -> bool:
    try:
        result = db.execute(
            text("CALL DeleteNote(:note_id, :author_id)"),
            {"note_id": note_id, "author_id": author_id},
        )
        db.commit()

        # Check if the deletion was successful
        if result.rowcount > 0: # type: ignore
            return True
        else:
            return False
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Failed to delete note: {str(e)}")
