# 批量转换使用指南

## 快速开始

### 1. 准备 PDF 文件

将需要转换的 PDF 文件放入 `pdfs/` 目录：

```bash
mkdir pdfs
cp your_files/*.pdf pdfs/
```

### 2. 运行批量转换

```bash
python batch_convert.py
```

### 3. 查看结果

转换后的图片保存在 `images/` 目录中，保持与输入相同的目录结构。

## 使用场景

### 场景 1：转换单个目录的所有 PDF

```bash
# 输入：pdfs/ 目录
# 输出：images/ 目录
python batch_convert.py
```

### 场景 2：自定义输入输出目录

```bash
python batch_convert.py -i my_documents -o converted_images
```

### 场景 3：递归转换包含子目录的 PDF

```bash
# 目录结构：
# pdfs/
#   ├── 2024/
#   │   ├── jan.pdf
#   │   └── feb.pdf
#   └── 2025/
#       └── mar.pdf

python batch_convert.py

# 输出结构：
# images/
#   ├── 2024/
#   │   ├── jan_long_screenshot.png
#   │   └── feb_long_screenshot.png
#   └── 2025/
#       └── mar_long_screenshot.png
```

### 场景 4：仅转换顶层目录（不递归）

```bash
python batch_convert.py --no-recursive
```

### 场景 5：增量转换（跳过已存在的文件）

```bash
# 第一次运行：转换所有文件
python batch_convert.py

# 添加新的 PDF 文件
cp new_file.pdf pdfs/

# 第二次运行：只转换新文件
python batch_convert.py --skip-existing
```

### 场景 6：批量转换为 JPEG 格式（节省空间）

```bash
python batch_convert.py -f jpeg -q 85
```

### 场景 7：高质量转换

```bash
python batch_convert.py --dpi 200 -f png
```

### 场景 8：静默模式（用于脚本）

```bash
python batch_convert.py --quiet
```

## 高级用法

### 组合多个选项

```bash
# 高质量 JPEG 转换，跳过已存在文件
python batch_convert.py \
  -i documents \
  -o screenshots \
  -f jpeg \
  -q 95 \
  --dpi 200 \
  --skip-existing
```

### 禁用自动裁剪（保留原始页面尺寸）

```bash
python batch_convert.py --no-crop
```

### 添加页面间距

```bash
python batch_convert.py --spacing 20
```

### 自定义裁剪边距

```bash
python batch_convert.py --crop-margin 30
```

## 性能提示

1. **大量文件处理**：使用 `--quiet` 减少输出，提高性能
2. **节省磁盘空间**：使用 JPEG 格式和适当的质量设置
3. **增量更新**：使用 `--skip-existing` 避免重复转换
4. **调整 DPI**：根据需求平衡质量和文件大小

## 常见问题

### Q: 如何查看转换进度？

A: 默认会显示详细进度。使用 `--quiet` 可以只显示摘要。

### Q: 转换失败的文件会怎样？

A: 失败的文件会显示错误信息，但不会中断整个批处理过程。最后会显示成功和失败的统计。

### Q: 如何保持原始目录结构？

A: 默认就会保持目录结构。输出目录会镜像输入目录的结构。

### Q: 可以转换网络驱动器上的文件吗？

A: 可以，只要路径可访问即可：
```bash
python batch_convert.py -i /mnt/network/pdfs -o /mnt/network/images
```

### Q: 如何处理大量文件？

A: 建议分批处理，或使用 `--quiet` 模式减少输出：
```bash
python batch_convert.py --quiet > conversion.log 2>&1
```

## 退出码

- `0`: 全部成功
- `1`: 没有文件被处理或输入目录不存在
- `2`: 部分文件转换失败
- `130`: 用户中断（Ctrl+C）
- `255`: 未知错误

## 示例脚本

### 自动化转换脚本

```bash
#!/bin/bash
# auto_convert.sh

# 设置目录
INPUT_DIR="pdfs"
OUTPUT_DIR="images"

# 检查输入目录
if [ ! -d "$INPUT_DIR" ]; then
    echo "错误：输入目录不存在"
    exit 1
fi

# 运行转换
echo "开始批量转换..."
python batch_convert.py \
    -i "$INPUT_DIR" \
    -o "$OUTPUT_DIR" \
    --skip-existing \
    --quiet

# 检查结果
if [ $? -eq 0 ]; then
    echo "转换完成！"
    echo "输出目录：$OUTPUT_DIR"
else
    echo "转换过程中出现错误"
    exit 1
fi
```

### 定时任务示例

```bash
# 添加到 crontab，每天凌晨 2 点自动转换
0 2 * * * cd /path/to/project && python batch_convert.py --skip-existing --quiet
```
