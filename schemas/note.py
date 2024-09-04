from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class NoteBase(BaseModel):
    title: str
    description: str
    tag: Optional[str] = None
    note_subject: Optional[str] = None


class NoteCreate(NoteBase):
    author_name: str


class NoteRequest(BaseModel):
    note_id: int


class NoteIdRequest(BaseModel):
    note_id: int


class NoteUpdate(BaseModel):
    note_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    tag: Optional[str] = None
    note_subject: Optional[str] = None

    class Config:
        from_attributes = True


class NoteInDB(NoteBase):
    note_id: int
    timestamp: datetime
    author_id: int

    class Config:
        from_attributes = True


class NotesListRequest(BaseModel):
    pageNo: int = Field(..., ge=1)  # Page number should be >= 1
    pageSize: int = Field(..., ge=1)  # Page size should be >= 1


class NoteResponse(BaseModel):
    status: bool
    detail: str
    data: Optional[NoteInDB]  # Use Optional to handle the case where no note is found


class NotesListResponse(BaseModel):
    status: bool
    detail: str
    total_count: int
    data: List[NoteInDB]


class DeleteNoteRequest(BaseModel):
    note_id: int


class DeleteNoteResponse(BaseModel):
    status: bool
    detail: str
    data: Optional[str] = None
