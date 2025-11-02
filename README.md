# PDF to Long Screenshot Converter

将 PDF 文件转换为长截图（单张垂直拼接的图片）的 Python 命令行工具。

## 功能特性

- ✅ 支持多页 PDF 转换为单张长图
- ✅ 可自定义 DPI（72-300）控制输出质量
- ✅ 支持 PNG 和 JPEG 输出格式
- ✅ 可调节页面间距
- ✅ 自动处理透明背景（转换为白色）
- ✅ **智能裁剪空白区域**（自动移除页面四周的空白边距）
- ✅ 实时进度显示
- ✅ 支持最大 100MB 的 PDF 文件

## 系统要求

- Python 3.8 或更高版本
- poppler 系统依赖

### 安装 poppler

#### macOS
```bash
brew install poppler
```

#### Ubuntu/Debian
```bash
sudo apt-get install poppler-utils
```

#### Windows
1. 下载 poppler for Windows: https://github.com/oschwartz10612/poppler-windows/releases
2. 解压并将 `bin` 目录添加到系统 PATH

## 截图

![image](./screenshots/scratch_long_screenshot.png)

## 安装

1. 克隆或下载本项目

```bash
git clone https://github.com/build-your-own-x-with-ai/PDF-to-Long-Screenshot-Converter.git
cd PDF-to-Long-Screenshot-Converter
```

2. 安装 Python 依赖：
```bash
pip install -r requirements.txt
```

3. （可选）安装为包：
```bash
pip install -e .
```

## 快速开始

### 单文件转换

```bash
python -m src.cli input.pdf
```

### 批量转换整个目录

```bash
# 1. 将 PDF 文件放入 pdfs/ 目录
mkdir pdfs
cp *.pdf pdfs/

# 2. 运行批量转换
python batch_convert.py

# 3. 转换结果保存在 images/ 目录
```

> 📖 更多批量转换示例和使用场景，请查看 [批量转换使用指南](BATCH_USAGE.md)

## 使用方法

### 单文件转换

#### 基本用法

```bash
python -m src.cli input.pdf
```

这将在与输入文件相同的目录下生成 `input_long_screenshot.png`。

### 指定输出路径

```bash
python -m src.cli input.pdf -o output.png
```

### 自定义 DPI（分辨率）

```bash
python -m src.cli input.pdf --dpi 200
```

DPI 范围：72-300，默认 150

### 输出为 JPEG 格式

```bash
python -m src.cli input.pdf -f jpeg -q 90
```

- `-f, --format`: 输出格式（png 或 jpeg）
- `-q, --quality`: JPEG 质量（1-100，默认 85）

### 添加页面间距

```bash
python -m src.cli input.pdf --spacing 10
```

在每页之间添加 10 像素的白色间距。

### 跳过覆盖确认

```bash
python -m src.cli input.pdf -o existing.png --no-confirm
```

### 禁用自动裁剪

默认情况下，工具会自动裁剪页面四周的空白区域。如果你想保留原始页面的所有空白：

```bash
python -m src.cli input.pdf --no-crop
```

### 调整裁剪边距

自定义裁剪时保留的边距（默认 10 像素）：

```bash
python -m src.cli input.pdf --crop-margin 20
```

### 使用固定宽度（保留页面间空白）

如果你想保留原始的居中对齐效果而不是左对齐：

```bash
python -m src.cli input.pdf --fixed-width
```

#### 完整示例

```bash
python -m src.cli document.pdf -o output.jpg -f jpeg -q 95 --dpi 200 --spacing 5
```

### 批量转换（目录）

批量转换目录中的所有 PDF 文件：

#### 基本用法（默认 pdfs/ → images/）

```bash
python batch_convert.py
```

这将递归扫描 `pdfs/` 目录中的所有 PDF 文件，并将转换结果保存到 `images/` 目录，保持原有的目录结构。

#### 自定义输入输出目录

```bash
python batch_convert.py -i my_pdfs -o my_images
```

#### 跳过已转换的文件

```bash
python batch_convert.py --skip-existing
```

#### 仅处理顶层目录（不递归）

```bash
python batch_convert.py --no-recursive
```

