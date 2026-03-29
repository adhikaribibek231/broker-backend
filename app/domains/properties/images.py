from pathlib import Path, PurePosixPath

from sqlalchemy.orm import Session

from app.domains.properties.model import Property

THUMBNAIL_SUFFIX = "-thumb.webp"
ASSET_PREFIX = "/assets/"


def build_thumbnail_image_url(image_url: str) -> str:
    if not image_url or image_url.endswith(THUMBNAIL_SUFFIX):
        return image_url

    path = PurePosixPath(image_url)
    return str(path.with_name(f"{path.stem}{THUMBNAIL_SUFFIX}"))


def resolve_asset_path(image_url: str, assets_root: Path) -> Path | None:
    if not image_url.startswith(ASSET_PREFIX):
        return None

    relative_path = image_url.removeprefix(ASSET_PREFIX)
    return assets_root / relative_path


def resolve_thumbnail_asset_path(image_url: str, assets_root: Path) -> Path | None:
    asset_path = resolve_asset_path(image_url, assets_root)
    if asset_path is None:
        return None

    return asset_path.with_name(f"{asset_path.stem}{THUMBNAIL_SUFFIX}")


def backfill_property_thumbnail_urls(db: Session, assets_root: Path) -> int:
    updated_rows = 0

    for property_obj in db.query(Property).all():
        thumb_url = build_thumbnail_image_url(property_obj.image_url)
        if thumb_url == property_obj.image_url:
            continue

        thumbnail_path = resolve_thumbnail_asset_path(property_obj.image_url, assets_root)
        if thumbnail_path is None or not thumbnail_path.exists():
            continue

        property_obj.image_url = thumb_url
        updated_rows += 1

    if updated_rows:
        db.commit()

    return updated_rows
