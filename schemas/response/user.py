from schemas.base import UserBase
from models.enums import RoleType


class UserOut(UserBase):
    id: int
    first_name: str
    last_name: str
    phone: str
    role: RoleType
    iban: str
