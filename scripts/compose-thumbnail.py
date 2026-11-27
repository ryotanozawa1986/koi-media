#!/usr/bin/env python3
"""スタイル定義を読み、サムネイル用のプロンプト表示とタイトル合成を行う。

日次自動化の流れ:
  1. --pick-style または --style D|E|F でスタイルを決める
  2. --print-prompt で GenerateImage 用の英語プロンプトを出す（文字は描かせない）
  3. 生成した背景を 1200x630 にし、このスクリプトでタイトルを載せて WebP にする

例:
  python scripts/compose-thumbnail.py --pick-style --category-id shichu-suimei --print-prompt
  python scripts/compose-thumbnail.py \\
    --image /tmp/bg.png --style D \\
    --title "四柱推命とは？恋愛傾向の見方" --category "四柱推命" \\
    --output public/thumbnails/slug.webp
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STYLES = Path(__file__).resolve().parent / "thumbnail-styles.json"
TARGET = (1200, 630)

def _load_overlay():
    import importlib.util

    path = Path(__file__).resolve().parent / "overlay-title.py"
    spec = importlib.util.spec_from_file_location("overlay_title", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"overlay-title.py を読めません: {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


overlay = _load_overlay()


def load_styles(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pick_style(data: dict, chosen: str | None) -> str:
    ids = list(data["styles"].keys())
    if chosen:
        if chosen not in data["styles"]:
            raise SystemExit(f"未知のスタイルです: {chosen}（使えるのは {', '.join(ids)}）")
        return chosen
    return random.choice(ids)


def fill_prompt(data: dict, style_id: str, category_id: str | None) -> str:
    template = data["styles"][style_id]["prompt"]
    motifs = data.get("motifs", {})
    motif = motifs.get(category_id or "", motifs.get("default", ""))
    return template.replace("{motif}", motif).strip()


def to_canvas(image: Image.Image) -> Image.Image:
    """16:9 などを 1200x630 にする。枠付き線画は縦方向に軽く伸ばして枠を残す。"""
    image = image.convert("RGB")
    return image.resize(TARGET, Image.Resampling.LANCZOS)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="サムネイルのスタイル選択とタイトル合成")
    parser.add_argument("--styles", type=Path, default=DEFAULT_STYLES)
    parser.add_argument("--style", help="D / E / F。省略時は --pick-style が必要")
    parser.add_argument("--pick-style", action="store_true", help="D/E/F からランダムに選ぶ")
    parser.add_argument("--category-id", default="", help="モチーフ用のカテゴリ id（例: shichu-suimei）")
    parser.add_argument("--print-prompt", action="store_true", help="GenerateImage 用プロンプトだけを出す")
    parser.add_argument("--image", type=Path, help="文字なしの背景画像")
    parser.add_argument("--title", default="", help="記事タイトル")
    parser.add_argument("--category", default="", help="画像に載せるカテゴリ名（例: 四柱推命）")
    parser.add_argument("--output", type=Path, help="出力（.webp または .png）")
    parser.add_argument("--max-width", type=int, default=0, help="指定時はスタイルの max_width を上書き")
    parser.add_argument("--max-title-size", type=int, default=0)
    args = parser.parse_args(argv)

    data = load_styles(args.styles)
    if not args.style and not args.pick_style:
        print("--style か --pick-style を指定してください。", file=sys.stderr)
        return 1
    style_id = pick_style(data, None if args.pick_style else args.style)
    style = data["styles"][style_id]
    overlay_cfg = style["overlay"]

    if args.print_prompt:
        print(f"# style: {style_id} ({style.get('name', '')})")
        print(fill_prompt(data, style_id, args.category_id or None))
        return 0

    if not args.image or not args.title or not args.output:
        print("合成には --image --title --output が必要です。", file=sys.stderr)
        return 1
    if not args.image.exists():
        print(f"画像がありません: {args.image}", file=sys.stderr)
        return 1

    bg = to_canvas(Image.open(args.image))
    color = overlay.parse_color(overlay_cfg["color"])
    accent = overlay.parse_color(overlay_cfg["accent"])
    result = overlay.overlay(
        image=bg,
        title=args.title,
        category=args.category or None,
        color=color,
        accent=accent,
        align=overlay_cfg.get("align", "left"),
        valign=overlay_cfg.get("valign", "center"),
        margin_x=int(overlay_cfg.get("margin_x", 96)),
        max_text_width=args.max_width or int(overlay_cfg.get("max_width") or 0) or None,
        max_title_size=args.max_title_size or overlay.DEFAULT_MAX_TITLE,
        min_title_size=overlay.DEFAULT_MIN_TITLE,
    )
    overlay.save(result, args.output)
    print(f"# style: {style_id}")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
