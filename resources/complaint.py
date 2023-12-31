from typing import List, Optional

from fastapi import APIRouter, Depends, Request

from managers import is_admin, is_complainer, oauth2_schema
from managers.complaint import ComplaintManager
from schemas.request import ComplaintIn
from schemas.response import ComplaintOut

router = APIRouter(tags=["Complaints"])


@router.get(
    "/complaints/",
    dependencies=[Depends(oauth2_schema)],
    response_model=List[Optional[ComplaintOut]],
)
async def get_call_complaints(request: Request):
    user = request.state.user
    return await ComplaintManager.get_complaints(user)


@router.post(
    "/complaints/",
    dependencies=[Depends(oauth2_schema), Depends(is_complainer)],
    # response_model=ComplaintOut
)
async def create_new_complaint(request: Request, complaint_obj: ComplaintIn):
    user = request.state.user
    return await ComplaintManager.create_complaint(complaint_obj, user)


@router.delete(
    "/complaints/{complaint_id}",
    dependencies=[Depends(oauth2_schema), Depends(is_admin)],
    status_code=201,
)
async def delete_complaint(complaint_id: int):
    await ComplaintManager.delete_complaint(complaint_id)


@router.put(
    "/complaints/{complaint_id}/approve",
    dependencies=[Depends(oauth2_schema)],
    status_code=201,
)
async def approve_specific_complaint(complaint_id: int):
    return await ComplaintManager.approve(complaint_id)


@router.put(
    "/complaints/{complaint_id}/reject",
    dependencies=[Depends(oauth2_schema)],
    status_code=201,
)
async def reject_specific_complaint(complaint_id: int):
    return await ComplaintManager.reject(complaint_id)
