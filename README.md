# MuseDigest · 妙析速递

> English version: [README_EN.md](README_EN.md)

自动收集最新的**摄影 / 设计 / 创意产业**资讯，编制**分类影像集**，从**设计与美学**视角分析每张图片 —— 最终呈现为一个自包含的**交互式 HTML 图库**（界面以中文为主）。

它是 [ArtiMuse](../README.md) 图像美学评估模型的配套工具：分析沿用 ArtiMuse 的 8 个专家维度（构图与设计、视觉元素与结构、技术执行、原创性与创意、主题与传达、情感与观者共鸣、整体格调、综合评估）。

```
采集 (RSS) → 提取 (图片) → 下载 (缩略图) → 分类 (题材)
          → 分析 (美学) → 交互式图库
```

## 一键运行（最简单）

进入 `muse-digest/` 文件夹，**双击**：

| 双击文件 | 作用 |
|---|---|
| **`menu.bat`** | 弹出**中文菜单**（推荐）：1 采集 / 2 ArtiMuse在线 / 3 登录 / 4 自检 / 5 导入本地图片 / 6 打开上次图库 / 7 清空 |
| **`start.bat`** | 零配置：采集资讯 → 生成图库 → 自动打开浏览器（heuristic 后端，无需 GPU/登录） |
| **`start-artimuse.bat`** | 真实美学评分：用系统 Edge 打开演示页让你登录 → 逐张分析 → 打开带雷达图的图库 |
| **`import-photos.bat`** | **把你自己的图片或文件夹拖到它图标上** → 直接分析你的照片并加入图库 |

> 双击会弹出一个命令行窗口显示中文进度；跑完后浏览器自动打开图库。窗口会停在
> 提示按键处，按一下即可关闭。想多采集几张就用命令行追加参数，例如 `start.bat --limit 20`。

### 放到桌面（更方便）

双击 **`make-shortcuts.bat`**，会在桌面自动创建三个快捷方式：
**「MuseDigest 菜单」「MuseDigest 一键运行」「MuseDigest ArtiMuse在线」**，
以后从桌面直接双击即可运行。

> 手动方式：右键 `menu.bat` →「发送到」→「桌面快捷方式」。
> PowerShell 菜单脚本是 `start-menu.ps1`，`menu.bat` 以 `-ExecutionPolicy Bypass`
> 调用它，因此即使系统禁止运行脚本也能用。

## 快速开始（命令行）

```bash
# 在 muse-digest/ 文件夹下，使用项目的 .venv
pip install -r requirements.txt
python run.py --limit 12 --backend heuristic --open
```

这会从 `config.yaml` 中的订阅源采集资讯，构建影像集，并打开 `data/gallery/index.html`。**heuristic** 后端不运行深度美学模型，但会**真实读取每张图的像素**（亮度、对比度、饱和度、色温、色彩丰富度、锐度、曝光裁切、明暗平衡、主色调），据此给出**逐图不同**的中文分析与启发式分数（雷达图据此点亮）。这是"画面统计"，不是 ArtiMuse 的美学判断 —— 想要真正的美学评分请用 `artimuse_browser`/`artimuse_local`。

## 交互式图库功能

生成的 `data/gallery/index.html` 是一个自包含、可离线打开的应用：

- **概览统计** —— 图片 / 分类 / 来源数量、平均分，以及彩色的分类占比条。
- **影像网格** —— 瀑布流布局，每张图片带**分数环**、题材标签和底部**主色调色带**。
- **主色调色板** —— 详情抽屉里展示每张图提取的 5 个主色（带 #hex），配色一眼可见。
- **筛选与排序** —— 题材标签、来源下拉框，以及按分数 / 来源排序。
- **详情抽屉** —— 完整评析，含 8 个美学维度的**雷达图**（当后端提供逐维度分数时点亮）、逐维度分数标签、"创意灵感"要点，以及图片间的 **← / →** 导航。
- **灯箱** —— 点击抽屉图片可放大查看，支持方向键导航。

