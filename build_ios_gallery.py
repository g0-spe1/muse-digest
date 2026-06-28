#!/usr/bin/env python
"""把现有图库渲染成一个面向 iOS Safari 优化的响应式图库页面。

它**不重新分析**任何图片，只读取已有的 ``data/library.json``，把数据注入
``ios/index.html`` 模板，输出一个自包含、可离线携带的移动端图库到
``data/gallery-ios/index.html``。

设计目标：
  * 与主管线解耦 —— 不依赖 muse_digest 包，单文件即可运行；
  * 容错 —— library.json 的字段命名各异时尽量归一化；
  * 离线可开 —— 没有 library.json 时回退到模板自带的示例数据，
    这样你在任何设备上双击 ios/index.html 也能看到效果。

用法::

    python build_ios_gallery.py                 # 用 data/library.json，输出到 data/gallery-ios/
    python build_ios_gallery.py --open          # 生成后用浏览器打开
    python build_ios_gallery.py --data path.json --out dist/
    python build_ios_gallery.py --serve         # 起一个本地服务器（iOS 真机扫码可访问）

为什么要 --serve：iOS Safari 直接打开 file:// 时无法 fetch 外部 JSON，且若图库很大
把整库内联进 HTML 会显得笨重。--serve 会在局域网起一个静态服务器，手机连同一 WiFi
即可在 Safari 里打开，体验最佳（也方便「添加到主屏幕」当 App 用）。
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "ios" / "index.html"
DEFAULT_DATA = ROOT / "data" / "library.json"
DEFAULT_OUT = ROOT / "data" / "gallery-ios"
DATA_MARKER = "__MUSE_DATA_JSON__"

# 8 个 ArtiMuse 维度的内部英文键（与主项目一致）。
DIM_KEYS = [
    "composition_design", "visual_elements_structure", "technical_execution",
    "originality_creativity", "theme_communication", "emotion_viewer_resonance",
    "overall_aesthetic", "comprehensive",
]


def _to_float(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    if f != f:  # NaN
        return None
    # 有些后端用 0-100，统一压到 0-10。
    if 10 < f <= 100:
        f = f / 10.0
    return max(0.0, min(10.0, f))


def _as_list(d, *keys):
    for k in keys:
        v = d.get(k)
        if isinstance(v, list) and v:
            return v
    return []


def _first(d, *keys, default=""):
    for k in keys:
        v = d.get(k)
        if v not in (None, "", []):
            return v
    return default


def _norm_dims(analysis: dict) -> dict:
    src = analysis.get("dimensions") or analysis.get("scores") or {}
    out = {}
    for k in DIM_KEYS:
        v = src.get(k) if isinstance(src, dict) else None
        if isinstance(v, dict):
            out[k] = {"score": _to_float(v.get("score")), "text": v.get("text", "")}
        else:
            out[k] = {"score": _to_float(v)}
    return out


def _norm_image(raw_path, item_id, out_dir: Path, images_dir: Path) -> str:
    """把图片路径归一化为相对输出页面的可用相对路径，必要时复制缩略图过去。"""
    if not raw_path:
        return ""
    p = Path(str(raw_path))
    # 找到真实文件：直接路径 / data/images 下同名文件。
    candidates = [p]
    if not p.is_absolute():
        candidates += [ROOT / p, images_dir / p.name]
    candidates.append(images_dir / p.name)
    real = next((c for c in candidates if c.exists() and c.is_file()), None)
    if real is None:
        # 找不到真实文件就原样返回（可能是远程 URL 或将由调用方处理）。
        s = str(raw_path)
        return s if s.startswith(("http://", "https://", "data:")) else ""
    dest_dir = out_dir / "images"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / real.name
    if not dest.exists():
        try:
            shutil.copy2(real, dest)
        except OSError:
            return ""
    return f"images/{real.name}"


def _norm_item(raw: dict, i: int, out_dir: Path, images_dir: Path) -> dict:
    analysis = raw.get("analysis") or {}
    dims = _norm_dims(analysis)
    score = _to_float(raw.get("score"))
    if score is None:
        score = _to_float(_first(analysis, "score", "overall", default=None)) \
            or dims["comprehensive"]["score"] or dims["overall_aesthetic"]["score"]
    item_id = str(raw.get("id") or f"i{i}")
    return {
        "id": item_id,
        "title": _first(raw, "title", "caption", default="未命名作品"),
        "source": _first(raw, "source", "feed", default="未知来源"),
        "source_url": _first(raw, "source_url", "url", "link", default=""),
        "image": _norm_image(_first(raw, "image", "thumb", "thumbnail", "path", default=""),
                             item_id, out_dir, images_dir),
        "category": raw.get("category") or "Uncategorized",
        "score": score,
        "dominant_colors": [str(c) for c in _as_list(raw, "dominant_colors", "colors")][:5]
        or [str(c) for c in _as_list(analysis, "dominant_colors")][:5],
        "analysis": {
            "backend": analysis.get("backend") or raw.get("backend") or "",
            "fallback": bool(analysis.get("fallback") or raw.get("fallback")),
            "summary": _first(analysis, "summary", "text", "analysis", default=""),
            "dimensions": dims,
            "inspiration": [str(t) for t in _as_list(analysis, "inspiration", "tips", "creative")],
        },
    }


def load_library(data_path: Path) -> tuple[list, dict]:
    """返回 (items, meta)。meta 里可能含图库自带的 title。"""
    if not data_path.exists():
        return [], {}
    try:
        raw = json.loads(data_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"⚠️  无法读取 {data_path}：{e}", file=sys.stderr)
        return [], {}
    if isinstance(raw, dict):
        items = raw.get("items") or raw.get("library") or []
        meta = {k: raw[k] for k in ("title", "subtitle") if raw.get(k)}
        return items, meta
    return (raw if isinstance(raw, list) else []), {}


def build(data_path: Path, out_dir: Path, title: str | None) -> Path:
    if not TEMPLATE.exists():
        raise FileNotFoundError(f"找不到模板：{TEMPLATE}")
    template = TEMPLATE.read_text(encoding="utf-8")

    images_dir = data_path.parent / "images"
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_items, meta = load_library(data_path)
    if raw_items:
        items = [_norm_item(it, i, out_dir, images_dir) for i, it in enumerate(raw_items)]
        payload = {
            "title": title or meta.get("title") or "妙析速递",
            "subtitle": meta.get("subtitle") or "摄影 · 设计 · 创意",
            "items": items,
        }
        data_json = json.dumps(payload, ensure_ascii=False)
        note = f"{len(items)} 张图片"
    else:
        # 没有真实数据：保留模板里的占位标记，前端会回退到内置示例数据。
        data_json = "null"
        note = "示例数据（未找到 library.json）"

    html = template.replace(DATA_MARKER, data_json, 1)
    out_index = out_dir / "index.html"
    out_index.write_text(html, encoding="utf-8")
    print(f"✅ 已生成 iOS 图库（{note}）：{out_index}")
    return out_index


def serve(out_dir: Path, port: int) -> None:
    import http.server
    import socket
    import functools

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(out_dir))
    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", port), handler)
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except OSError:
        ip = "127.0.0.1"
    print("\n📱 本地服务器已启动 —— iPhone 连同一 WiFi，用 Safari 打开：")
    print(f"      http://{ip}:{port}/")
    print(f"   或本机：http://127.0.0.1:{port}/")
    print("   在 Safari 里点「分享 → 添加到主屏幕」即可当 App 离线使用。按 Ctrl+C 停止。\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="把图库渲染为 iOS 优化的响应式页面（不重新分析）")
    p.add_argument("--data", type=Path, default=DEFAULT_DATA, help="library.json 路径")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT, help="输出目录")
    p.add_argument("--title", default=None, help="页面标题")
    p.add_argument("--open", action="store_true", help="生成后用浏览器打开")
    p.add_argument("--serve", action="store_true", help="生成后起本地服务器（真机访问）")
    p.add_argument("--port", type=int, default=8000, help="--serve 的端口")
    args = p.parse_args(argv)

    index = build(args.data, args.out, args.title)
    if args.open:
        webbrowser.open(index.as_uri())
    if args.serve:
        serve(args.out, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
