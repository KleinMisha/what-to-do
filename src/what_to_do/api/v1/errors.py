"""Status codes for API errors"""

from fastapi import status

from what_to_do.core.exceptions import InvalidAssignmentError, ResourceNotFoundError

error_to_code: dict[type[Exception], int] = {
    ResourceNotFoundError: status.HTTP_404_NOT_FOUND,
    InvalidAssignmentError: status.HTTP_409_CONFLICT,
}
