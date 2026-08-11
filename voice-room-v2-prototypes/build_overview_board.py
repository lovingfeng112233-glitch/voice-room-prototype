from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "voice-room-v2-overview-board.png"

SECTIONS = [
    ("01-auth", "01  注册登录 AUTH"),
    ("02-rooms", "02  房间 ROOMS"),
    ("03-invite", "03  裂变 INVITE"),
    ("04-me", "04  我的 ME"),
]

THUMB_W = 220
THUMB_H = 478
CARD_W = 248
CARD_H = 548
GAP = 18
LEFT = 200
TOP = 110
ROW_GAP = 56


def font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/STHeiti Medium.ttc" if bold else "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/SFNS.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def display_name(path: Path) -> str:
    stem = path.stem
    stem = stem.replace("-v2", "")
    parts = stem.split("-", 1)
    return parts[1].replace("-", " ").title() if len(parts) == 2 else stem.title()


rows = []
for folder, title in SECTIONS:
    files = [p for p in sorted((ROOT / folder).glob("*.png")) if "draft" not in p.name]
    rows.append((title, files))

max_count = max(len(files) for _, files in rows)
board_w = LEFT + 36 + max_count * CARD_W + max(0, max_count - 1) * GAP + 60
board_h = TOP + len(rows) * CARD_H + (len(rows) - 1) * ROW_GAP + 70

canvas = Image.new("RGB", (board_w, board_h), "#F5F8FC")
draw = ImageDraw.Draw(canvas)
title_font = font(40, True)
section_font = font(26, True)
label_font = font(18, True)
sub_font = font(15, False)

draw.text((46, 28), "VOYA · PHASE 1 COMPLETE PROTOTYPE MAP", fill="#071129", font=title_font)
draw.text((46, 76), "Auth / Rooms / Invite / Me · All primary states and secondary pages", fill="#5A6886", font=sub_font)

y = TOP
for section_title, files in rows:
    # section rail
    draw.rounded_rectangle((32, y, LEFT - 16, y + CARD_H), radius=24, fill="#071129")
    draw.text((52, y + 34), section_title, fill="#FFFFFF", font=section_font)
    draw.text((52, y + 86), f"{len(files)} screens", fill="#7FE8E5", font=sub_font)

    x = LEFT + 20
    for path in files:
        draw.rounded_rectangle((x, y, x + CARD_W, y + CARD_H), radius=18, fill="#FFFFFF", outline="#DDE5F0", width=2)
        label = display_name(path)
        # fit label on one line
        while draw.textbbox((0, 0), label, font=label_font)[2] > CARD_W - 24 and len(label) > 10:
            label = label[:-2].rstrip() + "…"
        draw.text((x + 12, y + 15), label, fill="#071129", font=label_font)
        draw.text((x + 12, y + 42), path.stem.split("-", 1)[0], fill="#00A7A5", font=sub_font)

        image = Image.open(path).convert("RGB")
        image.thumbnail((THUMB_W, THUMB_H), Image.Resampling.LANCZOS)
        ix = x + (CARD_W - image.width) // 2
        iy = y + 66 + (THUMB_H - image.height) // 2
        canvas.paste(image, (ix, iy))
        x += CARD_W + GAP
    y += CARD_H + ROW_GAP

canvas.save(OUT, quality=95)
print(OUT)
