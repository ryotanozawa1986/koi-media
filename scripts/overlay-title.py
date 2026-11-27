#!/usr/bin/env python3
"""サムネイル画像に日本語タイトル（と任意のカテゴリ）を合成する。

画像モデルには文字を描かせず、Noto CJK で後から載せる。
日次の記事自動化からも、同じ引数で呼べる。

例:
  python scripts/overlay-title.py \\
    --image public/thumbnails/slug.webp \\
    --title "四柱推命とは？恋愛傾向の見方" \\
    --category "四柱推命" \\
    --output public/thumbnails/slug.webp \\
    --align left --color "#3a2f28" --accent "#b8955a"
"""

from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CANVAS_W, CANVAS_H = 1200, 630

# カード表示（約 360px 幅）で本文が読めるサイズ。1200 幅の 0.3 倍になる。
DEFAULT_MAX_TITLE = 84  # カード上で約 25px
DEFAULT_MIN_TITLE = 52  # カード上で約 16px
DEFAULT_CATEGORY = 30  # カード上で約 9px（やや小さめだがラベル用）
# カテゴリはカードでも読めるよう、少し大きめにする
CATEGORY_SIZE = 34

# 日次自動化の実行環境に入っている想定のパス。
# Debian/Ubuntu は `sudo apt install fonts-noto-cjk` で入る。
# 見つかったパスと index は起動時に一度だけ解決する。
FONT_SERIF_BOLD_CANDIDATES = (
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJKjp-Bold.otf",
    "/usr/share/fonts/noto-cjk/NotoSerifCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSerifCJK-Bold.ttc",
    "/usr/local/share/fonts/NotoSerifCJK-Bold.ttc",
)
FONT_SANS_REGULAR_CANDIDATES = (
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Regular.otf",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/local/share/fonts/NotoSansCJK-Regular.ttc",
)

FONT_SERIF_BOLD = ""
FONT_SANS_REGULAR = ""
FONT_INDEX_JP = 0


def _jp_index(path: str) -> int:
    """TTC なら JP 面の index を探す。単体 OTF は 0。"""
    if not path.lower().endswith(".ttc"):
        return 0
    for index in range(8):
        try:
            font = ImageFont.truetype(path, 12, index=index)
        except OSError:
            break
        family, _ = font.getname()
        if "JP" in family.upper() or family.endswith("JP"):
            return index
    return 0


def _first_existing(candidates: tuple[str, ...], label: str) -> str:
    for path in candidates:
        if Path(path).is_file():
            return path
    joined = "\n  ".join(candidates)
    raise FileNotFoundError(
        f"{label} が見つかりません。Noto CJK を入れてください"
        f"（Debian/Ubuntu: sudo apt install fonts-noto-cjk）。探したパス:\n  {joined}"
    )


def _resolve_fonts() -> None:
    global FONT_SERIF_BOLD, FONT_SANS_REGULAR, FONT_INDEX_JP
    if FONT_SERIF_BOLD:
        return
    FONT_SERIF_BOLD = _first_existing(FONT_SERIF_BOLD_CANDIDATES, "Noto Serif CJK Bold")
    FONT_SANS_REGULAR = _first_existing(FONT_SANS_REGULAR_CANDIDATES, "Noto Sans CJK Regular")
    FONT_INDEX_JP = _jp_index(FONT_SERIF_BOLD)

# 句読点・切りやすい助詞の直後を優先して折り返す
PREFERRED_AFTER = ("？", "?", "！", "!", "。", "、", "」")
PREFERRED_UNITS = ("とは？", "とは?", "とは", "で読む", "について")


def parse_color(value: str) -> tuple[int, int, int]:
    text = value.strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        raise argparse.ArgumentTypeError(f"色は #RRGGBB で指定してください: {value}")
    return int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    _resolve_fonts()
    font_path = path or FONT_SERIF_BOLD
    return ImageFont.truetype(font_path, size, index=FONT_INDEX_JP)


def text_size(font: ImageFont.ImageFont, text: str) -> tuple[int, int]:
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def line_width(font: ImageFont.ImageFont, text: str) -> int:
    return text_size(font, text)[0]


def _char_name(ch: str) -> str:
    return unicodedata.name(ch, "")


