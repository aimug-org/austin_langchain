from typing_extensions import Optional
from pydantic import BaseModel, Field

class Board(BaseModel):
    """Base schema for board operations"""
    board_id: str = Field(..., description="ID of the board")
    name: Optional[str] = Field(None, description="Name of the board")
    description: Optional[str] = Field(None, description="Board description")

class BoardList(BaseModel):
    """Schema for board list operations - used when list is part of a board"""
    list_id: str = Field(..., description="ID of the list")
    name: Optional[str] = Field(None, description="Name of the list")
    board_id: Optional[str] = Field(None, description="ID of the board containing the list")
    position: Optional[str] = Field("bottom", description="Position in the board (top, bottom, or a positive number)")

class CardList(BaseModel):
    """Schema for card list operations - used when list contains cards"""
    list_id: str = Field(..., description="ID of the list")
    name: Optional[str] = Field(None, description="Name of the list")
    position: Optional[str] = Field("bottom", description="Position in the board (top, bottom, or a positive number)")

class Card(BaseModel):
    """Base schema for card operations"""
    card_id: str = Field(..., description="ID of the card")
    name: Optional[str] = Field(None, description="Name of the card")
    description: Optional[str] = Field(None, description="Description of the card")
    list_id: Optional[str] = Field(None, description="ID of the list containing the card")
    position: Optional[str] = Field("bottom", description="Position in the list (top, bottom, or a positive number)")
    due_date: Optional[str] = Field(None, description="Due date in ISO format")
