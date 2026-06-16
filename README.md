# MindMap Print Splitter (思维导图拼接打印切分工具)

[English](#english) | [中文](#chinese)

---

<a name="chinese"></a>
## 中文介绍

### 💡 痛点解决 (针对 XMind 等长思维导图)
在使用 XMind、GitMind 等脑图工具导出思维导图时，经常会遇到导图过长（高度极大）或过宽的问题。
- **直接单页打印**：字体会被缩放到纳米级，完全无法阅读。
- **驱动多页平铺**：打印驱动会在纸张边界硬生生地截断文字，把字劈成两半，极其尴尬。
- **本工具解决方案**：本工具允许您在原始高清大图上叠加物理纸张（如 A4、A3、自定义尺寸）的实际大小框，在可视化界面中**自由上下拖动调整每张纸的印刷位置**。通过拉伸或重叠，您可以完美避开文字和节点，让切分线精确地落在空白处！最终一键导出页边距、居中对齐均符合标准的 Multi-page 高清 PDF 文件，无缝进行纸面拼接。

### ✨ 主要功能
1. **多格式高清导入**：支持导入 PNG、JPG 图像，或直接导入 PDF 文档（自动进行 300 DPI 高清解析）。
2. **多语言一键切换**：支持在上方的 `Settings` -> `Language` 菜单中即时切换 **中文、英文、日语、法语、俄语、阿拉伯语**。
3. **纸张与边距自由设定**：
   - 纸张大小：A4、A3 规格，支持**自定义长宽物理尺寸**（毫米 mm）。
   - 纸张方向：纵向（Portrait）、横向（Landscape）。
   - 页边距：自定义上下左右边距（毫米 mm）。
   - 居中对齐：水平居中、垂直居中可选。
4. **边缘物理重叠度（Overlap）**：支持 0-50mm 可调重叠区域，打印后方便重合粘接，不丢失接缝信息。
5. **接缝文字智能避让（自动切分）**：使用图像行能量差算法，智能检测文字空隙，一键自动优化横向页缝位置，避免文字被斩断。
6. **矢量 PDF 无损裁剪**：若导入文件为 PDF，导出时将自动启用 **PDF 矢量无损裁剪引擎**，重塑坐标系并重新拼合，不损失任何分辨率或矢量排版信息。
7. **五套精美主题与自定义 CSS**：预设 Modern Dark（现代暗黑）、Classic Light（经典明亮）、Nordic Blue（北欧极地蓝）、Forest Green（森林绿意）、Matrix Amber（黑客帝国）五套精美主题，并支持直接编写 CSS/QSS 样式定制软件面板界面。
8. **高性能预览**：QPixmap 缓存机制，拖动参数滑块或调整网格瞬间更新，毫无阻碍。

### 🛠️ 后续维护与未来规划 (Roadmap)
以下功能已作为未来版本迭代的候选特性写入维护板块，敬请期待：
1. **多列流式排版网格 (Multi-column Flow Layout)**：针对宽度极大的横向思维导图，提供 Z 字形自动流式分页裁剪并拼合装订的方案。
2. **可视化交互接缝线拖拽**：在画布上直接通过鼠标悬停 and 拖拽虚线来微调局部接缝边界，而不需要拖拽整张纸。
3. **自定义纸张模版管理**：支持将常用的自定义长宽与边距参数保存为快捷模版，方便下次直接套用。

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
- **Our Solution**: This tool overlays actual paper boundary boxes (A4/A3/Custom paper sizes) directly on top of the original high-definition mind map. Users can pan, zoom, and **drag the paper rectangles vertically or horizontally** to ensure page breaks land cleanly in the white space between lines of text! Click confirm, and it compiles a pixel-perfect multi-page PDF with standard margins and centering.

### ✨ Core Features
1. **High-Definition Import**: Supports PNG, JPG, and single-page/multi-page PDF documents (renders PDF pages at 300 DPI).
2. **Multi-Language Support**: Instantly toggle between **Chinese, English, Japanese, French, Russian, and Arabic** from `Settings` -> `Language`.
3. **Print Layout Configuration**:
   - Paper Size: A4, A3, and **Custom Width/Height** (in mm).
   - Orientation: Portrait, Landscape.
   - Margins: Left, Right, Top, Bottom customizable in millimeters (mm).
   - Centering: Optional Horizontal and Vertical centering inside the printable area.
4. **Adjustable Overlap Margin**: Set 0–50mm vertical and horizontal physical page overlap to assist physical page stitching.
5. **Smart Seam Optimization (Text Avoidance)**: Applies an image energy profile algorithm to detect text rows, automatically shifting page breaks to clean white space gaps.
6. **Lossless Vector PDF Export**: When slicing source PDF files, the tool employs a **lossless vector transform engine** using `pypdf`, preserving all original vector paths, text objects, and infinite resolutions.
7. **5 Elegant Preset Themes & Custom CSS**: Features Modern Dark, Classic Light, Nordic Blue, Forest Green, and Matrix Amber styles, complete with a built-in QSS editor dialog for custom stylesheet overrides.
8. **Performance Optimized**: Cached `QPixmap` rendering ensures that sidebar sliders and spinboxes update the preview instantly without any lag.

### 🛠️ Future Roadmap & Maintenance
The following features are documented in the maintenance block for future iterations:
1. **Multi-column Flow Layout wrapping**: Support split grid wrapping for extremely wide mind maps in a Z-pattern, managing physical seam offsets automatically.
2. **Interactive Seam Line Dragging**: Introduce visual dashed seam lines that can be directly dragged on the canvas to fine-tune individual tile borders instead of moving entire page items.
3. **Custom Paper Profile Templates**: Save and load custom sizes and layouts as reusable presets.

### 🚀 Getting Started
Ensure Python 3.10+ is installed, then install requirements:
```bash
pip install -r requirements.txt
```
Run the application:
```bash
python image_pdf_printer/main.py
```
