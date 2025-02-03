# Standard library
from typing import Dict, List as PyList, Union
from typing_extensions import Optional

# Third-party
from mcp.server.fastmcp import FastMCP

# Local
from settings import settings
from trello_client import TrelloClient
from trello_errors import TrelloError, handle_trello_error
from trello_schemas import Board, BoardList, CardList, Card

# Initialize the MCP server
mcp = FastMCP("TrelloMCP")

# Initialize the Trello API client with settings
trello_client = TrelloClient(
    api_key=settings.TRELLO_API_KEY,
    token=settings.TRELLO_TOKEN,
    base_url=settings.TRELLO_API_BASE_URL
)

@mcp.tool()
def get_board_lists(params: Board) -> Dict[str, Union[PyList[BoardList], str]]:
    """
    Fetch all lists from a specific Trello board.
    
    Args:
        params: Board object containing board_id
    
    Returns:
        List of BoardList objects containing name and ID, or error message.
    """
    try:
        lists = trello_client.get_board_lists(params.board_id)
        return {"lists": lists}
    except TrelloError as e:
        return handle_trello_error(e)

@mcp.tool()
def list_boards() -> Dict[str, Union[PyList[Board], str]]:
    """
    Fetch all Trello boards for the authenticated user.
    
    Returns:
        List of Board objects containing name and ID, or error message.
    """
    try:
        boards = trello_client.get_boards()
        return {"boards": boards}
    except TrelloError as e:
        return handle_trello_error(e)

@mcp.tool()
def create_board(params: Board) -> Dict[str, str]:
    """
    Create a new Trello board.
    
    Args:
        params: Board object containing name and optional description
        
    Returns:
        Dict containing the ID of the created board or error message
    """
    try:
        board_id = trello_client.create_board(params.name, params.description)
        return {"id": board_id}
    except TrelloError as e:
        return handle_trello_error(e)

@mcp.tool()
def create_list(params: BoardList) -> Dict[str, str]:
    """
    Create a new list in a board.
    
    Args:
        params: BoardList object containing name, board_id, and optional position
        
    Returns:
        Dict containing the ID of the created list or error message
    """
    try:
        list_id = trello_client.create_list(
            params.name,
            params.board_id,
            params.position
        )
        return {"id": list_id}
    except TrelloError as e:
        return handle_trello_error(e)

@mcp.tool()
def create_card(params: Card) -> Dict[str, str]:
    """
    Create a new card in a list.
    
    Args:
        params: Card object containing list_id, name, and optional description
        
    Returns:
        Dict containing the ID of the created card or error message
    """
    try:
        card_id = trello_client.create_card(
            params.list_id,
            params.name,
            params.description or ""
        )
        return {"id": card_id}
    except TrelloError as e:
        return handle_trello_error(e)

@mcp.tool()
def move_card(params: Card) -> Dict[str, bool]:
    """
    Move a card to a different list.
    
    Args:
        params: Card object containing card_id, list_id, and optional position
        
    Returns:
        Dict indicating success or error message
    """
    try:
        trello_client.move_card(
            params.card_id,
            params.list_id,
            params.position
        )
        return {"success": True}
    except TrelloError as e:
        return handle_trello_error(e)

@mcp.tool()
def update_card(params: Card) -> Dict[str, bool]:
    """
    Update card details.
    
    Args:
        params: Card object containing card_id and optional name, description, due_date
        
    Returns:
        Dict indicating success or error message
    """
    try:
        trello_client.update_card(
            params.card_id,
            params.name,
            params.description,
            params.due_date
        )
        return {"success": True}
    except TrelloError as e:
        return handle_trello_error(e)

@mcp.tool()
def get_list_cards(params: CardList) -> Dict[str, Union[PyList[Card], str]]:
    """
    Fetch all cards in a list.
    
    Args:
        params: CardList object containing list_id
    
    Returns:
        List of Card objects containing name, ID, and description, or error message.
    """
    try:
        cards = trello_client.get_list_cards(params.list_id)
        return {"cards": cards}
    except TrelloError as e:
        return handle_trello_error(e)

@mcp.tool()
def get_board_lists_with_cards(params: Board) -> Dict[str, Union[PyList[BoardList], str]]:
    """
    Fetch all lists in a board along with their cards.
    
    Args:
        params: Board object containing board_id
    
    Returns:
        List of BoardList objects containing name, ID, and cards array, or error message.
    """
    try:
        lists = trello_client.get_board_lists_with_cards(params.board_id)
        return {"lists": lists}
    except TrelloError as e:
        return handle_trello_error(e)

@mcp.tool()
def archive_card(params: Card) -> Dict[str, bool]:
    """
    Archive a card.
    
    Args:
        params: Card object containing card_id
        
    Returns:
        Dict indicating success or error message
    """
    try:
        trello_client.archive_card(params.card_id)
        return {"success": True}
    except TrelloError as e:
        return handle_trello_error(e)

if __name__ == "__main__":
    mcp.run(transport='stdio')