def is_kanji(ch: str) -> bool:
    return "CJK UNIFIED" in _char_name(ch) or "CJK COMPATIBILITY IDEOGRAPH" in _char_name(ch)


def is_hiragana(ch: str) -> bool:
    return "HIRAGANA" in _char_name(ch)


def is_okurigana_break(text: str, index: int) -> bool:
    """漢字の直後の送りがな（読|む）で割っているか。"""
    if index <= 0 or index >= len(text):
        return False
    return is_kanji(text[index - 1]) and is_hiragana(text[index])


def break_score(text: str, index: int) -> int:
    """大きいほどよい分割位置。index は後半の開始位置。"""
    if index <= 0 or index >= len(text):
        return -10_000
    prev = text[index - 1]
    right = text[index:]
    score = 0
    for unit in PREFERRED_UNITS:
        if text.endswith(unit, 0, index):
            score += 80
            break
    if prev in PREFERRED_AFTER:
        score += 100
    if prev in "のとにをはがで":
        score += 20
    # 送りがなの途中や、行頭に送りがなだけ残る分割は強く避ける
    if is_okurigana_break(text, index):
        score -= 300
    if right and is_hiragana(right[0]) and len(right) > 1 and is_kanji(right[1]):
        score -= 200
    return score


def wrap_title(
    text: str, font: ImageFont.ImageFont, max_width: int, max_lines: int = 2
) -> tuple[list[str], int] | None:
    """(行, 分割スコア) を返す。1行に収まるときはスコア 1000。"""
    text = text.strip()
    if not text:
        return [], 1000
    if line_width(font, text) <= max_width:
        return [text], 1000
    if max_lines < 2:
        return None

    best: tuple[int, list[str]] | None = None
    for index in range(1, len(text)):
        left, right = text[:index].rstrip(), text[index:].lstrip()
        if not left or not right:
            continue
        if line_width(font, left) > max_width or line_width(font, right) > max_width:
            continue
        balance = -abs(line_width(font, left) - line_width(font, right)) // 8
        score = break_score(text, index) + balance
        if best is None or score > best[0]:
            best = (score, [left, right])
    if best is None:
        return None
    return best[1], best[0]


