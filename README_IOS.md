# MuseDigest · iOS 适配图库

面向 **iPhone / iPad（iOS Safari）** 优化的响应式图库版本。它把 MuseDigest 已生成的图库
（`data/library.json` + 缩略图）渲染成一个**自包含、可离线携带、可添加到主屏幕**的移动端页面，
针对触摸操作、刘海安全区、瀑布流自适应做了专门适配。

> 它**不重新采集、不重新分析**任何图片，只是把现有图库换一套移动端 UI 呈现。
> 想采集 / 分析请继续用主流程的 `python run.py`（见 [README.md](README.md)）。

## 一分钟上手

```bash
# 1) 先有图库（任选其一）
python run.py --limit 12 --backend heuristic        # 采集并分析，生成 data/library.json
#   或者你已经跑过、data/library.json 已存在

# 2) 生成 iOS 图库并打开
python build_ios_gallery.py --open                  # 输出 data/gallery-ios/index.html
```

或直接双击 **`start-ios.bat`**（Windows）/ 运行 **`./start-ios.sh`**（macOS / Linux）。

> 没有 `data/library.json` 也能跑：会回退到内置**示例数据**，方便你先看效果。

## 在 iPhone 真机上看（推荐）

iOS Safari 直接打开 `file://` 时不能加载外部图片/数据，所以用内置的局域网服务器最顺：

```bash
python build_ios_gallery.py --serve                 # 默认 8000 端口
```

终端会打印一个 `http://<你的电脑IP>:8000/` 地址。让 **iPhone 连同一个 WiFi**，在 Safari 里
打开该地址即可。再点 Safari 的 **「分享 → 添加到主屏幕」**，就能像 App 一样全屏、离线使用。

## 针对 iOS 做了什么适配

| 方面 | 适配 |
|---|---|
| **安全区 / 刘海** | `viewport-fit=cover` + `env(safe-area-inset-*)`，内容不被刘海和底部小白条遮挡 |
| **全屏 Web App** | `apple-mobile-web-app-capable`、状态栏样式、`apple-mobile-web-app-title`，支持「添加到主屏幕」 |
| **触摸手势** | 灯箱**左右滑**切换、**下滑关闭**；详情面板**下拉关闭**（iOS 底部抽屉手势） |
| **底部抽屉详情** | iOS 风格 bottom-sheet（带 grip 把手），而非桌面弹窗 |
| **自适应瀑布流** | 手机 2 列、平板 3–5 列（按宽度自动），`content-visibility` 优化长列表滚动 |
| **顺滑滚动** | `-webkit-overflow-scrolling:touch`、`overscroll-behavior` 防止背景跟随回弹 |
| **点按体验** | 去掉点击高亮、消除 300ms 双击缩放延迟、按钮 `touch-action:manipulation` |
| **深/浅色** | 跟随系统 `prefers-color-scheme`，`theme-color` 同步状态栏配色 |
| **动态视口** | 用 `svh`/`dvh` 适配 Safari 地址栏收起/展开导致的高度变化 |

功能与桌面版图库一致：概览统计、分数环、题材筛选、来源/排序、主色调色带、**8 维度雷达图**、
逐维度分数、创意灵感、灯箱大图。全部用原生 JS + 内联 SVG，**零依赖、可离线**。

## 命令行参数

```bash
python build_ios_gallery.py [--data PATH] [--out DIR] [--title T] [--open] [--serve] [--port N]
```

| 参数 | 默认 | 作用 |
|---|---|---|
| `--data` | `data/library.json` | 图库数据文件 |
| `--out` | `data/gallery-ios` | 输出目录（会把用到的缩略图复制进 `out/images/`） |
| `--title` | `妙析速递` | 页面标题 |
| `--open` | — | 生成后用默认浏览器打开 |
| `--serve` | — | 起局域网静态服务器（真机访问） |
| `--port` | `8000` | `--serve` 端口 |

## `library.json` 数据结构

构建器对字段命名比较**宽容**（会做归一化），最简到最全大致如下。分数支持 0–10 或 0–100
（会自动归一到 0–10）；缺图时用主色调生成渐变占位，因此即便没有图片文件也能展示。

```jsonc
[
  {
    "id": "abc123",
    "title": "晨雾中的山脊线",
    "source": "PetaPixel",
    "source_url": "https://…",          // 可选，详情里给出回源链接
    "image": "images/abc123.jpg",        // 相对/绝对路径或 http(s) URL；缺省则用主色渐变
    "category": "Landscape",             // 内部英文键，UI 显示对应中文
    "score": 8.4,                         // 0–10 或 0–100；缺省则取 comprehensive 维度
    "dominant_colors": ["#2a3b4d", "#6d8aa3", "#c7d6df"],  // 最多 5 个
    "analysis": {
      "backend": "heuristic",            // heuristic | artimuse_browser | artimuse_local
      "fallback": false,                  // 是否为单图失败回退（UI 标「回退」徽标）
      "summary": "整体评析的中文文字…",
      "dimensions": {                     // 8 维度，可只给分数，也可带 text
        "composition_design":        {"score": 8.6, "text": "…"},
        "visual_elements_structure": {"score": 8.0},
        "technical_execution":       {"score": 8.3},
        "originality_creativity":    {"score": 7.4},
        "theme_communication":       {"score": 8.1},
        "emotion_viewer_resonance":  {"score": 8.5},
        "overall_aesthetic":         {"score": 8.7},
        "comprehensive":             {"score": 8.4}
      },
      "inspiration": ["利用大气透视制造纵深", "把地平线压低给雾更多空间"]
    }
  }
]
```

顶层也可以是 `{"title": "...", "items": [ … ]}`。维度的内部英文键与中文映射沿用 ArtiMuse 的
8 个专家维度（构图与设计 / 视觉元素与结构 / 技术执行 / 原创性与创意 / 主题与传达 /
情感与观者共鸣 / 整体格调 / 综合评估）。

## 文件

```
ios/index.html            # iOS 优化的图库模板（也可单独双击打开，带内置示例数据）
build_ios_gallery.py      # 把 data/library.json 注入模板 → data/gallery-ios/index.html
start-ios.bat             # Windows 一键：构建并打开
start-ios.sh              # macOS / Linux 一键：构建并打开
```
