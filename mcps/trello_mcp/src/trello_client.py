from typing import Any, Dict, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from trello_errors import (
    TrelloError,
    TrelloAuthError,
    TrelloNotFoundError,
    TrelloRateLimitError,
    TrelloValidationError,
    TrelloServerError
)

class TrelloClient:
    def __init__(self, api_key: str, token: str, base_url: str):
        """Initialize Trello client with API credentials."""
        self.api_key = api_key
        self.api_token = token
        self.base_url = base_url
        self.client = httpx.Client(timeout=30)  # 30 second timeout
        
    def _handle_error(self, error: httpx.HTTPError) -> None:
        """Handle HTTP errors and raise appropriate exceptions."""
        if isinstance(error, httpx.HTTPStatusError):
            status_code = error.response.status_code
            try:
                response_data = error.response.json()
            except ValueError:
                response_data = {"error": error.response.text}

            if status_code == 401:
                raise TrelloAuthError("Authentication failed", status_code, response_data)
            elif status_code == 404:
                raise TrelloNotFoundError("Resource not found", status_code, response_data)
            elif status_code == 429:
                raise TrelloRateLimitError("Rate limit exceeded", status_code, response_data)
            elif status_code == 400:
                raise TrelloValidationError("Invalid request", status_code, response_data)
            elif status_code >= 500:
                raise TrelloServerError("Trello server error", status_code, response_data)
            
        raise TrelloError(f"Request failed: {str(error)}")

    def _get_auth_params(self) -> Dict[str, str]:
        """Get base parameters for authentication."""
        return {
            "key": self.api_key,
            "token": self.api_token
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def get_boards(self) -> list:
        """
        Fetch all boards for the authenticated user.
        
        Returns:
            list: List of board objects with name and ID.
            
        Raises:
            TrelloError: If the request fails.
        """
        url = f"{self.base_url}/members/me/boards"
        params = {
            **self._get_auth_params(),
            "fields": "name,id"
        }
        
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            self._handle_error(e)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def create_board(self, name: str, description: Optional[str] = None) -> str:
        """
        Create a new board.
        
        Args:
            name: Name of the board
            description: Optional board description
            
        Returns:
            str: ID of the created board
            
        Raises:
            TrelloError: If the request fails
        """
        url = f"{self.base_url}/boards"
        params = {
            **self._get_auth_params(),
            "name": name,
            "desc": description or "",
            "defaultLists": "false"  # Don't create default lists
        }
        
        try:
            response = self.client.post(url, params=params)
            response.raise_for_status()
            return response.json()["id"]
        except httpx.HTTPError as e:
            self._handle_error(e)

    def get_board_lists(self, board_id: str) -> list:
        """
        Fetch all lists for a board.
        
        Args:
            board_id: ID of the board to fetch lists from
            
        Returns:
            list: List of list objects with name and ID.
            
        Raises:
            TrelloError: If the request fails.
        """
        url = f"{self.base_url}/boards/{board_id}/lists"
        params = {
            **self._get_auth_params(),
            "fields": "name,id"
        }
        
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            self._handle_error(e)

    def create_list(self, name: str, board_id: str, position: str = "bottom") -> str:
        """
        Create a new list in a board.
        
        Args:
            name: Name of the list
            board_id: ID of the board to create the list in
            position: Position of the list (top, bottom, or a positive number)
            
        Returns:
            str: ID of the created list
            
        Raises:
            TrelloError: If the request fails
        """
        url = f"{self.base_url}/lists"
        params = {
            **self._get_auth_params(),
            "idBoard": board_id,
            "name": name,
            "pos": position
        }
        
        try:
            response = self.client.post(url, params=params)
            response.raise_for_status()
            return response.json()["id"]
        except httpx.HTTPError as e:
            self._handle_error(e)

    def create_card(self, list_id: str, name: str, description: str) -> str:
        """
        Create a new card on the specified list.
        
        Args:
            list_id: ID of the list to add the card to
            name: Name of the card
            description: Card description
            
        Returns:
            str: ID of the created card
            
        Raises:
            TrelloError: If the request fails
        """
        url = f"{self.base_url}/cards"
        params = {
            **self._get_auth_params(),
            "idList": list_id,
            "name": name,
            "desc": description
        }
        
        try:
            response = self.client.post(url, params=params)
            response.raise_for_status()
            return response.json()["id"]
        except httpx.HTTPError as e:
            self._handle_error(e)

    def move_card(self, card_id: str, list_id: str, position: str = "bottom") -> None:
        """
        Move a card to a different list.
        
        Args:
            card_id: ID of the card to move
            list_id: ID of the destination list
            position: Position in the list (top, bottom, or a positive number)
            
        Raises:
            TrelloError: If the request fails
        """
        url = f"{self.base_url}/cards/{card_id}"
        params = {
            **self._get_auth_params(),
            "idList": list_id,
            "pos": position
        }
        
        try:
            response = self.client.put(url, params=params)
            response.raise_for_status()
        except httpx.HTTPError as e:
            self._handle_error(e)

    def update_card(
        self,
        card_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str] = None
    ) -> None:
        """
        Update card details.
        
        Args:
            card_id: ID of the card to update
            name: New name for the card
            description: New description for the card
            due_date: Due date in ISO format
            
        Raises:
            TrelloError: If the request fails
        """
        url = f"{self.base_url}/cards/{card_id}"
        params = self._get_auth_params()
        
        if name is not None:
            params["name"] = name
        if description is not None:
            params["desc"] = description
        if due_date is not None:
            params["due"] = due_date
            
        try:
            response = self.client.put(url, params=params)
            response.raise_for_status()
        except httpx.HTTPError as e:
            self._handle_error(e)

    def get_list_cards(self, list_id: str) -> list:
        """
        Fetch all cards in a list.
        
        Args:
            list_id: ID of the list to fetch cards from
            
        Returns:
            list: List of card objects with name, ID, and description.
            
        Raises:
            TrelloError: If the request fails.
        """
        url = f"{self.base_url}/lists/{list_id}/cards"
        params = {
            **self._get_auth_params(),
            "fields": "name,id,desc"
        }
        
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            self._handle_error(e)

    def get_board_lists_with_cards(self, board_id: str) -> list:
        """
        Fetch all lists in a board along with their cards.
        
        Args:
            board_id: ID of the board to fetch lists and cards from
            
        Returns:
            list: List of list objects with name, ID, and cards array.
            
        Raises:
            TrelloError: If the request fails.
        """
        url = f"{self.base_url}/boards/{board_id}/lists"
        params = {
            **self._get_auth_params(),
            "cards": "open",  # Include non-archived cards
            "card_fields": "name,id,desc"  # Only get essential card fields
        }
        
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            self._handle_error(e)

    def archive_card(self, card_id: str) -> None:
        """
        Archive a card.
        
        Args:
            card_id: ID of the card to archive
            
        Raises:
            TrelloError: If the request fails
        """
        url = f"{self.base_url}/cards/{card_id}"
        params = {
            **self._get_auth_params(),
            "closed": "true"
        }
        
        try:
            response = self.client.put(url, params=params)
            response.raise_for_status()
        except httpx.HTTPError as e:
            self._handle_error(e)