def fit_title(
    title: str,
    max_width: int,
    max_size: int,
    min_size: int,
    max_lines: int,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    """分割の自然さを優先し、そのうえで大きい字を選ぶ。

    大きいサイズで無理に切るより、少し下げて「で読む」の後で割る方がよい。
    """
    best: tuple[int, ImageFont.FreeTypeFont, list[str], int] | None = None
    for size in range(max_size, min_size - 1, -2):
        font = load_font(FONT_SERIF_BOLD, size)
        wrapped = wrap_title(title, font, max_width, max_lines=max_lines)
        if not wrapped:
            continue
        lines, wrap_score = wrapped
        # カードで読める大きさを最優先。1行に収めるため小さくするのは避ける。
        # 同じサイズなら、自然な分割（良いスコア）と1行を少しだけ優遇する。
        total = size * 1000 + wrap_score
        if best is None or total > best[0]:
            best = (total, font, lines, size)
    if best is not None:
        return best[1], best[2], best[3]
    font = load_font(FONT_SERIF_BOLD, min_size)
    mid = max(1, len(title) // 2)
    fallback = [title[:mid], title[mid:]]
    wrapped = wrap_title(title, font, max_width, max_lines=max_lines)
    if wrapped:
        fallback = wrapped[0]
    return font, fallback, min_size


def overlay(
    image: Image.Image,
    title: str,
    category: str | None,
    color: tuple[int, int, int],
    accent: tuple[int, int, int],
    align: str,
    valign: str,
    margin_x: int,
    max_text_width: int | None,
    max_title_size: int,
    min_title_size: int,
) -> Image.Image:
    _resolve_fonts()
    base = image.convert("RGB")
    w, h = base.size
    overlay_img = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay_img)

    if max_text_width is None:
        # 左寄せなら右のモチーフを避ける。中央なら左右マージン内。
        if align == "center":
            max_text_width = w - margin_x * 2
        else:
            max_text_width = min(720, w - margin_x - 80)

    font, lines, title_size = fit_title(
        title,
        max_width=max_text_width,
        max_size=max_title_size,
        min_size=min_title_size,
        max_lines=2,
    )
    line_gap = max(8, int(title_size * 0.28))

    cat_font = None
    cat_h = 0
    rule_h = 0
    if category:
        cat_font = load_font(FONT_SANS_REGULAR, CATEGORY_SIZE)
        cat_h = text_size(cat_font, category)[1]
        rule_h = 14  # ラベル下の余白 + 線 + タイトルまでの余白の一部

    line_heights = [text_size(font, line)[1] for line in lines]
    title_block_h = sum(line_heights) + line_gap * (len(lines) - 1)
    block_h = title_block_h
    if category:
        block_h += cat_h + 10 + 1 + 18  # ラベル、隙間、線、線からタイトル

    if valign == "top":
        y = 72 if h >= 600 else 40
    elif valign == "bottom":
        y = h - block_h - (72 if h >= 600 else 40)
    else:
        y = (h - block_h) // 2

    def x_for(text_w: int) -> int:
        if align == "center":
            return (w - text_w) // 2
        if align == "right":
            return w - margin_x - text_w
        return margin_x

    # カテゴリ
    if category and cat_font is not None:
        cw = line_width(cat_font, category)
        cx = x_for(cw)
        # わずかな字間を空けてラベルらしくする
        tracking = 4
        tracked_w = cw + tracking * max(0, len(category) - 1)
        cx = x_for(tracked_w)
        cursor = cx
        for ch in category:
            draw.text((cursor, y), ch, font=cat_font, fill=accent + (255,))
            cursor += line_width(cat_font, ch) + tracking
        y += cat_h + 10
        rule_w = max(tracked_w, 120)
        rx = x_for(rule_w)
        draw.line((rx, y, rx + rule_w, y), fill=accent + (220,), width=1)
        y += 18

    # タイトル
    for i, line in enumerate(lines):
        tw = line_width(font, line)
        tx = x_for(tw)
        # ごく薄い影で淡い背景でも輪郭を残す（濃くしすぎない）
        draw.text((tx + 1, y + 1), line, font=font, fill=(255, 255, 255, 80))
        draw.text((tx, y), line, font=font, fill=color + (255,))
        y += line_heights[i] + (line_gap if i < len(lines) - 1 else 0)

    return Image.alpha_composite(base.convert("RGBA"), overlay_img).convert("RGB")


def save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix in {".webp"}:
        image.save(path, "WEBP", quality=90, method=6)
    elif suffix in {".jpg", ".jpeg"}:
        image.save(path, "JPEG", quality=92, subsampling=0, optimize=True)
    else:
        image.save(path, "PNG", optimize=True)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="サムネイルに日本語タイトルを合成する")
    p.add_argument("--image", required=True, type=Path, help="元画像（1200x630 想定）")
    p.add_argument("--title", required=True, help="記事タイトル")
    p.add_argument("--category", default="", help="カテゴリ名（省略可）")
    p.add_argument("--output", required=True, type=Path, help="出力パス（.png / .webp）")
    p.add_argument("--align", choices=("left", "center", "right"), default="left")
    p.add_argument("--valign", choices=("top", "center", "bottom"), default="center")
    p.add_argument("--color", type=parse_color, default=parse_color("#3a2f28"), help="タイトル色")
    p.add_argument("--accent", type=parse_color, default=parse_color("#b8955a"), help="カテゴリと罫線の色")
    p.add_argument("--margin-x", type=int, default=96)
    p.add_argument("--max-width", type=int, default=0, help="タイトルの最大幅。0 なら自動")
    p.add_argument("--max-title-size", type=int, default=DEFAULT_MAX_TITLE)
    p.add_argument("--min-title-size", type=int, default=DEFAULT_MIN_TITLE)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.image.exists():
        print(f"画像がありません: {args.image}", file=sys.stderr)
        return 1
    src = Image.open(args.image)
    result = overlay(
        image=src,
        title=args.title,
        category=args.category or None,
        color=args.color,
        accent=args.accent,
        align=args.align,
        valign=args.valign,
        margin_x=args.margin_x,
        max_text_width=args.max_width or None,
        max_title_size=args.max_title_size,
        min_title_size=args.min_title_size,
    )
    save(result, args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
