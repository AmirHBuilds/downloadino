import hashlib

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.visit_event import VisitEvent

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.post("/visit", status_code=204)
async def track_visit(request: Request, db: AsyncSession = Depends(get_db)):
    forwarded_for = request.headers.get("x-forwarded-for", "")
    ip_address = (forwarded_for.split(",")[0].strip() if forwarded_for else (request.client.host if request.client else "unknown"))
    user_agent = request.headers.get("user-agent", "unknown")
    raw_key = f"{ip_address}|{user_agent}"
    visitor_key = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    event = VisitEvent(
        visitor_key=visitor_key,
        path=request.headers.get("x-page-path") or str(request.url.path),
        referrer=request.headers.get("referer"),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(event)
    await db.commit()
