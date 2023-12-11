from typing import Optional, List
from fastapi import APIRouter, Depends
from managers.user import UserManager
from managers import oauth2_schema, is_admin
from schemas.response import UserOut
from models.enums import RoleType

router = APIRouter(tags=["Users"])


@router.get(
    "/users/",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    response_model=List[UserOut],
    response_model_exclude={"role"},
)
async def get_all_users(email: Optional[str] = None):
    if email:
        return await UserManager.get_user_by_email(email)
    return await UserManager.get_all_users()


@router.put(
    "/users/{user_id}/make-admin",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    status_code=201,
)
async def change_by_admin(user_id: int):
    await UserManager.change_role_status_by_user_id(RoleType.admin, user_id)


@router.put(
    "/users/{user_id}/make-approver",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    # status_code=201,
)
async def change_by_approver(user_id: int):
    await UserManager.change_role_status_by_user_id(RoleType.approver, user_id)