## 导入自己的照片分析

除了从网络采集，你也可以**主动导入本地图片**来分析（用 heuristic 后端会得到逐图不同的
画面分析；用 ArtiMuse 后端则得到真实美学评分）：

- **最简单**：把图片或整个文件夹**拖到 `import-photos.bat` 图标上**。
- **菜单**：双击 `menu.bat` → 选 **5**，输入路径。
- **命令行**：
  ```bash
  python run.py --import "D:\我的照片"                 # 整个文件夹（递归）
  python run.py --import a.jpg b.jpg --category 人像     # 多个文件 + 打题材标签
  python run.py --import "D:\照片" --backend artimuse_browser   # 用 ArtiMuse 评分
  ```
  支持 jpg/png/webp/bmp/t/tiff/gif；按内容自动去重；来源标记为「本地导入」。

## 图库管理

图库是**持久累积**的：每次采集或导入都会把结果合并进 `data/library.json`（按 id 去重），
页面展示**整个图库**。用顶部的题材标签、来源下拉、排序即可管理浏览。

| 命令 / 菜单 | 作用 |
|---|---|
| `python run.py --rebuild` | 不重新分析，仅用现有图库**重建并打开**页面（菜单 6 = 打开上次图库） |
| `python run.py --fresh` | **清空**后重新开始本次运行 |
| `python run.py --clear` | 清空整个图库（json + 缩略图）并退出（菜单 7） |

> 数据都在 `data/` 下：`library.json`（全部条目+分析）、`images/`（缩略图）、
> `gallery/index.html`（可离线携带的页面）。删掉 `data/` 即彻底重置。

## 分析器后端

通过 `--backend` 或 `config.yaml` 中的 `analyzer.backend` 选择：

| 后端 | 功能 | 需要 |
|---|---|---|
| `heuristic` | 读取像素统计（色彩/明暗/锐度/主色…）生成**逐图不同**的中文分析与启发式分数。总是可用。 | 无 |
| `artimuse_browser` | 在已登录的浏览器中驱动**官方演示**（artimuse.intern-ai.org.cn），抓取真实分数与 8 维度分析。 | `playwright`、一次手动登录 |
| `artimuse_local` | 在本地以 4 位精度运行 **InternVL3-8B**（禁用 flash-attn）。完全本地、可复现。 | 父项目的重型依赖、已下载的检查点、CUDA GPU |

任何单张图片失败时，管道都会**自动回退到 `heuristic`**，确保每次运行都能完成。回退会在图库中标记。

### `artimuse_browser`（"在线"方案）
ArtiMuse **没有公开 API**，也**没有 Hugging Face Space**；官方演示需要统一登录，所以唯一忠实的在线方案就是浏览器自动化。本项目**直接驱动系统自带的 Edge**（`config.yaml` 中 `channel: msedge`），因此**无需下载 chromium**。

```bash
# 一次性准备（只装 playwright，浏览器用系统 Edge）
pip install playwright

# 一次性登录（打开 Edge，手动登录 intern-ai.org.cn，回到终端按 Enter）
python tools/artimuse_login.py

# 用真实 ArtiMuse 在线分析跑一张自检图，打印抓到的分数+8维度
python tools/artimuse_selftest.py

# 正式运行（或直接双击 start-artimuse.bat）
python run.py --backend artimuse_browser --limit 3 --open
```

首次运行会用**持久化配置**（保存在 `.browser_profile/`）打开 Edge。登录一次后，后续运行复用该会话。

> 若你更想用 playwright 自带的 chromium，把 `config.yaml` 里 `analyzer.artimuse_browser.channel`
> 留空，并执行一次 `python -m playwright install chromium`。

#### 在线登录三步（图文）

1. **登录**：双击桌面「MuseDigest 菜单」→ 输入 **3**（仅登录）。会弹出 **Edge** 打开
   `artimuse.intern-ai.org.cn`；用你的 intern-ai.org.cn（书生）账号登录，没有就在该页注册。
   看到可上传图片的页面后，**回到黑色命令行窗口按 Enter**。会话存入 `.browser_profile/`，
   以后自动复用。
