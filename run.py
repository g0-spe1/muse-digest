#!/usr/bin/env python
"""MuseDigest CLI orchestrator.

采集/导入 -> 分析 -> 合并进持久图库 -> 生成图库页面

示例：
    python run.py                                  # 采集订阅源，合并进图库
    python run.py --import "D:\\我的照片"            # 分析本地文件夹里的照片
    python run.py --import a.jpg b.jpg --category 人像
    python run.py --backend artimuse_browser --open
    python run.py --rebuild --open                 # 不重新分析，仅用现有图库重建页面
    python run.py --fresh                           # 清空后重新开始
    python run.py --clear                           # 清空图库并退出
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import webbrowser
from pathlib import Path

# Make the package importable when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from muse_digest.analyze import get_analyzer
from muse_digest.categorize import categorize_images
from muse_digest.collect import collect_articles
from muse_digest.config import load_config
from muse_digest.download import download_images
from muse_digest.extract import enrich_articles
from muse_digest.gallery import build_gallery
from muse_digest.ingest import ingest_local_images
from muse_digest.library import (clear_library, load_library, merge_items,
                                 save_library)
from muse_digest.net import PoliteClient

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"


def setup_logging(verbose: bool) -> None:
    # Windows consoles default to GBK; force UTF-8 so logs/output never crash on
    # non-ASCII article titles or symbols.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("muse_digest").setLevel(logging.DEBUG if verbose else logging.INFO)


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="MuseDigest — 摄影/设计灵感采集与图库")
    p.add_argument("--config", default=None, help="config.yaml 路径")
    p.add_argument("--backend", default=None,
                   help="分析后端：heuristic | artimuse_browser | artimuse_local（覆盖配置）")
    p.add_argument("--limit", type=int, default=None, help="本次最多分析多少张（覆盖配置）")
    p.add_argument("--import", dest="import_paths", nargs="+", default=None,
                   metavar="PATH", help="导入本地图片/文件夹进行分析（不走网络采集）")
    p.add_argument("--category", default=None, help="给导入的整批图片打的题材标签")
    p.add_argument("--fresh", action="store_true", help="清空现有图库后再运行")
    p.add_argument("--rebuild", action="store_true", help="不重新分析，仅用现有图库重建页面")
    p.add_argument("--clear", action="store_true", help="清空图库并退出")
    p.add_argument("--open", action="store_true", help="完成后在浏览器中打开图库")
    p.add_argument("--verbose", action="store_true", help="调试日志")
    return p.parse_args(argv)


def _analyze(items, backend, analyzer_cfg, log):
    """对一批图片就地分析，单图失败回退 heuristic。"""
    log.info("用后端 '%s' 分析 %d 张图片...", backend, len(items))
    analyzer = get_analyzer(backend, analyzer_cfg)
    with analyzer:
        for i, item in enumerate(items, 1):
            try:
                item.analysis = analyzer.analyze(item)
            except Exception as e:
                log.warning("第 %s 张分析失败（%s），回退 heuristic。", item.id, e)
                item.analysis = analyzer.fallback(item, reason=str(e))
            log.info("  已分析 %d/%d (%s)", i, len(items), item.analysis.backend)


def main(argv=None) -> int:
    args = parse_args(argv)
    setup_logging(args.verbose)
    log = logging.getLogger("muse_digest.run")

    cfg = load_config(args.config)
    backend = args.backend or cfg.analyzer.get("backend", "heuristic")
    dl = cfg.download
    images_dir = DATA_DIR / "images"
    gallery_dir = DATA_DIR / "gallery"
    library_path = DATA_DIR / "library.json"
    title = cfg.output.get("title", "MuseDigest")

    # --- 管理命令 -------------------------------------------------------
    if args.clear:
        clear_library(library_path, images_dir)
        if gallery_dir.exists():
            import shutil
            shutil.rmtree(gallery_dir)
        print("已清空图库。")
        return 0

    if args.fresh:
        clear_library(library_path, images_dir)
        log.info("已清空图库，重新开始。")

    library = load_library(library_path)

    # --- 仅重建 ---------------------------------------------------------
    if args.rebuild:
        if not library:
            log.error("图库为空，没有可重建的内容。先运行一次采集或导入。")
            return 1
        index_path = build_gallery(library, [], gallery_dir, images_dir,
                                   title=title, backend="library")
        print(f"\n已用现有图库重建页面，共 {len(library)} 张。")
        print(f"   图库：{index_path}")
        if args.open:
            webbrowser.open(index_path.as_uri())
        return 0

    articles = []

    # --- 获取本次新图片：导入 或 采集 -----------------------------------
    if args.import_paths:
        new_items = ingest_local_images(
            args.import_paths, images_dir,
            thumb_max_px=dl.get("thumbnail_max_px", 900),
            category=args.category or "Uncategorized",
        )
        if not new_items:
            log.error("没有可导入的图片 —— 请检查路径是否为图片或文件夹。")
            return 1
    else:
        client = PoliteClient(
            user_agent=dl.get("user_agent", "MuseDigest/1.0"),
            delay=dl.get("request_delay_seconds", 1.5),
            timeout=dl.get("timeout_seconds", 20),
            respect_robots=dl.get("respect_robots", True),
        )
        articles = collect_articles(cfg.feeds, cfg.collection.get("max_articles_per_feed", 8))
        if not articles:
            log.error("未采集到任何文章 —— 请检查订阅源 URL 或网络。")
            return 1
        enrich_articles(articles, client, cfg.collection.get("max_images_per_article", 2))
        new_items = download_images(
            articles, client, images_dir,
            max_total=args.limit or cfg.collection.get("max_images_total", 24),
            thumb_max_px=dl.get("thumbnail_max_px", 900),
            min_px=dl.get("min_image_px", 400),
        )
        if not new_items:
            log.error("未下载到任何图片 —— 没有可分析的内容。")
            return 1
        categorize_images(new_items, cfg.categories)

    # --- 分析 -----------------------------------------------------------
    _analyze(new_items, backend, cfg.analyzer, log)

    # --- 合并进图库并保存 ----------------------------------------------
    library = merge_items(library, new_items)
    save_library(library_path, library)

    # --- 生成页面（展示整个图库）--------------------------------------
    index_path = build_gallery(library, articles, gallery_dir, images_dir,
                               title=title, backend=backend)

    print(f"\n完成。本次新增/更新 {len(new_items)} 张；图库现共 {len(library)} 张，"
          f"分布于 {len({it.category for it in library})} 个分类。")
    print(f"   图库：{index_path}")
    print(f"   图库数据：{library_path}")

    if args.open:
        webbrowser.open(index_path.as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
