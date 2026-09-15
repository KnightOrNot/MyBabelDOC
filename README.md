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
- Git 和 curl
- [pyenv](https://github.com/pyenv/pyenv)：安装并选择 Python
- [uv](https://docs.astral.sh/uv/getting-started/installation/)：创建 `.venv`、同步依赖和运行项目
- 可用的 OpenAI 兼容 API

项目支持 Python 3.10～3.13，当前开发环境固定为 Python 3.12.14。下面的流程由 pyenv 提供 Python，由 uv 管理项目环境；不会让 uv 另外下载一套 Python。

## 快速开始

### 1. 安装并配置 pyenv

先检查 pyenv：

```bash
pyenv --version
```

如果尚未安装，在 Ubuntu 或 WSL 中先安装编译 Python 所需的依赖：

```bash
sudo apt update
sudo apt install -y \
    build-essential curl git libbz2-dev libffi-dev liblzma-dev \
    libncursesw5-dev libreadline-dev libsqlite3-dev libssl-dev \
    libxml2-dev libxmlsec1-dev tk-dev xz-utils zlib1g-dev
```

然后使用 pyenv 官方安装脚本，并配置当前 shell：

```bash
curl -fsSL https://pyenv.run | bash
~/.pyenv/bin/pyenv init --install
exec "$SHELL"
pyenv --version
```

其他 Linux 发行版请先按照 [pyenv 的构建环境说明](https://github.com/pyenv/pyenv/wiki#suggested-build-environment)安装对应依赖。

### 2. 安装 uv

先检查 uv：

```bash
uv --version
```

如果尚未安装，使用 uv 官方安装脚本：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
exec "$SHELL"
uv --version
```

### 3. 克隆仓库并选择 Python

仓库可以克隆到任意目录：

```bash
git clone https://github.com/KnightOrNot/MyBabelDOC.git
cd MyBabelDOC
```

仓库中的 `.python-version` 指定了 Python 3.12.14。让 pyenv 安装这个具体版本，然后确认当前解释器：

```bash
pyenv install -s 3.12.14
pyenv version
python --version
pyenv which python
```

进入仓库及其子目录时，pyenv 会根据 `.python-version` 自动选择这套 Python，不会改变其他项目的全局版本。

### 4. 使用 uv 创建项目环境

让 uv 明确使用 pyenv 当前选中的解释器，并按照仓库中的 `uv.lock` 同步依赖：

```bash
uv sync --locked --no-managed-python --python "$(pyenv which python)"
```

uv 会在仓库中创建 `.venv`，并以 editable 模式安装当前源码。修改仓库中的 Python 文件后会直接生效。检查环境：

```bash
uv run python --version
uv run babeldoc --version
```

如果 `uv sync --locked` 提示 `uv.lock` 与 `pyproject.toml` 不一致，开发者应先运行 `uv lock` 更新锁文件；普通使用者不应随意更新锁文件。

### 5. 创建配置文件

以下命令需要在刚才克隆的仓库根目录中执行：

```bash
mkdir -p ~/.config/babeldoc
cp ./babeldoc.example.toml ~/.config/babeldoc/babeldoc.toml
chmod 600 ~/.config/babeldoc/babeldoc.toml
```

编辑 `~/.config/babeldoc/babeldoc.toml`，至少填写下面几项：

```toml
[babeldoc]
openai = true
openai-model = "模型名称"
openai-base-url = "https://你的接口地址/v1"
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

其余可选项和说明见仓库中的 [`babeldoc.example.toml`](./babeldoc.example.toml)。真实配置中包含 API 密钥，不要把它复制到仓库或提交到 Git。

### 6. 运行 BabelDOC

在仓库根目录中可以直接运行：

```bash
uv run babeldoc \
    -c "$HOME/.config/babeldoc/babeldoc.toml" \
    --files "/absolute/path/to/paper.pdf"
```

如果希望在任意目录中直接使用 `babeldoc`，先在仓库根目录运行 `pwd`，记下输出的绝对路径。然后把下面内容加入 `~/.bashrc`，并将 `/absolute/path/to/MyBabelDOC` 替换为刚才的实际输出：

```bash
export BABELDOC_PROJECT_DIR="/absolute/path/to/MyBabelDOC"
unalias babeldoc 2>/dev/null
babeldoc() {
    command uv run --project "$BABELDOC_PROJECT_DIR" babeldoc \
        -c "$HOME/.config/babeldoc/babeldoc.toml" \
        "$@"
}
```

重新加载 shell 配置并检查命令：

```bash
source ~/.bashrc
babeldoc --version
babeldoc --help
```

这个函数始终使用指定仓库的 `.venv` 和源码，但待翻译文件的相对路径仍以当前终端目录为基准。建议对 PDF 和输出目录使用绝对路径。

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

检查 `~/.bashrc` 中的 `BABELDOC_PROJECT_DIR` 是否已经替换为实际仓库路径：

```bash
type babeldoc
printf '%s\n' "$BABELDOC_PROJECT_DIR"
test -f "$BABELDOC_PROJECT_DIR/pyproject.toml" && echo "project found"
```

修改后运行 `source ~/.bashrc`。如果只在仓库目录中使用，则直接执行 `uv run babeldoc ...`，无需配置全局函数。

## 开发与验证

先进入自己实际克隆的仓库根目录，再安装开发依赖并运行测试和代码检查：

```bash
pyenv install -s 3.12.14
uv sync --locked --no-managed-python --python "$(pyenv which python)"
uv run pytest -q tests
uv run ruff check babeldoc tests
```

## 许可证

本项目基于原版 [BabelDOC](https://github.com/funstory-ai/BabelDOC) 修改，属于其派生版本，不是从零开始编写的独立实现。原始代码的版权仍归原版权持有人所有。推荐使用者同时访问并支持原版仓库。

原始代码和当前派生版本均按照 **GNU Affero General Public License Version 3（AGPL-3.0）** 发布。使用、修改或分发本项目时，应遵守 [LICENSE](./LICENSE) 中的完整条款。

当前派生版本于 2026 年 9 月开始修改，主要增加了 API 空响应保护、翻译结果校验、图形文字处理、作者信息保护、默认无推广页眉以及本地配置工作流。详细说明见 [NOTICE](./NOTICE)。

当前维护者仅计划将其用于个人和非商业用途；这不会给 AGPL 添加“禁止商业使用”等额外限制，也不会改变原许可证授予其他使用者的权利。