2. **自检**：菜单选 **4**。它用一张测试图跑通，打印抓到的总分+8维度。打印出内容 = 成功；
   若某维度为空，照打印结果微调选择器（见下）。
3. **正式跑**：双击「MuseDigest ArtiMuse在线」，或菜单选 **2**。

> 注意：`headless: false` 必须保持（要可见才能登录）；在线有速率限制，建议 `--limit 3~5`；
> 会话过期就再跑一次菜单 3。已实测：playwright 已装、系统 Edge 能正常启动。
> ❗ "用你的账号登录"这一步只能你本人做（intern-ai 的 SSO 决定），自动化替代不了。

#### 演示页结构（实测，便于排错）
通过一次无登录的探测，已确认官方演示页：

- **有 1 个 `input[type="file"]`** —— 上传走它（对隐藏 input 也有效），选择器可靠；
- **没有 `<button>` 元素** —— 用 div/span 做点击，多半"上传即自动评测"，所以提交按钮是尽力而为；
- **界面与输出是中文**（如「总分」「构图与设计」）—— 因此结果解析**以中文标题为主**匹配，
  英文为兜底（见 `_heading_candidates`），并把分数映射回内部英文键，雷达图据此点亮。

#### 首次调试指引
登录后的**结果页面布局尚未实测确认**（登录只能你本人完成）。所以首次请先跑
`python tools/artimuse_selftest.py`：

- 它会打印**抓到的整体分数 + 8 维度文本 + 逐维度分数**；
- 若某些维度为"(空)"或分数为 None，说明演示页的标题/数字位置与预期不同 ——
  对照打印结果，到 `muse_digest/analyze/artimuse_browser.py` 集中修改 `SELECTORS`
  （上传/提交）或 `_heading_candidates`（维度标题匹配）、`_SCORE_RE`/`_SCORE_CN_RE`（分数）即可；
- 任何单图失败都会**自动回退到中文 heuristic**，并在图库中标记，不会让整次运行中断。

> ⚠️ 这是自动化第三方界面：**易碎**（页面结构可能变化）、**有速率限制**、仅适合**小批量个人学习**。

### `artimuse_local`（4 位本地）
重量级且在 6 GB 笔记本 GPU 上 **显存吃紧**（慢：每张图片 8 次属性推理）。

1. 从父项目根安装依赖：`pip install -r ../requirements.txt`
2. 下载检查点到 `../checkpoints/ArtiMuse`（来自 https://huggingface.co/Thunderbolt215215/ArtiMuse ）。
3. 运行：`python run.py --backend artimuse_local --limit 1 --open`

`analyzer.artimuse_local` 下的配置控制 `model_path`、`device`、`load_in_4bit`、`use_flash_attn`、`max_new_tokens`。

## 配置

一切都在 [`config.yaml`](config.yaml)：`feeds`（订阅源）、`categories`（题材分类）、`collection`/`download`（限额），以及 `analyzer`（分析器设置）。CLI 参数（`--backend`、`--limit`）会覆盖对应的配置值。

界面的中文标签集中在 [`muse_digest/labels.py`](muse_digest/labels.py)（维度与题材的中文映射）；内部键保持英文，以便 ArtiMuse 的英文提示词和针对英文订阅源的关键词分类继续工作。

## 输出

```
data/
  images/                # 下载的学习用缩略图
  results/results.json   # 完整结构化结果（出处 + 分析）
  gallery/index.html     # 交互式、可离线携带的图库
```

## 负责任地使用

MuseDigest 遵守 `robots.txt`，对每个主机限速，下载**缩小尺寸的学习缩略图**（非全分辨率），并对每张图片**带署名并链接回来源**。它不重新托管媒体。请尊重各来源的条款；超出个人学习用途，请向版权方申请许可。
