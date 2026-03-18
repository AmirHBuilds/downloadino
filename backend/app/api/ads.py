import mimetypes

from fastapi import APIRouter, Depends, File as FastAPIFile, HTTPException, Request, UploadFile
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.file_validator import validate_file
from app.core.rate_limiter import upload_limiter
from app.core.security import require_admin_permission
from app.core.storage import delete_file, get_file_content, save_storage_file
from app.db.session import get_db
from app.models.ad import Ad
from app.schemas.ad import AdCreate, AdResponse, AdUpdate

router = APIRouter(tags=["Ads"])

AD_MEDIA_URL_PREFIX = "/api/ads/media/"
ALLOWED_AD_MEDIA_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",
    "video/mp4",
    "video/webm",
}


def hosted_ad_storage_path(image_url: str | None) -> str | None:
    if not image_url or not image_url.startswith(AD_MEDIA_URL_PREFIX):
        return None
    storage_path = image_url.removeprefix(AD_MEDIA_URL_PREFIX).strip("/")
    if not storage_path.startswith("ads/"):
        return None
    return storage_path


@router.get("/ads/active", response_model=list[AdResponse])
async def get_active_ads(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ad).where(Ad.is_active == True).order_by(Ad.created_at.desc()))
    return result.scalars().all()


@router.get("/ads/media/{storage_path:path}")
async def get_ad_media(storage_path: str):
    normalized_path = storage_path.strip("/")
    if not normalized_path.startswith("ads/"):
        raise HTTPException(status_code=404, detail="Ad media not found")

    content = await get_file_content(normalized_path)
    media_type = mimetypes.guess_type(normalized_path)[0] or "application/octet-stream"
    return Response(content=content, media_type=media_type, headers={"Cache-Control": "public, max-age=300"})


@router.get("/admin/ads", response_model=list[AdResponse])
async def list_all_ads(db: AsyncSession = Depends(get_db), _=Depends(require_admin_permission("manage_ads"))):
    result = await db.execute(select(Ad).order_by(Ad.created_at.desc()))
    return result.scalars().all()


@router.post("/admin/ads/upload-media")
@upload_limiter.limit("100/hour")
async def upload_ad_media(
    request: Request,
    media: UploadFile = FastAPIFile(...),
    _=Depends(require_admin_permission("manage_ads")),
):
    content, detected_mime = await validate_file(media)
    mime_type = media.content_type or detected_mime
    if mime_type not in ALLOWED_AD_MEDIA_TYPES and detected_mime not in ALLOWED_AD_MEDIA_TYPES:
        raise HTTPException(status_code=415, detail="Only JPG, PNG, GIF, WEBP, SVG, MP4, and WEBM ad media are supported.")

    _, storage_path = await save_storage_file(content, media.filename or "ad-media", "ads")
    return {"url": f"{AD_MEDIA_URL_PREFIX}{storage_path}"}


@router.post("/admin/ads", response_model=AdResponse, status_code=201)
async def create_ad(data: AdCreate, db: AsyncSession = Depends(get_db), _=Depends(require_admin_permission("manage_ads"))):
    ad = Ad(**data.model_dump())
    db.add(ad)
    await db.flush()
    return ad


@router.put("/admin/ads/{ad_id}", response_model=AdResponse)
async def update_ad(ad_id: int, data: AdUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_admin_permission("manage_ads"))):
    result = await db.execute(select(Ad).where(Ad.id == ad_id))
    ad = result.scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    previous_image_url = ad.image_url
    updates = data.model_dump(exclude_unset=True)
    for k, v in updates.items():
        setattr(ad, k, v)

    if "image_url" in updates and updates["image_url"] != previous_image_url:
        old_storage_path = hosted_ad_storage_path(previous_image_url)
        if old_storage_path:
            await delete_file(old_storage_path)

    return ad


@router.delete("/admin/ads/{ad_id}", status_code=204)
async def delete_ad(ad_id: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin_permission("manage_ads"))):
    result = await db.execute(select(Ad).where(Ad.id == ad_id))
    ad = result.scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    storage_path = hosted_ad_storage_path(ad.image_url)
    if storage_path:
        await delete_file(storage_path)

    await db.delete(ad)


@router.post("/ads/{ad_id}/click")
async def track_click(ad_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ad).where(Ad.id == ad_id, Ad.is_active == True))
    ad = result.scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    ad.click_count += 1
    return {"target_url": ad.target_url}
