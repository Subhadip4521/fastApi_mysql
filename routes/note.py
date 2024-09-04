from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from services.note import (
    create_note,
    delete_note,
    find_all_notes,
    find_note_by_id,
    update_note,
)
from utils.dependencies import get_db, get_current_user
from config.constants import (
    ERROR_NOTE_FETCHING,
    ERROR_NOTES_FETCHING,
    ERROR_NOTE_NOT_FOUND,
    ERROR_CREATE_NOTE,
    ERROR_UPDATE_NOTE,
    ERROR_DELETE_NOTE,
    SUCCESS_NOTE_CREATED,
    SUCCESS_NOTE_UPDATED,
    SUCCESS_NOTE_DELETED,
    SUCCESS_NOTES_FETCHED,
    SUCCESS_NOTE_FETCHED,
    API_PREFIX,
)
from schemas.auth import TokenData, ResponseModel
from schemas.note import (
    DeleteNoteRequest,
    NoteInDB as NoteSchema,
    NoteCreate,
    NoteUpdate,
    NoteIdRequest,
    NoteResponse,
    NotesListResponse,
    DeleteNoteResponse,
    NotesListRequest,
)

note = APIRouter(
    prefix="/notes",
    tags=["Notes"],
)


@note.post(f"{API_PREFIX}/find_all", response_model=NotesListResponse)
async def find_all_notes_route(
    request: NotesListRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> NotesListResponse:
    try:
        page_no = request.pageNo
        page_size = request.pageSize

        notes, total_count = find_all_notes(db, page_no, page_size)

        # Convert notes to list of NoteInDB instances
        note_list = (
            [
                NoteSchema(
                    **dict(
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
                            note,
                        )
                    )
                )
                for note in notes
            ]
            if notes
            else []
        )

        return NotesListResponse(
            status=True,
            detail=SUCCESS_NOTES_FETCHED,
            total_count=total_count,  # type: ignore
            data=note_list,
        )
    except Exception as e:
        return NotesListResponse(
            status=False,
            detail=f"{ERROR_NOTES_FETCHING}: {str(e)}",
            total_count=0,
            data=[],
        )


@note.post(f"{API_PREFIX}/find_one", response_model=NoteResponse)
async def find_one_note_route(
    request: NoteIdRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> NoteResponse:
    try:
        note_data = find_note_by_id(db, request.note_id)
        if not note_data:
            raise HTTPException(status_code=404, detail=ERROR_NOTE_NOT_FOUND)

        # Convert the note data to NoteInDB instance
        note_in_db = NoteSchema(**note_data)

        return NoteResponse(
            status=True,
            detail=SUCCESS_NOTE_FETCHED.format(note_id=request.note_id),
            data=note_in_db,
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        return NoteResponse(
            status=False,
            detail=f"{ERROR_NOTE_FETCHING} with note_id = {request.note_id}: {str(e)}",
            data=None,
        )


@note.post(f"{API_PREFIX}/create", response_model=NoteResponse)
async def create_note_route(
    note: NoteCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> NoteResponse:
    try:
        # Convert NoteCreate to dictionary
        note_data = note.dict()
        # Get author_id from current_user
        author_id = current_user.user_id

        # Call create_note with note data and author_id
        new_note = create_note(
            db, note_data, author_id # type: ignore
        )  # Ensure create_note returns the expected format

        if not new_note:
            return NoteResponse(status=False, detail="Error creating note", data=None)

        # Convert result to NoteInDB
        note_response = NoteSchema(**new_note)  # Use NoteInDB if it's the correct schema

        return NoteResponse(
            status=True,
            detail=f"{SUCCESS_NOTE_CREATED} with note_id={new_note['note_id']}",
            data=note_response,
        )
    except Exception as e:
        return NoteResponse(
            status=False, detail=f"{ERROR_CREATE_NOTE}: {str(e)}", data=None
        )


@note.post(f"{API_PREFIX}/update", response_model=NoteResponse)
async def update_note_route(
    note_update: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> NoteResponse:
    try:
        note_data = note_update.dict()
        note_data["author_id"] = current_user.user_id  # Implicitly set author_id

        updated_note = update_note(db, note_data)  # Call the function

        if not updated_note:
            return NoteResponse(status=False, detail=ERROR_UPDATE_NOTE, data=None)

        return NoteResponse(
            status=True,
            detail=f"{SUCCESS_NOTE_UPDATED} with note_id={note_update.note_id}",
            data=NoteSchema(**updated_note),
        )
    except Exception as e:
        return NoteResponse(
            status=False, detail=f"Failed to update note: {str(e)}", data=None
        )


@note.post(f"{API_PREFIX}/delete", response_model=DeleteNoteResponse)
async def delete_note_route(
    delete_request: DeleteNoteRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> DeleteNoteResponse:
    try:
        # Extract the note_id from the request
        note_id = delete_request.note_id
        author_id = current_user.user_id  # Use the current user's ID

        # Call the function to delete the note
        is_deleted = delete_note(db, note_id, author_id) # type: ignore

        if is_deleted:
            return DeleteNoteResponse(
                status=True, detail=f"Note with note_id={note_id} deleted successfully."
            )
        else:
            return DeleteNoteResponse(
                status=False,
                detail="Failed to delete note: Note not found or unauthorized.",
            )
    except Exception as e:
        return DeleteNoteResponse(
            status=False, detail=f"Failed to delete note: {str(e)}"
        )
