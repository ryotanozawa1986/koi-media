"""【非推奨】初期サンプル用の 1200x630 抽象サムネイルを Pillow で作る。

新しい記事のサムネイルには使わない。
今の運用は scripts/thumbnail-styles.json のスタイル D/E/F で背景を生成し、
scripts/overlay-title.py（または compose-thumbnail.py）でタイトルを載せる。
手順は CONTENT_GUIDE.md の「4. サムネイル」を見ること。
"""

import sys
import warnings

warnings.warn(
    "generate-sample-images.py は非推奨です。CONTENT_GUIDE.md のサムネイル手順を使ってください。",
    DeprecationWarning,
    stacklevel=1,
)
print("警告: このスクリプトは非推奨です。新しいサムネイルは CONTENT_GUIDE.md の手順で作ってください。", file=sys.stderr)

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
OUT = Path(__file__).resolve().parents[1] / "public"
FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def canvas(top, bottom):
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        col = lerp(top, bottom, y / (H - 1))
        for x in range(W):
            px[x, y] = col
    return img.convert("RGBA")


def save(img, name):
    path = OUT / "thumbnails" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(path, "WEBP", quality=84, method=6)
    print(path)


def frame(draw, color):
    draw.rectangle((36, 36, W - 37, H - 37), outline=color + (150,), width=1)


def pillars():
    img = canvas((120, 58, 72), (244, 220, 206))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    accent = (206, 168, 112)
    for x in (210, 292, 374, 456):
        draw.line((x, 90, x, 540), fill=accent + (170,), width=2)
    draw.ellipse((760, 70, 1120, 560), outline=accent + (120,), width=2)
    frame(draw, accent)
    save(Image.alpha_composite(img, overlay), "sample-shichu-suimei-love.webp")


def stars():
    img = canvas((42, 48, 82), (196, 176, 198))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    accent = (236, 220, 180)
    import math

    for i in range(6):
        ang = math.radians(-150 + i * 26)
        x = 820 + 250 * math.cos(ang)
        y = 320 + 150 * math.sin(ang)
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=accent + (230,))
    draw.arc((430, 70, 1120, 560), start=200, end=350, fill=accent + (110,), width=2)
    frame(draw, accent)
    save(Image.alpha_composite(img, overlay), "sample-rokusei-compatibility.webp")


def nine():
    img = canvas((226, 216, 204), (154, 166, 156))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    accent = (122, 92, 70)
    for row in range(3):
        for col in range(3):
            x = 760 + col * 96
            y = 175 + row * 96
            draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=accent + (210,))
    draw.rectangle((720, 135, 1020, 500), outline=accent + (130,), width=1)
    frame(draw, accent)
    save(Image.alpha_composite(img, overlay), "sample-kyusei-timing.webp")


def brand():
    img = canvas((246, 241, 234), (243, 224, 220))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    accent = (156, 77, 92)
    frame(draw, accent)
    font_en = ImageFont.truetype(FONT, 86)
    font_ja = ImageFont.truetype(FONT, 34)
    draw.text((96, 230), "koi-media", font=font_en, fill=(36, 28, 30, 255))
    draw.text((100, 350), "恋愛と占いのメディア", font=font_ja, fill=accent + (255,))
    path = OUT / "og-default.webp"
    Image.alpha_composite(img, overlay).convert("RGB").save(path, "WEBP", quality=84, method=6)
    print(path)


if __name__ == "__main__":
    pillars()
    stars()
    nine()
    brand()
