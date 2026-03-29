#!/usr/bin/env python3

from pathlib import Path

from PIL import Image, ImageOps


ROOT_DIR = Path(__file__).resolve().parents[1]
PROPERTIES_DIR = ROOT_DIR / "app" / "assets" / "properties"
THUMB_MAX_WIDTH = 640
THUMB_QUALITY = 82


def thumbnail_path(original_path: Path) -> Path:
    return original_path.with_name(f"{original_path.stem}-thumb.webp")


def resize_for_thumbnail(image: Image.Image) -> Image.Image:
    if image.width <= THUMB_MAX_WIDTH:
        return image

    target_height = round(image.height * THUMB_MAX_WIDTH / image.width)
    return image.resize((THUMB_MAX_WIDTH, target_height), Image.Resampling.LANCZOS)


def generate_thumbnail(original_path: Path) -> Path:
    target_path = thumbnail_path(original_path)

    with Image.open(original_path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image = resize_for_thumbnail(image)
        image.save(target_path, format="WEBP", quality=THUMB_QUALITY, method=6)

    return target_path


def main() -> None:
    originals = sorted(PROPERTIES_DIR.glob("*.jpg"))
    if not originals:
        print("No property images found")
        return

    for original_path in originals:
        target_path = generate_thumbnail(original_path)
        print(f"Generated {target_path.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
