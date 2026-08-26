"""
Annotation drawing engine with Pillow.
Provides primitives for arrows, rectangles, circles, text labels, highlights, and blur/pixelation.
"""

import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor
from screensnap.config import FONT_FAMILY


def draw_arrow(img: Image.Image, p1: tuple[int, int], p2: tuple[int, int], color: str, thickness: int) -> Image.Image:
    res = img.copy()
    draw = ImageDraw.Draw(res)
    x1, y1 = p1
    x2, y2 = p2

    draw.line([(x1, y1), (x2, y2)], fill=color, width=thickness)

    # Arrowhead geometry
    angle = math.atan2(y2 - y1, x2 - x1)
    arrow_len = max(18, thickness * 4.5)
    arrow_angle = math.pi / 6

    ap1 = (x2 - arrow_len * math.cos(angle - arrow_angle), y2 - arrow_len * math.sin(angle - arrow_angle))
    ap2 = (x2 - arrow_len * math.cos(angle + arrow_angle), y2 - arrow_len * math.sin(angle + arrow_angle))

    draw.polygon([(x2, y2), ap1, ap2], fill=color)
    return res


def draw_rectangle(img: Image.Image, p1: tuple[int, int], p2: tuple[int, int], color: str, thickness: int) -> Image.Image:
    res = img.copy()
    draw = ImageDraw.Draw(res)
    box = [min(p1[0], p2[0]), min(p1[1], p2[1]), max(p1[0], p2[0]), max(p1[1], p2[1])]
    draw.rectangle(box, outline=color, width=thickness)
    return res


def draw_circle(img: Image.Image, p1: tuple[int, int], p2: tuple[int, int], color: str, thickness: int) -> Image.Image:
    res = img.copy()
    draw = ImageDraw.Draw(res)
    box = [min(p1[0], p2[0]), min(p1[1], p2[1]), max(p1[0], p2[0]), max(p1[1], p2[1])]
    draw.ellipse(box, outline=color, width=thickness)
    return res


def draw_highlight(img: Image.Image, p1: tuple[int, int], p2: tuple[int, int], color: str) -> Image.Image:
    box = [min(p1[0], p2[0]), min(p1[1], p2[1]), max(p1[0], p2[0]), max(p1[1], p2[1])]
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    try:
        rgb = ImageColor.getrgb(color)
    except Exception:
        rgb = (0, 229, 255)
    draw.rectangle(box, fill=(rgb[0], rgb[1], rgb[2], 90))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def apply_blur_pixelation(img: Image.Image, p1: tuple[int, int], p2: tuple[int, int]) -> Image.Image:
    res = img.copy()
    box = (int(min(p1[0], p2[0])), int(min(p1[1], p2[1])), int(max(p1[0], p2[0])), int(max(p1[1], p2[1])))
    if box[2] > box[0] and box[3] > box[1]:
        crop = res.crop(box)
        pixel_scale = max(6, int(max(crop.size) / 28))
        small_w = max(1, crop.width // pixel_scale)
        small_h = max(1, crop.height // pixel_scale)
        pix = crop.resize((small_w, small_h), Image.Resampling.BILINEAR)
        pix = pix.resize(crop.size, Image.Resampling.NEAREST).filter(ImageFilter.GaussianBlur(radius=2))
        res.paste(pix, box)
    return res


def draw_text_label(img: Image.Image, pos: tuple[int, int], text: str, color: str, thickness: int) -> Image.Image:
    res = img.copy()
    draw = ImageDraw.Draw(res)
    font_size = max(18, int(thickness * 6))
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

    bbox = draw.textbbox(pos, text, font=font)
    pad = 8
    bg_box = [bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad]

    overlay = Image.new("RGBA", res.size, (255, 255, 255, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle(bg_box, radius=6, fill=(8, 9, 14, 220), outline=color, width=2)
    res = Image.alpha_composite(res.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(res)
    draw.text(pos, text, fill=color, font=font)
    return res