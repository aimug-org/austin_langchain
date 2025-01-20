from typing import Any, Dict, Optional

class TrelloError(Exception):
    """Base exception for Trello API errors."""
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)

    def to_response(self) -> Dict[str, Any]:
        """Convert error to a standardized response format."""
        return {
            "error": {
                "type": self.__class__.__name__,
                "message": self.message,
                "status_code": self.status_code,
                "details": self.response_data
            }
        }

class TrelloAuthError(TrelloError):
    """Raised when authentication fails."""
    pass

class TrelloNotFoundError(TrelloError):
    """Raised when a requested resource is not found."""
    pass

class TrelloRateLimitError(TrelloError):
    """Raised when API rate limit is exceeded."""
    pass

class TrelloValidationError(TrelloError):
    """Raised when request validation fails."""
    pass

class TrelloServerError(TrelloError):
    """Raised when Trello API returns a server error."""
    pass

def handle_trello_error(error: TrelloError) -> Dict[str, Any]:
    """Convert any TrelloError to a standardized response format."""
    return {
        "error_type": error.__class__.__name__,
        "error_message": str(error.message),
        "status_code": error.status_code
    }