from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BizException
from app.db.crud import EmailCRUD
from app.db.session import get_db
from app.schemas import (
    ApiResponse,
    ApproveRequest,
    EditSendRequest,
    EmailDetailData,
    PendingItem,
    PendingListData,
    RegenerateRequest,
    RiskMarkRequest,
)
from app.services.workflow import ReviewWorkflow

router = APIRouter(prefix="/api/reviews", tags=["review"])
workflow = ReviewWorkflow()


@router.get("/pending", response_model=ApiResponse)
async def list_pending(page: int = 1, size: int = 20, db: AsyncSession = Depends(get_db)):
    items, total = await EmailCRUD.list_pending(db, page, size)
    data = PendingListData(
        items=[
            PendingItem(
                id=i.id,
                sender=i.sender,
                subject=i.subject,
                status=i.status.value,
                risk_level=i.risk_level,
                created_at=i.created_at,
            )
            for i in items
        ],
        total=total,
        page=page,
        size=size,
    )
    return ApiResponse(data=data)


@router.get("/{email_id}", response_model=ApiResponse)
async def get_detail(email_id: int, db: AsyncSession = Depends(get_db)):
    email = await EmailCRUD.get_by_id(db, email_id)
    if not email:
        raise BizException(404, "邮件不存在")
    data = EmailDetailData(
        id=email.id,
        sender=email.sender,
        recipients=email.recipients,
        subject=email.subject,
        body_text=email.body_text,
        ai_result=email.ai_result,
        structured_data=email.structured_data,
        draft_reply=email.draft_reply,
        status=email.status.value,
        risk_level=email.risk_level,
        erp_sync_status=email.erp_sync_status,
        last_error=email.last_error,
        created_at=email.created_at,
    )
    return ApiResponse(data=data)


@router.post("/{email_id}/approve", response_model=ApiResponse)
async def approve(email_id: int, req: ApproveRequest, db: AsyncSession = Depends(get_db)):
    email = await workflow.approve_and_execute(db, email_id, req.operator, req.remark)
    if not email:
        raise BizException(404, "邮件不存在")
    return ApiResponse(message="已审核并发送", data={"id": email.id, "status": email.status.value})


@router.post("/{email_id}/send-edited", response_model=ApiResponse)
async def send_edited(email_id: int, req: EditSendRequest, db: AsyncSession = Depends(get_db)):
    email = await workflow.send_edited(db, email_id, req.operator, req.edited_draft, req.remark)
    if not email:
        raise BizException(404, "邮件不存在")
    return ApiResponse(message="已编辑并发送", data={"id": email.id, "status": email.status.value})


@router.post("/{email_id}/regenerate", response_model=ApiResponse)
async def regenerate(email_id: int, req: RegenerateRequest, db: AsyncSession = Depends(get_db)):
    email = await workflow.regenerate(db, email_id, req.operator, req.reason)
    if not email:
        raise BizException(404, "邮件不存在")
    return ApiResponse(message="已退回重生成", data={"id": email.id, "status": email.status.value})


@router.post("/{email_id}/flag-risk", response_model=ApiResponse)
async def flag_risk(email_id: int, req: RiskMarkRequest, db: AsyncSession = Depends(get_db)):
    email = await workflow.mark_risk(db, email_id, req.operator, req.level, req.remark)
    if not email:
        raise BizException(404, "邮件不存在")
    return ApiResponse(message="已标记风险", data={"id": email.id, "status": email.status.value})