#### 批量转换为 JPEG 格式

```bash
python batch_convert.py -f jpeg -q 90 --dpi 200
```

#### 静默模式（不显示进度）

```bash
python batch_convert.py --quiet
```

## 命令行参数

### 单文件转换 (src.cli)

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `input` | - | 输入 PDF 文件路径（必需） | - |
| `--output` | `-o` | 输出图像文件路径 | `<input>_long_screenshot.<format>` |
| `--dpi` | - | 分辨率（72-300） | 150 |
| `--format` | `-f` | 输出格式（png/jpeg） | png |
| `--quality` | `-q` | JPEG 质量（1-100） | 85 |
| `--spacing` | `-s` | 页面间距（像素） | 0 |
| `--no-confirm` | - | 跳过覆盖确认 | False |
| `--fixed-width` | - | 使用固定宽度（保留页面间空白） | False |
| `--no-crop` | - | 禁用自动裁剪空白 | False |
| `--crop-margin` | - | 裁剪时保留的边距（像素） | 10 |
| `--help` | `-h` | 显示帮助信息 | - |

### 批量转换 (batch_convert.py)

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--input-dir` | `-i` | 输入目录（包含 PDF 文件） | pdfs |
| `--output-dir` | `-o` | 输出目录（保存图片） | images |
| `--no-recursive` | - | 不递归搜索子目录 | False |
| `--skip-existing` | - | 跳过已存在的输出文件 | False |
| `--dpi` | - | 分辨率（72-300） | 150 |
| `--format` | `-f` | 输出格式（png/jpeg） | png |
| `--quality` | `-q` | JPEG 质量（1-100） | 85 |
| `--spacing` | `-s` | 页面间距（像素） | 0 |
| `--fixed-width` | - | 使用固定宽度 | False |
| `--no-crop` | - | 禁用自动裁剪 | False |
| `--crop-margin` | - | 裁剪边距（像素） | 10 |
| `--quiet` | - | 静默模式（不显示进度） | False |
| `--help` | `-h` | 显示帮助信息 | - |

## 退出码

### 单文件转换

- `0`: 成功
- `1`: 文件验证错误
- `2`: 渲染错误
- `3`: 图像拼接错误
- `4`: 输出错误
- `130`: 用户取消
- `255`: 未知错误

### 批量转换

- `0`: 全部成功
- `1`: 没有文件被处理
- `2`: 部分文件失败
- `130`: 用户取消
- `255`: 未知错误

## 开发

### 运行测试

```bash
python -m unittest discover tests
```

### 运行特定测试

```bash
python -m unittest tests.test_validator
python -m unittest tests.test_renderer
python -m unittest tests.test_compositor
python -m unittest tests.test_output
python -m unittest tests.test_integration
```

## 项目结构

```
pdf-to-long-screenshot/
├── src/
│   ├── __init__.py
│   ├── cli.py              # 命令行接口
│   ├── validator.py        # PDF 验证
│   ├── renderer.py         # PDF 渲染
│   ├── compositor.py       # 图像拼接
│   ├── output.py           # 输出生成
│   ├── progress.py         # 进度报告
│   ├── config.py           # 配置管理
│   └── exceptions.py       # 异常定义
├── tests/
│   ├── test_validator.py
│   ├── test_renderer.py
│   ├── test_compositor.py
│   ├── test_output.py
│   └── test_integration.py
├── requirements.txt
├── setup.py
└── README.md
```

## 技术栈

- **pdf2image**: PDF 页面渲染（基于 poppler）
- **Pillow**: 图像处理和拼接
- **argparse**: 命令行参数解析

## 限制

- 最大支持 100MB 的 PDF 文件
- DPI 范围限制在 72-300 之间
- 大文件可能需要较多内存

## 故障排除

### 错误：poppler 未安装

如果遇到 `poppler not found` 错误，请确保已安装 poppler 并添加到系统 PATH。

### 内存不足

对于大型 PDF 文件，可以尝试：
- 降低 DPI 值
- 分批处理页面
- 增加系统可用内存

### PDF 无法读取

确保 PDF 文件：
- 未加密或受密码保护
- 未损坏
- 格式正确

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
