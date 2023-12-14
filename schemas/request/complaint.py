from pydantic import BaseModel

from schemas.base import BaseComplaint


class ComplaintIn(BaseComplaint):
    encoded_photo: str
    extension: str
