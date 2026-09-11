# BabelDOC 本地增强版

这是一个面向英文科研 PDF 的本地翻译工具，通过 OpenAI 兼容接口生成中文单语和双语 PDF。

本项目基于原版 [BabelDOC](https://github.com/funstory-ai/BabelDOC) 修改。欢迎访问、关注并支持原版仓库，了解上游项目的最新功能、版本和社区进展。

当前版本针对实际论文翻译做了以下调整：

- 拒绝并重试 API 返回的空译文，避免正文被空内容覆盖。
- 为推理模型提供更充足的输出 token。
- 改善短文本和中英文 token 比例不同造成的误判。
- 保留论文作者、机构、网址和图形内部文字的原始排版。
- 翻译正文、标题和图表注释。
- 默认不在 PDF 页眉添加推广文字。
- 支持通过用户目录中的 TOML 文件保存 API 和常用参数。

## 环境要求

- Linux 或 WSL
- Git
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- 可用的 OpenAI 兼容 API

不要求提前安装 Python。下面的命令会让 uv 自动准备 Python 3.12。

## 快速开始

### 1. 安装 uv

先检查系统中是否已有 uv：

```bash
uv --version
```

如果提示 `uv: command not found`，使用官方安装脚本：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

如果系统没有 `curl`，也可以使用：

```bash
wget -qO- https://astral.sh/uv/install.sh | sh
```

安装后重新打开终端，再确认：

```bash
uv --version
```

### 2. 克隆并安装当前源码

在本项目的仓库页面复制实际的 clone 地址，然后执行以下命令。`YOUR_REPOSITORY_URL` 和 `YOUR_REPOSITORY_DIRECTORY` 是占位符，需要替换成实际内容：

```bash
git clone git@github.com:KnightOrNot/MyBabelDOC.git
cd MyBabelDoc
uv tool install --python 3.12 --editable .
uv tool update-shell
```

如果已经克隆了仓库，直接进入仓库根目录，从 `uv tool install` 开始执行即可。

`--editable` 会让命令使用当前仓库中的源码。以后修改 Python 文件时无需重复安装。如果此前已经安装过同名工具，可强制替换：

```bash
uv tool install --force --python 3.12 --editable .
```

`uv tool update-shell` 会把 uv 的工具目录加入 `PATH`。执行后重新打开终端，再检查：

```bash
babeldoc --version
```

### 3. 创建配置文件

以下命令需要在刚才克隆的仓库根目录中执行：

```bash
mkdir -p ~/.config/babeldoc
cp ./babeldoc.example.toml ~/.config/babeldoc/babeldoc.toml
chmod 600 ~/.config/babeldoc/babeldoc.toml
```

编辑 `~/.config/babeldoc/babeldoc.toml` ：

- 简略配置如下：

```toml
[babeldoc]
openai = true
openai-model = "模型名称"                    # 需要自己填写
openai-base-url = "https://你的接口地址/v1"    # 需要自己填写
openai-api-key = "你的 API 密钥"                

lang-in = "en-US"
lang-out = "zh-CN"
qps = 4
pool-max-workers = 4

# 必须使用绝对路径，不能使用 ~ 或 $HOME。
output = "/home/你的用户名/paper/translate"

debug = false
watermark-output-mode = "no_watermark"

# 不需要自动术语表时建议关闭，避免兼容接口返回空 JSON。
no-auto-extract-glossary = true
```

- 详细配置如下：

```toml
[babeldoc]
# Basic settings
debug = false
lang-in = "en-US"
lang-out = "zh-CN"
qps = 10
output = "/home/knight/paper/translate"

# PDF processing options
split-short-lines = false
short-line-split-factor = 0.8
skip-clean = false
dual-translate-first = false
disable-rich-text-translate = false
use-alternating-pages-dual = false
watermark-output-mode = "no_watermark"  # Choices: "watermarked", "no_watermark", "both"
max-pages-per-part = 50  # Automatically split the document for translation and merge it back.
only-include-translated-page = false # Only include translated pages in the output PDF. Effective only when `pages` is used.
# no-watermark = false  # DEPRECATED: Use watermark-output-mode instead
skip-scanned-detection = false  # Skip scanned document detection for faster processing
no-auto-extract-glossary = false
formular-font-pattern = "" # Font pattern for formula text
formular-char-pattern = "" # Character pattern for formula text
show-char-box = false # Show character bounding boxes (debug)
ocr-workaround = false # Use OCR workaround for scanned PDFs
rpc-doclayout = "" # RPC service host for document layout analysis
working-dir = "" # Working directory for translation
auto-enable-ocr-workaround = false # Enable automatic OCR workaround for scanned PDFs. See docs for interaction with ocr_workaround and skip_scanned_detection.
skip-form-render = false # Skip form rendering (default: False)
skip-curve-render = false # Skip curve rendering (default: False)
only-parse-generate-pdf = false # Only parse PDF and generate output PDF without translation (default: False)
remove-non-formula-lines = false # Remove non-formula lines from paragraph areas (default: False)
non-formula-line-iou-threshold = 0.2 # IoU threshold for paragraph overlap detection (default: 0.2)
figure-table-protection-threshold = 0.3 # IoU threshold for figure/table protection (default: 0.3)

# Translation service
openai = true
openai-model = "deepseek-flash"
openai-base-url = "https://api.deepseek.com"
openai-api-key = "sk-0139fc46905c4d819e7df11cdbe02275"
enable-json-mode-if-requested = false  # Enable JSON mode when requested (default: false)
disable-same-text-fallback = false # Disable fallback translation when LLM output matches input text (default: false)
pool-max-workers = 8  # Maximum worker threads for task processing (defaults to QPS value if not set)

# Glossary Options (Optional)
# glossary-files = "/path/to/glossary1.csv,/path/to/glossary2.csv"

# Output control
no-dual = false
no-mono = false
min-text-length = 5
report-interval = 0.5

# Offline assets management
# Uncomment one of these options as needed:
# generate-offline-assets = "/path/to/output/dir"
# restore-offline-assets = "/path/to/offline_assets_package.zip"
```

真实配置中包含 API 密钥，不要把它复制到仓库或提交到 Git。

### 4. 让命令自动读取配置

将下面的函数加入 `~/.bashrc` 的最后。它只引用用户配置目录，不依赖仓库的克隆位置：

```bash
babeldoc() {
    command babeldoc -c "$HOME/.config/babeldoc/babeldoc.toml" "$@"
}
```

让配置立即生效：

```bash
source ~/.bashrc
babeldoc --version
babeldoc --help
```

此后可以在任意路径使用 `babeldoc`，无需激活虚拟环境，也无需重复输入 API 参数。

## 翻译文档

翻译单个 PDF：

```bash
babeldoc --files "/absolute/path/to/paper.pdf"
```

翻译多个 PDF：

```bash
babeldoc \
    --files "/absolute/path/to/paper-1.pdf" \
    --files "/absolute/path/to/paper-2.pdf"
```

忽略已有译文缓存并重新翻译：

```bash
babeldoc --files "/absolute/path/to/paper.pdf" --ignore-cache
```

临时指定输出目录：

```bash
babeldoc \
    --files "/absolute/path/to/paper.pdf" \
    --output "/absolute/path/to/output"
```

程序通常会生成：

- `*.zh-CN.mono.pdf`：中文单语版。
- `*.zh-CN.dual.pdf`：原文与译文双语版。

## 翻译指定页面

使用 `--pages` 指定页面：

```bash
babeldoc --files "/absolute/path/to/paper.pdf" --pages 1-5
```

科研论文的正文经常跨页。检查第一页时建议同时包含第二页：

```bash
babeldoc \
    --files "/absolute/path/to/paper.pdf" \
    --pages 1-2 \
    --ignore-cache
```

只解析第一页会截断延续到第二页的段落，例如第一页末尾可能留下 `en-` 之类的断词。

# 

## 预下载资源

首次使用前可以下载并校验字体、CMap 和版面模型：

```bash
babeldoc --warmup
```

资源默认保存在：

```text
~/.cache/babeldoc/
```

正常翻译会重复使用这些资源。

生成可搬运的离线资源包：

```bash
babeldoc --generate-offline-assets "/absolute/path/to/assets"
```

从离线包恢复资源：

```bash
babeldoc --restore-offline-assets "/absolute/path/to/offline_assets_xxx.zip"
```

`generate-offline-assets` 和 `restore-offline-assets` 是独立操作，执行后程序会退出，不要把它们写入日常翻译配置。

## 常用参数

| 参数                             | 用途                |
| ------------------------------ | ----------------- |
| `--files PATH`                 | 添加一个待翻译 PDF，可重复使用 |
| `--pages RANGE`                | 翻译指定页面，例如 `1-5`   |
| `--output PATH`                | 指定输出目录            |
| `--ignore-cache`               | 忽略译文缓存，强制重新请求 API |
| `--no-dual`                    | 不生成双语 PDF         |
| `--no-mono`                    | 不生成单语 PDF         |
| `--qps NUMBER`                 | 设置 API 每秒请求数      |
| `--pool-max-workers NUMBER`    | 设置翻译工作线程数         |
| `--no-auto-extract-glossary`   | 关闭自动术语提取          |
| `--watermark-output-mode MODE` | 控制页眉输出模式          |
| `--debug`                      | 输出详细日志和调试中间文件     |
| `--warmup`                     | 下载并校验本地资源         |

查看当前版本支持的完整参数：

```bash
babeldoc --help
```

## 常见问题

### Translation service returned an empty response

API 返回了空的 `message.content`。程序会自动重试三次；仍然为空时保留原文，避免正文消失。

如果警告来自自动术语提取，并且不需要术语表，请在配置中设置：

```toml
no-auto-extract-glossary = true
```

### Translation result is too long or too short

程序会检查较长段落的输入输出 token 比例。明显异常的结果会转入简单翻译流程。少于 10 token 的短标题和标签不会使用严格比例检查。

### 资源下载超时

重新运行 `babeldoc --warmup`。已经下载且校验通过的资源会直接复用。如果网络需要代理，应先在终端设置 `HTTP_PROXY` 和 `HTTPS_PROXY`。

### 命令只能在仓库目录中运行

确认已执行 `uv tool update-shell`，重新打开终端，然后检查：

```bash
uv tool dir --bin
type babeldoc
```

如果 `type babeldoc` 仍然找不到命令，再执行一次 `uv tool update-shell`，并重新打开终端。

## 开发与验证

先进入自己实际克隆的仓库根目录，再安装开发依赖并运行测试和代码检查：

```bash
uv sync --python 3.12 --group dev
uv run pytest -q tests
uv run ruff check babeldoc tests
```

## 许可证

本项目基于原版 [BabelDOC](https://github.com/funstory-ai/BabelDOC) 修改，属于其派生版本，不是从零开始编写的独立实现。原始代码的版权仍归原版权持有人所有。推荐使用者同时访问并支持原版仓库。

原始代码和当前派生版本均按照 **GNU Affero General Public License Version 3（AGPL-3.0）** 发布。使用、修改或分发本项目时，应遵守 [LICENSE](./LICENSE) 中的完整条款。

当前派生版本于 2026 年 9 月开始修改，主要增加了 API 空响应保护、翻译结果校验、图形文字处理、作者信息保护、默认无推广页眉以及本地配置工作流。详细说明见 [NOTICE](./NOTICE)。

当前维护者仅计划将其用于个人和非商业用途；这不会给 AGPL 添加“禁止商业使用”等额外限制，也不会改变原许可证授予其他使用者的权利。
