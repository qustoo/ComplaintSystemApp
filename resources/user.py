from typing import Optional, List
from fastapi import APIRouter, Depends
from managers.user import UserManager
from managers import oauth2_schema, is_admin
from schemas.response import UserOut

router = APIRouter(tags=["Users"])


@router.get(
    "/users/",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    response_model=List[UserOut],response_model_exclude={"role"}
)
async def get_all_users(email: Optional[str] = None):
    if email:
        return await UserManager.get_user_by_email(email)
    return await UserManager.get_all_users()
