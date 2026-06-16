# MindMap Print Splitter (思维导图拼接打印切分工具)

[English](#english) | [中文](#chinese)

---

<a name="chinese"></a>
## 中文介绍

### 💡 痛点解决 (针对 XMind 等长思维导图)
在使用 XMind、GitMind 等脑图工具导出思维导图时，经常会遇到导图过长（高度极大）或过宽的问题。
- **直接单页打印**：字体会被缩放到纳米级，完全无法阅读。
- **驱动多页平铺**：打印驱动会在纸张边界硬生生地截断文字，把字劈成两半，极其尴尬。
- **本工具解决方案**：本工具允许您在原始高清大图上叠加物理纸张（如 A4、A3）的实际大小框，在可视化界面中**自由上下拖动调整每张纸的印刷位置**。通过拉伸或重叠，您可以完美避开文字和节点，让切分线精确地落在空白处！最终一键导出页边距、居中对齐均符合标准的 Multi-page 高清 PDF 文件，无缝进行纸面拼接。

### ✨ 主要功能
1. **多格式高清导入**：支持导入 PNG、JPG 图像，或直接导入 PDF 文档（自动进行 300 DPI 高清解析）。
2. **多语言一键切换**：支持在上方的 `Settings` -> `Language` 菜单中即时切换 **中文、英文、日语、法语、俄语、阿拉伯语**。
3. **纸张与边距自由设定**：
   - 纸张大小：A4、A3 规格。
   - 纸张方向：纵向（Portrait）、横向（Landscape）。
   - 页边距：自定义上下左右边距（毫米 mm）。
   - 居中对齐：水平居中、垂直居中可选。
4. **两种排版模式**：
   - **Mode A**：单页比例缩放预览。
   - **Mode B (默认)**：多页分割拼接模式，可在画布中拖拽纸张，支持 **X 轴锁定/Y 轴锁定**，确保多页纸纵向或横向对齐不漂移。
5. **高性能无卡顿**：预览图缓存机制，拖动参数滑块瞬间更新。
6. **无损导出**：提取原图对应的高清像素，渲染至物理白底页边距画板，生成标准 300 DPI multi-page PDF。

### 🚀 运行与启动
确保您的系统已安装 Python 3.10+，然后安装依赖：
```bash
pip install -r requirements.txt
```
运行程序：
```bash
python image_pdf_printer/main.py
```

---

<a name="english"></a>
## English Description

### 💡 Pain Point Solved (Designed for XMind Mind Maps)
When exporting giant mind maps or flowcharts from tools like XMind or GitMind, users face a common dilemma:
- **Print on a single page**: The fonts shrink to an unreadable nanometer size.
- **Default multi-page tiling**: The print driver cuts right through characters and nodes at the page boundaries, leaving letters sliced in half.
- **Our Solution**: This tool overlays actual paper boundary boxes (A4/A3) directly on top of the original high-definition mind map. Users can pan, zoom, and **drag the paper rectangles vertically or horizontally** to ensure page breaks land cleanly in the white space between lines of text! Click confirm, and it compiles a pixel-perfect multi-page PDF with standard margins and centering.

### ✨ Core Features
1. **High-Definition Import**: Supports PNG, JPG, and single-page/multi-page PDF documents (renders PDF pages at 300 DPI).
2. **Multi-Language Support**: Instantly toggle between **Chinese, English, Japanese, French, Russian, and Arabic** from `Settings` -> `Language`.
3. **Print Layout Configuration**:
   - Paper Size: A4, A3.
   - Orientation: Portrait, Landscape.
   - Margins: Left, Right, Top, Bottom customizable in millimeters (mm).
   - Centering: Optional Horizontal and Vertical centering inside the printable area.
4. **Dual Layout Modes**:
   - **Mode A**: Standard single-page preview with percentage scaling.
   - **Mode B (Default)**: Tiled grid layout ($X \times Y$ pages) with draggable page rectangles. Alignment locks (Lock X or Lock Y) prevent grids from drifting sideways.
5. **Performance Optimized**: Cached `QPixmap` rendering ensures that sidebar sliders and spinboxes update the preview instantly without any lag.
6. **Lossless PDF Export**: Crops the high-resolution source and renders sections onto physical-dimensioned canvases at 300 DPI.

### 🚀 Getting Started
Ensure Python 3.10+ is installed, then install requirements:
```bash
pip install -r requirements.txt
```
Run the application:
```bash
python image_pdf_printer/main.py
```
