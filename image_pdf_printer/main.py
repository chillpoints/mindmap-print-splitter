import os
import sys
from io import BytesIO
from PIL import Image, JpegImagePlugin, PdfImagePlugin

from PySide6.QtCore import Qt, QSize, QSizeF, QPointF, QRectF
from PySide6.QtGui import QPixmap, QImage, QPainter, QColor, QPen, QBrush, QFont, QIcon, QTransform
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QCheckBox, QDoubleSpinBox, QSpinBox,
    QLabel, QFileDialog, QGroupBox, QRadioButton, QSlider,
    QGraphicsScene, QMessageBox, QSplitter, QStatusBar, QFrame,
    QGraphicsPixmapItem, QGraphicsRectItem, QDialog, QTextEdit,
    QDialogButtonBox
)
from PySide6.QtPdf import QPdfDocument

# Import our custom canvas items
from canvas import DraggablePageItem, InteractiveGraphicsView

# Six-language translations dictionary
TRANSLATIONS = {
    "zh": {
        "menu_settings": "设置",
        "menu_language": "语言",
        "menu_theme": "主题",
        "file_group_title": "导入文件",
        "import_btn": "导入图片 / PDF",
        "no_file": "未加载文件。\n(支持 png, jpg, pdf)",
        "file_info_img": "文件: {name}\n大小: {w} x {h} px",
        "file_info_pdf": "PDF: {name}\n页数: {page_idx} / {total}\n渲染大小: {w} x {h} px (300 DPI)",
        "select_page": "选择页面:",
        "paper_group_title": "纸张与页边距",
        "lbl_paper": "纸张大小:",
        "lbl_orient": "方向:",
        "orient_portrait": "纵向",
        "orient_landscape": "横向",
        "chk_center_h": "水平居中",
        "chk_center_v": "垂直居中",
        "lbl_margin_top": "上边距 (mm):",
        "lbl_margin_bottom": "下边距 (mm):",
        "lbl_margin_left": "左边距 (mm):",
        "lbl_margin_right": "右边距 (mm):",
        "lbl_overlap": "重叠边距 (mm):",
        "custom_w_label": "自定义宽 (mm):",
        "custom_h_label": "自定义高 (mm):",
        "layout_group_title": "排版与缩放方式",
        "radio_mode_a": "模式 A: 按比例缩放单页",
        "radio_mode_b": "模式 B: 多页分割拼接 (默认)",
        "lbl_scale_factor": "缩放比例:",
        "lbl_cols": "列数 (X):",
        "lbl_rows": "行数 (Y):",
        "lock_x": "锁定 X 轴对齐",
        "lock_y": "锁定 Y 轴对齐",
        "lbl_page_scale": "纸张尺寸比例: {val}%",
        "autofit_btn": "自动缩放铺满图像",
        "optimize_btn": "智能避让文字接缝",
        "action_group_title": "操作",
        "btn_reset": "重置纸张网格布局",
        "btn_export": "导出 PDF",
        "view_title_a": "打印预览 - 单页比例缩放",
        "view_title_b": "交互式分割拼接编辑器 (多页模式)",
        "status_ready": "准备就绪。导入一个图片或 PDF 文件开始。",
        "status_loading": "正在加载 {name}...",
        "status_loaded": "成功加载 {name}。",
        "status_error_loading": "加载文件时出错。",
        "status_dragging": "拖动第 {num} 页: 内容区域 X={x1}-{x2}, Y={y1}-{y2} px",
        "status_reset": "纸张网格布局已重置为默认位置。",
        "status_exporting": "正在导出至 {name}...",
        "status_exported": "成功导出 PDF 至 {name}",
        "status_export_failed": "导出 PDF 失败。",
        "status_optimized": "接缝自动避让文字优化已完成。",
        "msg_export_success": "成功生成了 {pages} 页 of PDF 文件：\n{path}",
        "msg_error_title": "错误",
        "msg_success_title": "导出成功",
        "msg_load_error_title": "文件加载错误",
        "msg_no_pages_defined": "未定义分割网格的页面。",
        "msg_export_failed_title": "导出失败",
        "fit_all": "适应全部",
        "fit_width": "适应宽度",
    },
    "en": {
        "menu_settings": "Settings",
        "menu_language": "Language",
        "menu_theme": "Theme",
        "file_group_title": "File Input",
        "import_btn": "Import Image / PDF",
        "no_file": "No file loaded.\n(Supports png, jpg, pdf)",
        "file_info_img": "File: {name}\nSize: {w} x {h} px",
        "file_info_pdf": "PDF: {name}\nPage: {page_idx} / {total}\nRendered: {w} x {h} px (300 DPI)",
        "select_page": "Select Page:",
        "paper_group_title": "Paper & Margins",
        "lbl_paper": "Paper Size:",
        "lbl_orient": "Orientation:",
        "orient_portrait": "Portrait",
        "orient_landscape": "Landscape",
        "chk_center_h": "Horizontal Center",
        "chk_center_v": "Vertical Center",
        "lbl_margin_top": "Top Margin (mm):",
        "lbl_margin_bottom": "Bottom Margin (mm):",
        "lbl_margin_left": "Left Margin (mm):",
        "lbl_margin_right": "Right Margin (mm):",
        "lbl_overlap": "Overlap Margin (mm):",
        "custom_w_label": "Custom Width (mm):",
        "custom_h_label": "Custom Height (mm):",
        "layout_group_title": "Layout & Scaling",
        "radio_mode_a": "Mode A: Scale to % (Single Page)",
        "radio_mode_b": "Mode B: Fit to X x Y Pages (Tiling)",
        "lbl_scale_factor": "Scale factor:",
        "lbl_cols": "Cols (X):",
        "lbl_rows": "Rows (Y):",
        "lock_x": "Lock X Alignment",
        "lock_y": "Lock Y Alignment",
        "lbl_page_scale": "Paper Size Scale: {val}%",
        "autofit_btn": "Auto-fit Scale to Cover Image",
        "optimize_btn": "Optimize Seams (Avoid Text Cut)",
        "action_group_title": "Actions",
        "btn_reset": "Reset Paper Grid Layout",
        "btn_export": "Generate PDF",
        "view_title_a": "Print Preview - Single Page Layout",
        "view_title_b": "Interactive View - Tile Splitting Editor",
        "status_ready": "Ready. Load an image or PDF to start.",
        "status_loading": "Loading {name}...",
        "status_loaded": "Loaded {name} successfully.",
        "status_error_loading": "Error loading file.",
        "status_dragging": "Dragging Page {num}: Content region X={x1}-{x2}, Y={y1}-{y2} px",
        "status_reset": "Page grid layout has been reset to default.",
        "status_exporting": "Exporting to {name}...",
        "status_exported": "Exported successfully to {name}",
        "status_export_failed": "Export failed.",
        "status_optimized": "Seams optimized to avoid text cutting.",
        "msg_export_success": "Successfully generated PDF file with {pages} pages:\n{path}",
        "msg_error_title": "Error",
        "msg_success_title": "Export Successful",
        "msg_load_error_title": "File Load Error",
        "msg_no_pages_defined": "No pages defined for tiling layout.",
        "msg_export_failed_title": "Export Failed",
        "fit_all": "Fit All",
        "fit_width": "Fit Width",
    },
    "ja": {
        "menu_settings": "設定",
        "menu_language": "言語",
        "menu_theme": "テーマ",
        "file_group_title": "ファイルのインポート",
        "import_btn": "画像 / PDFを読み込む",
        "no_file": "ファイルが読み込まれていません。\n(png, jpg, pdf 対応)",
        "file_info_img": "ファイル: {name}\nサイズ: {w} x {h} px",
        "file_info_pdf": "PDF: {name}\nページ: {page_idx} / {total}\nレンダリング: {w} x {h} px (300 DPI)",
        "select_page": "ページ選択:",
        "paper_group_title": "用紙と余白",
        "lbl_paper": "用紙サイズ:",
        "lbl_orient": "方向:",
        "orient_portrait": "縦方向",
        "orient_landscape": "横方向",
        "chk_center_h": "水平中央揃え",
        "chk_center_v": "垂直中央揃え",
        "lbl_margin_top": "上余白 (mm):",
        "lbl_margin_bottom": "下余白 (mm):",
        "lbl_margin_left": "左余白 (mm):",
        "lbl_margin_right": "右余白 (mm):",
        "lbl_overlap": "重なり余白 (mm):",
        "custom_w_label": "カスタム幅 (mm):",
        "custom_h_label": "カスタム高 (mm):",
        "layout_group_title": "レイアウトと縮放",
        "radio_mode_a": "モード A: 倍率指定（単一ページ）",
        "radio_mode_b": "モード B: 複数ページ分割表示",
        "lbl_scale_factor": "倍率:",
        "lbl_cols": "列数 (X):",
        "lbl_rows": "行数 (Y):",
        "lock_x": "X軸 of 配置をロック",
        "lock_y": "Y軸 of 配置をロック",
        "lbl_page_scale": "用紙サイズ比率: {val}%",
        "autofit_btn": "自動調整して画像全体を覆う",
        "optimize_btn": "文字切れ目の自動回避",
        "action_group_title": "操作",
        "btn_reset": "グリッド配置をリセット",
        "btn_export": "PDFを出力",
        "view_title_a": "印刷プレビュー - 单一ページ表示",
        "view_title_b": "インタラクティブ分割編集画面",
        "status_ready": "準備完了。画像またはPDFをインポートしてください。",
        "status_loading": "{name} を読み込み中...",
        "status_loaded": "{name} が正常に読み込まれました。",
        "status_error_loading": "ファイルの読み込みエラー。",
        "status_dragging": "ページ {num} 移動中: 範囲 X={x1}-{x2}, Y={y1}-{y2} px",
        "status_reset": "グリッドレイアウトが初期位置にリセットされました。",
        "status_exporting": "{name} にエクスポート中...",
        "status_exported": "{name} にエクスポートされました。",
        "status_export_failed": "エクスポート失敗。",
        "status_optimized": "文字切れ目の自動回避を適用しました。",
        "msg_export_success": "{pages} ページのPDFファイルが正常に生成されました:\n{path}",
        "msg_error_title": "エラー",
        "msg_success_title": "エクスポート成功",
        "msg_load_error_title": "ファイル読み込みエラー",
        "msg_no_pages_defined": "分割表示用のページが定義されていません。",
        "msg_export_failed_title": "エクスポート失敗",
        "fit_all": "全体表示",
        "fit_width": "幅に合わせる",
    },
    "fr": {
        "menu_settings": "Paramètres",
        "menu_language": "Langue",
        "menu_theme": "Thème",
        "file_group_title": "Fichier d'entrée",
        "import_btn": "Importer Image / PDF",
        "no_file": "Aucun fichier chargé.\n(Formats png, jpg, pdf)",
        "file_info_img": "Fichier: {name}\nTaille: {w} x {h} px",
        "file_info_pdf": "PDF: {name}\nPage: {page_idx} / {total}\nRendu: {w} x {h} px (300 DPI)",
        "select_page": "Sélectionner Page:",
        "paper_group_title": "Papier & Marges",
        "lbl_paper": "Taille du papier:",
        "lbl_orient": "Orientation:",
        "orient_portrait": "Portrait",
        "orient_landscape": "Paysage",
        "chk_center_h": "Centrer Horizontalement",
        "chk_center_v": "Centrer Verticalement",
        "lbl_margin_top": "Marge Supérieure (mm):",
        "lbl_margin_bottom": "Marge Inférieure (mm):",
        "lbl_margin_left": "Marge Gauche (mm):",
        "lbl_margin_right": "Marge Droite (mm):",
        "lbl_overlap": "Marge de superposition (mm):",
        "custom_w_label": "Largeur Personnalisée (mm):",
        "custom_h_label": "Hauteur Personnalisée (mm):",
        "layout_group_title": "Mise en page & Échelle",
        "radio_mode_a": "Mode A: Échelle en % (Page Unique)",
        "radio_mode_b": "Mode B: Ajuster sur X x Y Pages (Tuiles)",
        "lbl_scale_factor": "Facteur d'échelle:",
        "lbl_cols": "Colonnes (X):",
        "lbl_rows": "Lignes (Y):",
        "lock_x": "Verrouiller Alignement X",
        "lock_y": "Verrouiller Alignement Y",
        "lbl_page_scale": "Échelle du Papier: {val}%",
        "autofit_btn": "Ajustement Auto pour couvrir l'image",
        "optimize_btn": "Optimiser les coutures",
        "action_group_title": "Actions",
        "btn_reset": "Réinitialiser la grille",
        "btn_export": "Générer PDF",
        "view_title_a": "Aperçu avant impression - Page Unique",
        "view_title_b": "Éditeur de division de tuiles interactif",
        "status_ready": "Prêt. Chargez une image ou un PDF.",
        "status_loading": "Chargement de {name}...",
        "status_loaded": "Chargé {name} avec succès.",
        "status_error_loading": "Erreur lors du chargement.",
        "status_dragging": "Déplacement Page {num}: Zone X={x1}-{x2}, Y={y1}-{y2} px",
        "status_reset": "La grille a été réinitialisée.",
        "status_exporting": "Exportation vers {name}...",
        "status_exported": "Exporté avec succès vers {name}",
        "status_export_failed": "L'exportation a échoué.",
        "status_optimized": "Coutures optimisées pour éviter de couper le texte.",
        "msg_export_success": "Fichier PDF généré avec succès ({pages} pages) :\n{path}",
        "msg_error_title": "Erreur",
        "msg_success_title": "Exportation Réussie",
        "msg_load_error_title": "Erreur de chargement",
        "msg_no_pages_defined": "Aucune page définie pour l'exportation.",
        "msg_export_failed_title": "Échec de l'exportation",
        "fit_all": "Ajuster Tout",
        "fit_width": "Ajuster Largeur",
    },
    "ru": {
        "menu_settings": "Настройки",
        "menu_language": "Язык",
        "menu_theme": "Тема",
        "file_group_title": "Импорт файла",
        "import_btn": "Импорт Изображения / PDF",
        "no_file": "Файл не загружен.\n(Поддерживаются png, jpg, pdf)",
        "file_info_img": "Файл: {name}\nРазмер: {w} x {h} px",
        "file_info_pdf": "PDF: {name}\nСтраница: {page_idx} / {total}\nРендер: {w} x {h} px (300 DPI)",
        "select_page": "Выбор Страницы:",
        "paper_group_title": "Бумага и поля",
        "lbl_paper": "Размер бумаги:",
        "lbl_orient": "Ориентация:",
        "orient_portrait": "Книжная",
        "orient_landscape": "Альбомная",
        "chk_center_h": "По Горизонтали",
        "chk_center_v": "По Вертикали",
        "lbl_margin_top": "Верхнее Поле (мм):",
        "lbl_margin_bottom": "Нижнее Поле (мм):",
        "lbl_margin_left": "Левое Поле (мм):",
        "lbl_margin_right": "Правое Поле (мм):",
        "lbl_overlap": "Перекрытие (мм):",
        "custom_w_label": "Ширина (мм):",
        "custom_h_label": "Высота (мм):",
        "layout_group_title": "Макет и Масштаб",
        "radio_mode_a": "Режим А: Масштаб в % (Одна страница)",
        "radio_mode_b": "Режим B: Разбить на X x Y страниц",
        "lbl_scale_factor": "Масштаб:",
        "lbl_cols": "Колонки (X):",
        "lbl_rows": "Строки (Y):",
        "lock_x": "Блокировать Выравнивание X",
        "lock_y": "Блокировать Выравнивание Y",
        "lbl_page_scale": "Масштаб Бумаги: {val}%",
        "autofit_btn": "Автоподбор под размер изображения",
        "optimize_btn": "Оптимизировать швы",
        "action_group_title": "Действия",
        "btn_reset": "Сбросить Сетку Страниц",
        "btn_export": "Создать PDF",
        "view_title_a": "Предпросмотр - Одностраничный макет",
        "view_title_b": "Интерактивный редактор разбивки страниц",
        "status_ready": "Готово. Загрузите изображение или PDF.",
        "status_loading": "Загрузка {name}...",
        "status_loaded": "Успешно загружен {name}.",
        "status_error_loading": "Ошибка загрузки файла.",
        "status_dragging": "Перемещение Страницы {num}: Область X={x1}-{x2}, Y={y1}-{y2} px",
        "status_reset": "Сетка страниц сброшена по умолчанию.",
        "status_exporting": "Экспорт в {name}...",
        "status_exported": "Успешный экспорт в {name}",
        "status_export_failed": "Ошибка экспорта.",
        "status_optimized": "Швы оптимизированы для избежания разрезания текста.",
        "msg_export_success": "Успешно создан PDF-файл из {pages} страниц:\n{path}",
        "msg_error_title": "Ошибка",
        "msg_success_title": "Экспорт Выполнен",
        "msg_load_error_title": "Ошибка загрузки файла",
        "msg_no_pages_defined": "Страницы для сетки не заданы.",
        "msg_export_failed_title": "Ошибка экспорта",
        "fit_all": "Показать все",
        "fit_width": "По ширине",
    },
    "ar": {
        "menu_settings": "الإعدادات",
        "menu_language": "اللغة",
        "menu_theme": "السمة",
        "file_group_title": "إدخال الملف",
        "import_btn": "استيراد صورة / PDF",
        "no_file": "لم يتم تحميل ملف.\n(يدعم png, jpg, pdf)",
        "file_info_img": "الملف: {name}\nالحجم: {w} x {h} بكسل",
        "file_info_pdf": "PDF: {name}\nالصفحة: {page_idx} / {total}\nالرندر: {w} x {h} بكسل (300 DPI)",
        "select_page": "اختر الصفحة:",
        "paper_group_title": "الورقة والهوامش",
        "lbl_paper": "حجم الورق:",
        "lbl_orient": "الاتجاه:",
        "orient_portrait": "عمودي",
        "orient_landscape": "أفقي",
        "chk_center_h": "توسط أفقي",
        "chk_center_v": "توسط عمودي",
        "lbl_margin_top": "الهامش العلوي (مم):",
        "lbl_margin_bottom": "الهامش السفلي (مم):",
        "lbl_margin_left": "الهامش الأيسر (مم):",
        "lbl_margin_right": "الهامش الأيمن (مم):",
        "lbl_overlap": "هامش التداخل (مم):",
        "custom_w_label": "عرض مخصص (مم):",
        "custom_h_label": "ارتفاع مخصص (مم):",
        "layout_group_title": "التنسيق وتغيير الحجم",
        "radio_mode_a": "الوضع A: تغيير الحجم كنسبة مئوية",
        "radio_mode_b": "الوضع B: تقسيم على X x Y صفحات",
        "lbl_scale_factor": "نسبة الحجم:",
        "lbl_cols": "الأعمدة (X):",
        "lbl_rows": "الصفوف (Y):",
        "lock_x": "قفل محاذاة X",
        "lock_y": "قفل محاذاة Y",
        "lbl_page_scale": "نسبة حجم الورقة: {val}%",
        "autofit_btn": "ملاءمة تلقائية لتغطية الصورة",
        "optimize_btn": "تحسين الفواصل (تجنب القطع)",
        "action_group_title": "الإجراءات",
        "btn_reset": "إعادة تعيين تخطيط الشبكة",
        "btn_export": "تصدير PDF",
        "view_title_a": "معاينة الطباعة - صفحة واحدة",
        "view_title_b": "محرر تقسيم الصفحات التفاعلي",
        "status_ready": "جاهز. يرجى تحميل صورة أو ملف PDF.",
        "status_loading": "جاري تحميل {name}...",
        "status_loaded": "تم تحميل {name} بنجاح.",
        "status_error_loading": "خطأ في تحميل الملف.",
        "status_dragging": "سحب الصفحة {num}: منطقة المحتوى X={x1}-{x2}, Y={y1}-{y2} بكسل",
        "status_reset": "تم إعادة تعيين تخطيط الشبكة الافتراضي.",
        "status_exporting": "جاري التصدير إلى {name}...",
        "status_exported": "تم التصدير بنجاح إلى {name}",
        "status_export_failed": "فشل التصدير.",
        "status_optimized": "تم تحسين الفواصل لتجنب قطع النص.",
        "msg_export_success": "تم إنشاء ملف PDF بنجاح بعدد صفحات {pages}:\n{path}",
        "msg_error_title": "خطأ",
        "msg_success_title": "تم التصدير بنجاح",
        "msg_load_error_title": "خطأ في تحميل الملف",
        "msg_no_pages_defined": "لم يتم تحديد أي صفحات للشبكة.",
        "msg_export_failed_title": "فشل التصدير",
        "fit_all": "ملاءمة الكل",
        "fit_width": "ملاءمة العرض",
    }
}

PRESET_PAPERS = [
    ("A0", 841, 1189),
    ("A1", 594, 841),
    ("A2", 420, 594),
    ("A3", 297, 420),
    ("A4", 210, 297),
    ("A5", 148, 210),
    ("B3", 353, 500),
    ("B4", 250, 353),
    ("B5", 176, 250),
]

# Stylesheet presets (5 themes)
THEMES = {
    "dark": """
        QMainWindow { background-color: #121212; }
        QWidget { color: #e0e0e0; font-family: 'Segoe UI', 'Outfit', sans-serif; font-size: 13px; }
        QGroupBox { border: 1px solid #2d2d2d; border-radius: 8px; margin-top: 15px; padding-top: 15px; font-weight: bold; color: #ffffff; }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; padding: 0 5px; }
        QPushButton { background-color: #007aff; color: white; border: none; border-radius: 5px; padding: 8px 15px; font-weight: bold; }
        QPushButton:hover { background-color: #0062cc; }
        QPushButton:pressed { background-color: #004ea6; }
        QPushButton#reset_btn { background-color: #2d2d2d; color: #e0e0e0; border: 1px solid #3c3c3c; }
        QPushButton#reset_btn:hover { background-color: #3d3d3d; }
        QPushButton#zoom_btn { background-color: #2d2d2d; color: #ffffff; border: 1px solid #3c3c3c; border-radius: 5px; font-weight: bold; }
        QPushButton#zoom_btn:hover { background-color: #3d3d3d; }
        QComboBox, QDoubleSpinBox, QSpinBox, QLineEdit { background-color: #1e1e1e; border: 1px solid #3c3c3c; border-radius: 5px; padding: 5px; color: #ffffff; }
        QComboBox::drop-down { border: none; }
        QSlider::groove:horizontal { border: 1px solid #3c3c3c; height: 6px; background: #1e1e1e; border-radius: 3px; }
        QSlider::handle:horizontal { background: #007aff; width: 14px; margin-top: -4px; margin-bottom: -4px; border-radius: 7px; }
        QSlider::handle:horizontal:hover { background: #0062cc; }
        QStatusBar { background-color: #1a1a1a; color: #888888; }
        
        /* Menu and Dialog Custom Styling */
        QMenuBar { background-color: #121212; color: #e0e0e0; border-bottom: 1px solid #2d2d2d; }
        QMenuBar::item { background: transparent; padding: 4px 10px; border-radius: 4px; }
        QMenuBar::item:selected { background-color: #2d2d2d; color: #ffffff; }
        QMenu { background-color: #1e1e1e; color: #e0e0e0; border: 1px solid #2d2d2d; border-radius: 6px; padding: 5px; }
        QMenu::item { padding: 6px 20px; border-radius: 4px; }
        QMenu::item:selected { background-color: #007aff; color: white; }
        QDialog { background-color: #121212; }
        QTextEdit { background-color: #1e1e1e; color: #ffffff; border: 1px solid #3c3c3c; border-radius: 5px; font-family: 'Consolas', 'Courier New', monospace; font-size: 13px; }
        
        /* Scrollbar Styling */
        QScrollBar:vertical { border: none; background: #121212; width: 10px; margin: 0px; }
        QScrollBar::handle:vertical { background: #2d2d2d; min-height: 20px; border-radius: 5px; }
        QScrollBar::handle:vertical:hover { background: #3d3d3d; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
        QScrollBar:horizontal { border: none; background: #121212; height: 10px; margin: 0px; }
        QScrollBar::handle:horizontal { background: #2d2d2d; min-width: 20px; border-radius: 5px; }
        QScrollBar::handle:horizontal:hover { background: #3d3d3d; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { border: none; background: none; }
    """,
    "light": """
        QMainWindow { background-color: #f5f5f7; }
        QWidget { color: #1d1d1f; font-family: 'Segoe UI', 'Outfit', sans-serif; font-size: 13px; }
        QGroupBox { border: 1px solid #d2d2d7; border-radius: 8px; margin-top: 15px; padding-top: 15px; font-weight: bold; color: #1d1d1f; }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; padding: 0 5px; }
        QPushButton { background-color: #007aff; color: white; border: none; border-radius: 5px; padding: 8px 15px; font-weight: bold; }
        QPushButton:hover { background-color: #0062cc; }
        QPushButton:pressed { background-color: #004ea6; }
        QPushButton#reset_btn { background-color: #e8e8ed; color: #1d1d1f; border: 1px solid #d2d2d7; }
        QPushButton#reset_btn:hover { background-color: #d2d2d7; }
        QPushButton#zoom_btn { background-color: #e8e8ed; color: #1d1d1f; border: 1px solid #d2d2d7; border-radius: 5px; font-weight: bold; }
        QPushButton#zoom_btn:hover { background-color: #d2d2d7; }
        QComboBox, QDoubleSpinBox, QSpinBox, QLineEdit { background-color: #ffffff; border: 1px solid #d2d2d7; border-radius: 5px; padding: 5px; color: #1d1d1f; }
        QComboBox::drop-down { border: none; }
        QSlider::groove:horizontal { border: 1px solid #d2d2d7; height: 6px; background: #e8e8ed; border-radius: 3px; }
        QSlider::handle:horizontal { background: #007aff; width: 14px; margin-top: -4px; margin-bottom: -4px; border-radius: 7px; }
        QSlider::handle:horizontal:hover { background: #0062cc; }
        QStatusBar { background-color: #e8e8ed; color: #86868b; }
        
        /* Menu and Dialog Custom Styling */
        QMenuBar { background-color: #f5f5f7; color: #1d1d1f; border-bottom: 1px solid #d2d2d7; }
        QMenuBar::item { background: transparent; padding: 4px 10px; border-radius: 4px; }
        QMenuBar::item:selected { background-color: #e8e8ed; color: #1d1d1f; }
        QMenu { background-color: #ffffff; color: #1d1d1f; border: 1px solid #d2d2d7; border-radius: 6px; padding: 5px; }
        QMenu::item { padding: 6px 20px; border-radius: 4px; }
        QMenu::item:selected { background-color: #007aff; color: white; }
        QDialog { background-color: #f5f5f7; }
        QTextEdit { background-color: #ffffff; color: #1d1d1f; border: 1px solid #d2d2d7; border-radius: 5px; font-family: 'Consolas', 'Courier New', monospace; font-size: 13px; }
        
        /* Scrollbar Styling */
        QScrollBar:vertical { border: none; background: #f5f5f7; width: 10px; margin: 0px; }
        QScrollBar::handle:vertical { background: #d2d2d7; min-height: 20px; border-radius: 5px; }
        QScrollBar::handle:vertical:hover { background: #b8b8bf; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
        QScrollBar:horizontal { border: none; background: #f5f5f7; height: 10px; margin: 0px; }
        QScrollBar::handle:horizontal { background: #d2d2d7; min-width: 20px; border-radius: 5px; }
        QScrollBar::handle:horizontal:hover { background: #b8b8bf; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { border: none; background: none; }
    """,
    "nordic": """
        QMainWindow { background-color: #0f172a; }
        QWidget { color: #f1f5f9; font-family: 'Segoe UI', 'Outfit', sans-serif; font-size: 13px; }
        QGroupBox { border: 1px solid #334155; border-radius: 8px; margin-top: 15px; padding-top: 15px; font-weight: bold; color: #f8fafc; }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; padding: 0 5px; }
        QPushButton { background-color: #38bdf8; color: #0f172a; border: none; border-radius: 5px; padding: 8px 15px; font-weight: bold; }
        QPushButton:hover { background-color: #0ea5e9; }
        QPushButton:pressed { background-color: #0284c7; }
        QPushButton#reset_btn { background-color: #1e293b; color: #f1f5f9; border: 1px solid #334155; }
        QPushButton#reset_btn:hover { background-color: #334155; }
        QPushButton#zoom_btn { background-color: #1e293b; color: #f1f5f9; border: 1px solid #334155; border-radius: 5px; font-weight: bold; }
        QPushButton#zoom_btn:hover { background-color: #334155; }
        QComboBox, QDoubleSpinBox, QSpinBox, QLineEdit { background-color: #1e293b; border: 1px solid #334155; border-radius: 5px; padding: 5px; color: #f1f5f9; }
        QComboBox::drop-down { border: none; }
        QSlider::groove:horizontal { border: 1px solid #334155; height: 6px; background: #1e293b; border-radius: 3px; }
        QSlider::handle:horizontal { background: #38bdf8; width: 14px; margin-top: -4px; margin-bottom: -4px; border-radius: 7px; }
        QSlider::handle:horizontal:hover { background: #0ea5e9; }
        QStatusBar { background-color: #1e293b; color: #94a3b8; }
        
        /* Menu and Dialog Custom Styling */
        QMenuBar { background-color: #0f172a; color: #f1f5f9; border-bottom: 1px solid #334155; }
        QMenuBar::item { background: transparent; padding: 4px 10px; border-radius: 4px; }
        QMenuBar::item:selected { background-color: #1e293b; color: #f8fafc; }
        QMenu { background-color: #1e293b; color: #f1f5f9; border: 1px solid #334155; border-radius: 6px; padding: 5px; }
        QMenu::item { padding: 6px 20px; border-radius: 4px; }
        QMenu::item:selected { background-color: #38bdf8; color: #0f172a; }
        QDialog { background-color: #0f172a; }
        QTextEdit { background-color: #1e293b; color: #f1f5f9; border: 1px solid #334155; border-radius: 5px; font-family: 'Consolas', 'Courier New', monospace; font-size: 13px; }
        
        /* Scrollbar Styling */
        QScrollBar:vertical { border: none; background: #0f172a; width: 10px; margin: 0px; }
        QScrollBar::handle:vertical { background: #1e293b; min-height: 20px; border-radius: 5px; }
        QScrollBar::handle:vertical:hover { background: #334155; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
        QScrollBar:horizontal { border: none; background: #0f172a; height: 10px; margin: 0px; }
        QScrollBar::handle:horizontal { background: #1e293b; min-width: 20px; border-radius: 5px; }
        QScrollBar::handle:horizontal:hover { background: #334155; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { border: none; background: none; }
    """,
    "forest": """
        QMainWindow { background-color: #141b1a; }
        QWidget { color: #e6f4f1; font-family: 'Segoe UI', 'Outfit', sans-serif; font-size: 13px; }
        QGroupBox { border: 1px solid #2d3d3a; border-radius: 8px; margin-top: 15px; padding-top: 15px; font-weight: bold; color: #ffffff; }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; padding: 0 5px; }
        QPushButton { background-color: #059669; color: white; border: none; border-radius: 5px; padding: 8px 15px; font-weight: bold; }
        QPushButton:hover { background-color: #047857; }
        QPushButton:pressed { background-color: #065f46; }
        QPushButton#reset_btn { background-color: #1c2826; color: #e6f4f1; border: 1px solid #2d3d3a; }
        QPushButton#reset_btn:hover { background-color: #2d3d3a; }
        QPushButton#zoom_btn { background-color: #1c2826; color: #e6f4f1; border: 1px solid #2d3d3a; border-radius: 5px; font-weight: bold; }
        QPushButton#zoom_btn:hover { background-color: #2d3d3a; }
        QComboBox, QDoubleSpinBox, QSpinBox, QLineEdit { background-color: #1c2826; border: 1px solid #2d3d3a; border-radius: 5px; padding: 5px; color: #ffffff; }
        QComboBox::drop-down { border: none; }
        QSlider::groove:horizontal { border: 1px solid #2d3d3a; height: 6px; background: #1c2826; border-radius: 3px; }
        QSlider::handle:horizontal { background: #059669; width: 14px; margin-top: -4px; margin-bottom: -4px; border-radius: 7px; }
        QSlider::handle:horizontal:hover { background: #047857; }
        QStatusBar { background-color: #1c2826; color: #809c96; }
        
        /* Menu and Dialog Custom Styling */
        QMenuBar { background-color: #141b1a; color: #e6f4f1; border-bottom: 1px solid #2d3d3a; }
        QMenuBar::item { background: transparent; padding: 4px 10px; border-radius: 4px; }
        QMenuBar::item:selected { background-color: #1c2826; color: #ffffff; }
        QMenu { background-color: #1c2826; color: #e6f4f1; border: 1px solid #2d3d3a; border-radius: 6px; padding: 5px; }
        QMenu::item { padding: 6px 20px; border-radius: 4px; }
        QMenu::item:selected { background-color: #059669; color: white; }
        QDialog { background-color: #141b1a; }
        QTextEdit { background-color: #1c2826; color: #ffffff; border: 1px solid #2d3d3a; border-radius: 5px; font-family: 'Consolas', 'Courier New', monospace; font-size: 13px; }
        
        /* Scrollbar Styling */
        QScrollBar:vertical { border: none; background: #141b1a; width: 10px; margin: 0px; }
        QScrollBar::handle:vertical { background: #1c2826; min-height: 20px; border-radius: 5px; }
        QScrollBar::handle:vertical:hover { background: #2d3d3a; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
        QScrollBar:horizontal { border: none; background: #141b1a; height: 10px; margin: 0px; }
        QScrollBar::handle:horizontal { background: #1c2826; min-width: 20px; border-radius: 5px; }
        QScrollBar::handle:horizontal:hover { background: #2d3d3a; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { border: none; background: none; }
    """,
    "matrix": """
        QMainWindow { background-color: #000000; }
        QWidget { color: #ffb000; font-family: 'Courier New', 'Consolas', monospace; font-size: 13px; }
        QGroupBox { border: 1px solid #ffb000; border-radius: 8px; margin-top: 15px; padding-top: 15px; font-weight: bold; color: #ffb000; }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; padding: 0 5px; }
        QPushButton { background-color: #ffb000; color: #000000; border: none; border-radius: 5px; padding: 8px 15px; font-weight: bold; }
        QPushButton:hover { background-color: #e09b00; }
        QPushButton:pressed { background-color: #c28600; }
        QPushButton#reset_btn { background-color: #000000; color: #ffb000; border: 1px solid #ffb000; }
        QPushButton#reset_btn:hover { background-color: #1a1a1a; }
        QPushButton#zoom_btn { background-color: #000000; color: #ffb000; border: 1px solid #ffb000; border-radius: 5px; font-weight: bold; }
        QPushButton#zoom_btn:hover { background-color: #1a1a1a; }
        QComboBox, QDoubleSpinBox, QSpinBox, QLineEdit { background-color: #000000; border: 1px solid #ffb000; border-radius: 5px; padding: 5px; color: #ffb000; }
        QComboBox::drop-down { border: none; }
        QSlider::groove:horizontal { border: 1px solid #ffb000; height: 6px; background: #000000; border-radius: 3px; }
        QSlider::handle:horizontal { background: #ffb000; width: 14px; margin-top: -4px; margin-bottom: -4px; border-radius: 7px; }
        QSlider::handle:horizontal:hover { background: #e09b00; }
        QStatusBar { background-color: #000000; color: #cc8d00; border-top: 1px solid #ffb000; }
        
        /* Menu and Dialog Custom Styling */
        QMenuBar { background-color: #000000; color: #ffb000; border-bottom: 1px solid #ffb000; }
        QMenuBar::item { background: transparent; padding: 4px 10px; border-radius: 4px; }
        QMenuBar::item:selected { background-color: #1a1a1a; color: #ffb000; }
        QMenu { background-color: #000000; color: #ffb000; border: 1px solid #ffb000; border-radius: 6px; padding: 5px; }
        QMenu::item { padding: 6px 20px; border-radius: 4px; }
        QMenu::item:selected { background-color: #ffb000; color: #000000; }
        QDialog { background-color: #000000; }
        QTextEdit { background-color: #000000; color: #ffb000; border: 1px solid #ffb000; border-radius: 5px; font-family: 'Consolas', 'Courier New', monospace; font-size: 13px; }
        
        /* Scrollbar Styling */
        QScrollBar:vertical { border: none; background: #000000; width: 10px; margin: 0px; }
        QScrollBar::handle:vertical { background: #1a1a1a; min-height: 20px; border-radius: 5px; border: 1px solid #ffb000; }
        QScrollBar::handle:vertical:hover { background: #2a2a2a; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
        QScrollBar:horizontal { border: none; background: #000000; height: 10px; margin: 0px; }
        QScrollBar::handle:horizontal { background: #1a1a1a; min-width: 20px; border-radius: 5px; border: 1px solid #ffb000; }
        QScrollBar::handle:horizontal:hover { background: #2a2a2a; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { border: none; background: none; }
    """
}

class CssEditorDialog(QDialog):
    """
    QDialog containing a QTextEdit to let user write/modify QSS directly.
    """
    def __init__(self, current_css, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Custom CSS Editor (自定义 CSS 样式)")
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlainText(current_css)
        layout.addWidget(self.text_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def get_css(self):
        return self.text_edit.toPlainText()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image & PDF Advanced Print Preview & Tiling Tool")
        self.resize(1280, 800)
        self.setAcceptDrops(True)
        
        # State variables
        self.input_file_path = ""
        self.is_pdf = False
        self.pdf_doc = None
        self.current_pdf_page = 0
        
        # Original PIL Image (in RGB mode) and its dimensions
        self.pil_image = None
        self.image_width = 0
        self.image_height = 0
        
        # Performance optimization: Cached QPixmap
        self.q_pixmap = None
        
        # Default States
        self.current_lang = "zh"
        self.current_theme = "dark"
        
        # Graphics view elements
        self.scene = QGraphicsScene(self)
        self.image_item = None
        self.page_items = []
        
        # Mode A mock elements
        self.mock_paper_item = None
        self.mock_printable_item = None
        self.mock_image_item = None
        
        # Build UI
        self.setup_ui()
        self.set_theme("dark")
        
        # Connect signals
        self.connect_signals()
        
        # Initial Retranslate to ZH
        self.retranslate_ui()
        
        # Update UI visibility
        self.update_controls_visibility()
        
    def setup_ui(self):
        # Create Menu Bar for Settings -> Language / Theme
        menubar = self.menuBar()
        self.menu_settings = menubar.addMenu("Settings")
        self.menu_language = self.menu_settings.addMenu("Language")
        
        self.action_lang_zh = self.menu_language.addAction("中文")
        self.action_lang_en = self.menu_language.addAction("English")
        self.action_lang_ja = self.menu_language.addAction("日本語")
        self.action_lang_fr = self.menu_language.addAction("Français")
        self.action_lang_ru = self.menu_language.addAction("Русский")
        self.action_lang_ar = self.menu_language.addAction("العربية")
        
        self.menu_theme = self.menu_settings.addMenu("Theme")
        self.action_theme_dark = self.menu_theme.addAction("Modern Dark (现代暗黑)")
        self.action_theme_light = self.menu_theme.addAction("Classic Light (经典明亮)")
        self.action_theme_nordic = self.menu_theme.addAction("Nordic Blue (北欧极地蓝)")
        self.action_theme_forest = self.menu_theme.addAction("Forest Green (森林绿意)")
        self.action_theme_matrix = self.menu_theme.addAction("Matrix Amber (黑客帝国)")
        self.action_theme_custom = self.menu_theme.addAction("Custom CSS (自定义CSS...)")
        
        # Central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Splitter to allow resizing sidebar
        splitter = QSplitter(Qt.Orientation.Horizontal, central_widget)
        main_layout.addWidget(splitter)
        
        # Sidebar widget
        sidebar = QWidget(splitter)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 10, 0)
        sidebar_layout.setSpacing(10)
        sidebar.setMaximumWidth(360)
        sidebar.setMinimumWidth(280)
        
        # --- 1. File Input Group ---
        self.file_group = QGroupBox("File Input", sidebar)
        file_layout = QVBoxLayout(self.file_group)
        self.btn_import = QPushButton("Import Image / PDF", self.file_group)
        self.lbl_file_info = QLabel("No file loaded.\n(Supports png, jpg, pdf)", self.file_group)
        self.lbl_file_info.setWordWrap(True)
        self.lbl_file_info.setStyleSheet("color: #888;")
        
        self.pdf_page_widget = QWidget(self.file_group)
        pdf_page_layout = QHBoxLayout(self.pdf_page_widget)
        pdf_page_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_pdf_page = QLabel("Select Page:", self.pdf_page_widget)
        self.combo_pdf_page = QComboBox(self.pdf_page_widget)
        pdf_page_layout.addWidget(self.lbl_pdf_page)
        pdf_page_layout.addWidget(self.combo_pdf_page)
        
        file_layout.addWidget(self.btn_import)
        file_layout.addWidget(self.lbl_file_info)
        file_layout.addWidget(self.pdf_page_widget)
        sidebar_layout.addWidget(self.file_group)
        
        # --- 2. Paper Setup Group ---
        self.paper_group = QGroupBox("Paper & Margins", sidebar)
        paper_layout = QVBoxLayout(self.paper_group)
        
        # Paper Size
        paper_size_widget = QWidget(self.paper_group)
        paper_size_layout = QHBoxLayout(paper_size_widget)
        paper_size_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_paper = QLabel("Paper Size:", paper_size_widget)
        self.combo_paper_size = QComboBox(paper_size_widget)
        # We populate dynamically in retranslate_ui, adding "Custom"
        paper_size_layout.addWidget(self.lbl_paper)
        paper_size_layout.addWidget(self.combo_paper_size)
        paper_layout.addWidget(paper_size_widget)
        
        # Custom Paper Formats widget (Hidden by default)
        self.custom_paper_widget = QWidget(self.paper_group)
        custom_paper_layout = QHBoxLayout(self.custom_paper_widget)
        custom_paper_layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_custom_w = QLabel("W (mm):", self.custom_paper_widget)
        self.spin_custom_w = QDoubleSpinBox(self.custom_paper_widget)
        self.spin_custom_w.setRange(100.0, 2000.0)
        self.spin_custom_w.setValue(210.0) # default A4
        
        self.lbl_custom_h = QLabel("H (mm):", self.custom_paper_widget)
        self.spin_custom_h = QDoubleSpinBox(self.custom_paper_widget)
        self.spin_custom_h.setRange(100.0, 2000.0)
        self.spin_custom_h.setValue(297.0)
        
        custom_paper_layout.addWidget(self.lbl_custom_w)
        custom_paper_layout.addWidget(self.spin_custom_w)
        custom_paper_layout.addWidget(self.lbl_custom_h)
        custom_paper_layout.addWidget(self.spin_custom_h)
        self.custom_paper_widget.setVisible(False)
        paper_layout.addWidget(self.custom_paper_widget)
        
        # Orientation
        orientation_widget = QWidget(self.paper_group)
        orientation_layout = QHBoxLayout(orientation_widget)
        orientation_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_orient = QLabel("Orientation:", orientation_widget)
        self.combo_orientation = QComboBox(orientation_widget)
        orientation_layout.addWidget(self.lbl_orient)
        orientation_layout.addWidget(self.combo_orientation)
        paper_layout.addWidget(orientation_widget)
        
        # Centering
        center_widget = QWidget(self.paper_group)
        center_layout = QHBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        self.chk_center_h = QCheckBox("Horizontal Center", center_widget)
        self.chk_center_v = QCheckBox("Vertical Center", center_widget)
        self.chk_center_h.setChecked(True)
        self.chk_center_v.setChecked(True)
        center_layout.addWidget(self.chk_center_h)
        center_layout.addWidget(self.chk_center_v)
        paper_layout.addWidget(center_widget)
        
        # Margins (mm)
        margins_group = QWidget(self.paper_group)
        margins_grid = QHBoxLayout(margins_group)
        margins_grid.setContentsMargins(0, 0, 0, 0)
        
        # Top/Bottom
        tb_widget = QWidget(margins_group)
        tb_layout = QVBoxLayout(tb_widget)
        tb_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_margin_top = QLabel("Top Margin (mm):", tb_widget)
        tb_layout.addWidget(self.lbl_margin_top)
        self.spin_margin_top = QDoubleSpinBox(tb_widget)
        self.spin_margin_top.setRange(0.0, 100.0)
        self.spin_margin_top.setValue(10.0)
        tb_layout.addWidget(self.spin_margin_top)
        
        self.lbl_margin_bottom = QLabel("Bottom Margin (mm):", tb_widget)
        tb_layout.addWidget(self.lbl_margin_bottom)
        self.spin_margin_bottom = QDoubleSpinBox(tb_widget)
        self.spin_margin_bottom.setRange(0.0, 100.0)
        self.spin_margin_bottom.setValue(10.0)
        tb_layout.addWidget(self.spin_margin_bottom)
        margins_grid.addWidget(tb_widget)
        
        # Left/Right
        lr_widget = QWidget(margins_group)
        lr_layout = QVBoxLayout(lr_widget)
        lr_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_margin_left = QLabel("Left Margin (mm):", lr_widget)
        lr_layout.addWidget(self.lbl_margin_left)
        self.spin_margin_left = QDoubleSpinBox(lr_widget)
        self.spin_margin_left.setRange(0.0, 100.0)
        self.spin_margin_left.setValue(10.0)
        lr_layout.addWidget(self.spin_margin_left)
        
        self.lbl_margin_right = QLabel("Right Margin (mm):", lr_widget)
        lr_layout.addWidget(self.lbl_margin_right)
        self.spin_margin_right = QDoubleSpinBox(lr_widget)
        self.spin_margin_right.setRange(0.0, 100.0)
        self.spin_margin_right.setValue(10.0)
        lr_layout.addWidget(self.spin_margin_right)
        margins_grid.addWidget(lr_widget)
        paper_layout.addWidget(margins_group)
        
        # Overlap Margin (mm)
        overlap_widget = QWidget(self.paper_group)
        overlap_layout = QHBoxLayout(overlap_widget)
        overlap_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_overlap = QLabel("Overlap Margin (mm):", overlap_widget)
        self.spin_overlap = QDoubleSpinBox(overlap_widget)
        self.spin_overlap.setRange(0.0, 50.0)
        self.spin_overlap.setValue(0.0)
        overlap_layout.addWidget(self.lbl_overlap)
        overlap_layout.addWidget(self.spin_overlap)
        paper_layout.addWidget(overlap_widget)
        
        sidebar_layout.addWidget(self.paper_group)
        
        # --- 3. Scaling & Layout Mode Group ---
        self.layout_group = QGroupBox("Layout & Scaling", sidebar)
        layout_layout = QVBoxLayout(self.layout_group)
        
        self.radio_mode_a = QRadioButton("Mode A: Scale to % (Single Page)", self.layout_group)
        self.radio_mode_b = QRadioButton("Mode B: Fit to X x Y Pages (Tiling)", self.layout_group)
        self.radio_mode_b.setChecked(True)
        layout_layout.addWidget(self.radio_mode_a)
        layout_layout.addWidget(self.radio_mode_b)
        
        # Mode A Panel
        self.panel_mode_a = QFrame(self.layout_group)
        self.panel_mode_a.setFrameShape(QFrame.Shape.StyledPanel)
        mode_a_layout = QHBoxLayout(self.panel_mode_a)
        self.lbl_scale_factor = QLabel("Scale factor:", self.panel_mode_a)
        mode_a_layout.addWidget(self.lbl_scale_factor)
        self.spin_scale_pct = QSpinBox(self.panel_mode_a)
        self.spin_scale_pct.setRange(10, 1000)
        self.spin_scale_pct.setValue(100)
        self.spin_scale_pct.setSuffix("%")
        mode_a_layout.addWidget(self.spin_scale_pct)
        layout_layout.addWidget(self.panel_mode_a)
        
        # Mode B Panel
        self.panel_mode_b = QFrame(self.layout_group)
        self.panel_mode_b.setFrameShape(QFrame.Shape.StyledPanel)
        mode_b_layout = QVBoxLayout(self.panel_mode_b)
        
        grid_widget = QWidget(self.panel_mode_b)
        grid_layout = QHBoxLayout(grid_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_cols = QLabel("Cols (X):", grid_widget)
        grid_layout.addWidget(self.lbl_cols)
        self.spin_cols = QSpinBox(grid_widget)
        self.spin_cols.setRange(1, 20)
        self.spin_cols.setValue(1)
        grid_layout.addWidget(self.spin_cols)
        
        self.lbl_rows = QLabel("Rows (Y):", grid_widget)
        grid_layout.addWidget(self.lbl_rows)
        self.spin_rows = QSpinBox(grid_widget)
        self.spin_rows.setRange(1, 20)
        self.spin_rows.setValue(3)
        grid_layout.addWidget(self.spin_rows)
        mode_b_layout.addWidget(grid_widget)
        
        # Drag lock options
        locks_widget = QWidget(self.panel_mode_b)
        locks_layout = QHBoxLayout(locks_widget)
        locks_layout.setContentsMargins(0, 0, 0, 0)
        self.chk_lock_h = QCheckBox("Lock X Alignment", locks_widget)
        self.chk_lock_h.setChecked(True)
        self.chk_lock_v = QCheckBox("Lock Y Alignment", locks_widget)
        locks_layout.addWidget(self.chk_lock_h)
        locks_layout.addWidget(self.chk_lock_v)
        mode_b_layout.addWidget(locks_widget)
        
        # Scale Slider & SpinBox
        slider_widget = QWidget(self.panel_mode_b)
        slider_layout = QVBoxLayout(slider_widget)
        slider_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_page_scale = QLabel("Paper Size Scale: 100%", slider_widget)
        slider_layout.addWidget(self.lbl_page_scale)
        
        # Horizontal container for QSlider and QSpinBox
        scale_ctrl_widget = QWidget(slider_widget)
        scale_ctrl_layout = QHBoxLayout(scale_ctrl_widget)
        scale_ctrl_layout.setContentsMargins(0, 0, 0, 0)
        scale_ctrl_layout.setSpacing(5)
        
        self.slider_page_scale = QSlider(Qt.Orientation.Horizontal, scale_ctrl_widget)
        self.slider_page_scale.setRange(10, 300)
        self.slider_page_scale.setValue(100)
        
        self.spin_page_scale = QSpinBox(scale_ctrl_widget)
        self.spin_page_scale.setRange(10, 300)
        self.spin_page_scale.setValue(100)
        self.spin_page_scale.setSuffix("%")
        self.spin_page_scale.setFixedWidth(65)
        
        scale_ctrl_layout.addWidget(self.slider_page_scale)
        scale_ctrl_layout.addWidget(self.spin_page_scale)
        
        slider_layout.addWidget(scale_ctrl_widget)
        
        # Auto-fit scale button
        self.btn_autofit = QPushButton("Auto-fit Scale to Cover Image", slider_widget)
        self.btn_autofit.setStyleSheet("background-color: #2d2d2d; color: #007aff; border: 1px solid #007aff;")
        slider_layout.addWidget(self.btn_autofit)
        
        # Optimize Seams (Avoid Text Cut) button
        self.btn_optimize_seams = QPushButton("Optimize Seams", slider_widget)
        self.btn_optimize_seams.setStyleSheet("background-color: #2d2d2d; color: #38bdf8; border: 1px solid #38bdf8;")
        slider_layout.addWidget(self.btn_optimize_seams)
        
        mode_b_layout.addWidget(slider_widget)
        layout_layout.addWidget(self.panel_mode_b)
        
        sidebar_layout.addWidget(self.layout_group)
        
        # --- 4. Export & Actions Group ---
        self.action_group = QGroupBox("Actions", sidebar)
        action_layout = QVBoxLayout(self.action_group)
        self.btn_reset = QPushButton("Reset Paper Grid Layout", self.action_group)
        self.btn_reset.setObjectName("reset_btn")
        self.btn_export = QPushButton("Generate PDF", self.action_group)
        
        action_layout.addWidget(self.btn_reset)
        action_layout.addWidget(self.btn_export)
        sidebar_layout.addWidget(self.action_group)
        
        sidebar_layout.addStretch()
        
        # Main Preview Viewport Area (Right side)
        preview_container = QWidget(splitter)
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(10, 0, 0, 0)
        preview_layout.setSpacing(5)
        
        # Toolbar above the graphics view
        toolbar = QWidget(preview_container)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(10)
        
        self.lbl_view_title = QLabel("Print Preview", toolbar)
        self.lbl_view_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        toolbar_layout.addWidget(self.lbl_view_title)
        toolbar_layout.addStretch()
        
        # Zoom controls
        self.btn_zoom_in = QPushButton("", toolbar)
        self.btn_zoom_in.setFixedSize(30, 30)
        self.btn_zoom_in.setObjectName("zoom_btn")
        
        self.btn_zoom_out = QPushButton("", toolbar)
        self.btn_zoom_out.setFixedSize(30, 30)
        self.btn_zoom_out.setObjectName("zoom_btn")
        
        self.btn_zoom_fit = QPushButton("Fit All", toolbar)
        self.btn_zoom_fit.setFixedHeight(30)
        self.btn_zoom_fit.setObjectName("zoom_btn")
        self.btn_zoom_fit.setStyleSheet("padding: 0 10px;")
        
        self.btn_zoom_width = QPushButton("Fit Width", toolbar)
        self.btn_zoom_width.setFixedHeight(30)
        self.btn_zoom_width.setObjectName("zoom_btn")
        self.btn_zoom_width.setStyleSheet("padding: 0 10px;")
        
        self.lbl_zoom_level = QLabel("Zoom: 100%", toolbar)
        self.lbl_zoom_level.setMinimumWidth(80)
        
        toolbar_layout.addWidget(self.btn_zoom_out)
        toolbar_layout.addWidget(self.lbl_zoom_level)
        toolbar_layout.addWidget(self.btn_zoom_in)
        toolbar_layout.addWidget(self.btn_zoom_fit)
        toolbar_layout.addWidget(self.btn_zoom_width)
        
        preview_layout.addWidget(toolbar)
        
        # The Custom Graphics View
        self.view = InteractiveGraphicsView(preview_container)
        self.view.setScene(self.scene)
        preview_layout.addWidget(self.view)
        
        # Add widgets to splitter
        splitter.addWidget(sidebar)
        splitter.addWidget(preview_container)
        
        # Status Bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

    def set_theme(self, theme_name):
        self.current_theme = theme_name
        if theme_name in THEMES:
            QApplication.instance().setStyleSheet(THEMES[theme_name])
        elif theme_name == "custom":
            current_qss = QApplication.instance().styleSheet() or ""
            dialog = CssEditorDialog(current_qss, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                custom_qss = dialog.get_css()
                QApplication.instance().setStyleSheet(custom_qss)
        self.update_zoom_icons()

    def connect_signals(self):
        # File operations
        self.btn_import.clicked.connect(self.on_import_clicked)
        self.combo_pdf_page.currentIndexChanged.connect(self.on_pdf_page_changed)
        
        # Preview updates triggered by setting changes
        self.combo_paper_size.currentIndexChanged.connect(self.on_paper_size_combo_changed)
        self.combo_orientation.currentIndexChanged.connect(self.update_preview)
        self.chk_center_h.toggled.connect(self.update_preview)
        self.chk_center_v.toggled.connect(self.update_preview)
        
        self.spin_margin_top.valueChanged.connect(self.update_preview)
        self.spin_margin_bottom.valueChanged.connect(self.update_preview)
        self.spin_margin_left.valueChanged.connect(self.update_preview)
        self.spin_margin_right.valueChanged.connect(self.update_preview)
        self.spin_overlap.valueChanged.connect(self.update_preview)
        
        self.spin_custom_w.valueChanged.connect(self.update_preview)
        self.spin_custom_h.valueChanged.connect(self.update_preview)
        
        # Modes toggle
        self.radio_mode_a.toggled.connect(self.on_mode_toggled)
        self.radio_mode_b.toggled.connect(self.on_mode_toggled)
        
        # Mode A parameters
        self.spin_scale_pct.valueChanged.connect(self.update_preview)
        
        # Mode B parameters
        self.spin_cols.valueChanged.connect(self.on_grid_settings_changed)
        self.spin_rows.valueChanged.connect(self.on_grid_settings_changed)
        self.chk_lock_h.toggled.connect(self.update_drag_constraints)
        self.chk_lock_v.toggled.connect(self.update_drag_constraints)
        
        self.slider_page_scale.valueChanged.connect(self.on_slider_scale_changed)
        self.btn_autofit.clicked.connect(self.on_autofit_clicked)
        self.btn_optimize_seams.clicked.connect(self.on_optimize_seams_clicked)
        
        # Action buttons
        self.btn_reset.clicked.connect(self.reset_layout)
        self.btn_export.clicked.connect(self.export_to_pdf)
        
        # Theme trigger connections
        self.action_theme_dark.triggered.connect(lambda: self.set_theme("dark"))
        self.action_theme_light.triggered.connect(lambda: self.set_theme("light"))
        self.action_theme_nordic.triggered.connect(lambda: self.set_theme("nordic"))
        self.action_theme_forest.triggered.connect(lambda: self.set_theme("forest"))
        self.action_theme_matrix.triggered.connect(lambda: self.set_theme("matrix"))
        self.action_theme_custom.triggered.connect(lambda: self.set_theme("custom"))
        
        # Language trigger connections
        self.action_lang_zh.triggered.connect(lambda: self.change_language("zh"))
        self.action_lang_en.triggered.connect(lambda: self.change_language("en"))
        self.action_lang_ja.triggered.connect(lambda: self.change_language("ja"))
        self.action_lang_fr.triggered.connect(lambda: self.change_language("fr"))
        self.action_lang_ru.triggered.connect(lambda: self.change_language("ru"))
        self.action_lang_ar.triggered.connect(lambda: self.change_language("ar"))
        
        # Sync slider and spinbox for page scale
        self.slider_page_scale.valueChanged.connect(self.on_slider_scale_changed)
        self.spin_page_scale.valueChanged.connect(self.on_spin_scale_changed)
        
        # View zoom controls
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        self.btn_zoom_fit.clicked.connect(self.zoom_fit_all)
        self.btn_zoom_width.clicked.connect(self.zoom_fit_width)
        
        # Wire graphics view zoom change to label
        self.view.zoom_changed_callback = self.update_zoom_label

    def on_paper_size_combo_changed(self):
        is_custom = self.combo_paper_size.currentIndex() == len(PRESET_PAPERS)
        self.custom_paper_widget.setVisible(is_custom)
        self.update_preview()

    def change_language(self, lang_code):
        self.current_lang = lang_code
        self.retranslate_ui()
        self.update_preview()
        self.zoom_fit_all()

    def retranslate_ui(self):
        lang = self.current_lang
        t = TRANSLATIONS[lang]
        
        # Override Style menu title (settings/style) and options
        menu_theme_titles = {
            "zh": "样式",
            "en": "Style",
            "ja": "スタイル",
            "fr": "Style",
            "ru": "Стиль",
            "ar": "النمط"
        }
        theme_names = {
            "zh": {
                "dark": "现代暗黑 (Modern Dark)",
                "light": "经典明亮 (Classic Light)",
                "nordic": "北欧极地蓝 (Nordic Blue)",
                "forest": "森林绿意 (Forest Green)",
                "matrix": "黑客帝国 (Matrix Amber)",
                "custom": "自定义 CSS (Custom QSS)..."
            },
            "en": {
                "dark": "Modern Dark",
                "light": "Classic Light",
                "nordic": "Nordic Blue",
                "forest": "Forest Green",
                "matrix": "Matrix Amber",
                "custom": "Custom CSS..."
            },
            "ja": {
                "dark": "モダンダーク",
                "light": "クラシックライト",
                "nordic": "ノルディックブルー",
                "forest": "フォレストグリーン",
                "matrix": "マトリックスアンバー",
                "custom": "カスタムQSS..."
            },
            "fr": {
                "dark": "Sombre Moderne",
                "light": "Clair Classique",
                "nordic": "Bleu Nordique",
                "forest": "Vert Forêt",
                "matrix": "Ambre Matrice",
                "custom": "QSS Personnalisé..."
            },
            "ru": {
                "dark": "Современный темный",
                "light": "Классический светлый",
                "nordic": "Северный синий",
                "forest": "Лесной зеленый",
                "matrix": "Янтарная матрица",
                "custom": "Пользовательский QSS..."
            },
            "ar": {
                "dark": "مظلم حديث",
                "light": "مضيء كلاسيكي",
                "nordic": "أزرق شمالي",
                "forest": "أخضر غابة",
                "matrix": "كهرماني مصفوفة",
                "custom": "QSS مخصص..."
            }
        }
        
        # Menu Bar
        self.menu_settings.setTitle(t["menu_settings"])
        self.menu_language.setTitle(t["menu_language"])
        
        theme_title = menu_theme_titles.get(lang, "Style")
        self.menu_theme.setTitle(theme_title)
        
        t_theme = theme_names.get(lang, theme_names["en"])
        self.action_theme_dark.setText(t_theme["dark"])
        self.action_theme_light.setText(t_theme["light"])
        self.action_theme_nordic.setText(t_theme["nordic"])
        self.action_theme_forest.setText(t_theme["forest"])
        self.action_theme_matrix.setText(t_theme["matrix"])
        self.action_theme_custom.setText(t_theme["custom"])
        
        # Sidebar Groups
        self.file_group.setTitle(t["file_group_title"])
        self.btn_import.setText(t["import_btn"])
        self.lbl_pdf_page.setText(t["select_page"])
        
        self.paper_group.setTitle(t["paper_group_title"])
        self.lbl_paper.setText(t["lbl_paper"])
        
        # Re-populate Paper Size Combo
        self.combo_paper_size.blockSignals(True)
        curr_paper = self.combo_paper_size.currentIndex()
        self.combo_paper_size.clear()
        
        # Translate the options (Custom added)
        paper_options = []
        for name, w, h in PRESET_PAPERS:
            paper_options.append(f"{name} ({w} x {h} mm)")
            
        if lang == "zh":
            paper_options.append("自定义纸张 (Custom)...")
        elif lang == "ja":
            paper_options.append("カスタム用紙...")
        elif lang == "fr":
            paper_options.append("Papier Personnalisé...")
        elif lang == "ru":
            paper_options.append("Пользовательский...")
        elif lang == "ar":
            paper_options.append("ورقة مخصصة...")
        else:
            paper_options.append("Custom Paper...")
            
        self.combo_paper_size.addItems(paper_options)
        # Default to A4 (index 4) if not set yet
        self.combo_paper_size.setCurrentIndex(curr_paper if curr_paper >= 0 else 4)
        self.combo_paper_size.blockSignals(False)
        
        # Custom Paper labels
        self.lbl_custom_w.setText(t["custom_w_label"])
        self.lbl_custom_h.setText(t["custom_h_label"])
        
        self.lbl_orient.setText(t["lbl_orient"])
        
        # Re-populate Orientation Combo
        self.combo_orientation.blockSignals(True)
        curr_orient = self.combo_orientation.currentIndex()
        self.combo_orientation.clear()
        self.combo_orientation.addItems([t["orient_portrait"], t["orient_landscape"]])
        self.combo_orientation.setCurrentIndex(curr_orient if curr_orient >= 0 else 0)
        self.combo_orientation.blockSignals(False)
        
        self.chk_center_h.setText(t["chk_center_h"])
        self.chk_center_v.setText(t["chk_center_v"])
        self.lbl_margin_top.setText(t["lbl_margin_top"])
        self.lbl_margin_bottom.setText(t["lbl_margin_bottom"])
        self.lbl_margin_left.setText(t["lbl_margin_left"])
        self.lbl_margin_right.setText(t["lbl_margin_right"])
        self.lbl_overlap.setText(t["lbl_overlap"])
        
        self.layout_group.setTitle(t["layout_group_title"])
        self.radio_mode_a.setText(t["radio_mode_a"])
        self.radio_mode_b.setText(t["radio_mode_b"])
        
        self.lbl_scale_factor.setText(t["lbl_scale_factor"])
        self.lbl_cols.setText(t["lbl_cols"])
        self.lbl_rows.setText(t["lbl_rows"])
        
        self.chk_lock_h.setText(t["lock_x"])
        self.chk_lock_v.setText(t["lock_y"])
        
        val_scale = self.slider_page_scale.value()
        self.lbl_page_scale.setText(t["lbl_page_scale"].format(val=val_scale))
        self.btn_autofit.setText(t["autofit_btn"])
        self.btn_optimize_seams.setText(t["optimize_btn"])
        
        self.action_group.setTitle(t["action_group_title"])
        self.btn_reset.setText(t["btn_reset"])
        self.btn_export.setText(t["btn_export"])
        
        self.btn_zoom_fit.setText(t["fit_all"])
        self.btn_zoom_width.setText(t["fit_width"])
        
        # Dynamic Text fields
        is_mode_a = self.radio_mode_a.isChecked()
        if is_mode_a:
            self.lbl_view_title.setText(t["view_title_a"])
        else:
            self.lbl_view_title.setText(t["view_title_b"])
            
        if self.pil_image is None:
            self.lbl_file_info.setText(t["no_file"])
            self.status_bar.showMessage(t["status_ready"])
        else:
            if self.is_pdf:
                self.lbl_file_info.setText(
                    t["file_info_pdf"].format(
                        name=os.path.basename(self.input_file_path),
                        page_idx=self.current_pdf_page + 1,
                        total=self.pdf_doc.pageCount(),
                        w=self.image_width,
                        h=self.image_height
                    )
                )
            else:
                self.lbl_file_info.setText(
                    t["file_info_img"].format(
                        name=os.path.basename(self.input_file_path),
                        w=self.image_width,
                        h=self.image_height
                    )
                )
            self.status_bar.showMessage(t["status_loaded"].format(name=os.path.basename(self.input_file_path)))

    def update_controls_visibility(self):
        # PDF page selection
        self.pdf_page_widget.setVisible(self.is_pdf)
        
        # Mode panels
        is_mode_a = self.radio_mode_a.isChecked()
        self.panel_mode_a.setVisible(is_mode_a)
        self.panel_mode_b.setVisible(not is_mode_a)
        
        # Disable export and actions if no image loaded
        has_image = self.pil_image is not None
        self.btn_export.setEnabled(has_image)
        self.btn_reset.setEnabled(has_image and not is_mode_a)
        
        # Labels and title
        t = TRANSLATIONS[self.current_lang]
        if is_mode_a:
            self.lbl_view_title.setText(t["view_title_a"])
        else:
            self.lbl_view_title.setText(t["view_title_b"])

    def on_mode_toggled(self):
        self.update_controls_visibility()
        self.update_preview()
        self.zoom_fit_all()

    def update_zoom_label(self, scale_val):
        self.lbl_zoom_level.setText(f"Zoom: {int(scale_val * 100)}%")

    def on_import_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image or PDF File", "",
            "Supported Files (*.png *.jpg *.jpeg *.pdf);;Images (*.png *.jpg *.jpeg);;PDF Documents (*.pdf)"
        )
        if not file_path:
            return
            
        self.load_file(file_path)

    def load_file(self, file_path):
        t = TRANSLATIONS[self.current_lang]
        self.status_bar.showMessage(t["status_loading"].format(name=os.path.basename(file_path)))
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        try:
            self.input_file_path = file_path
            self.is_pdf = file_path.lower().endswith('.pdf')
            
            if self.is_pdf:
                self.pdf_doc = QPdfDocument(self)
                err = self.pdf_doc.load(file_path)
                if err != QPdfDocument.Error.None_:
                    raise Exception(f"Failed to load PDF: Error code {err}")
                    
                page_count = self.pdf_doc.pageCount()
                self.combo_pdf_page.blockSignals(True)
                self.combo_pdf_page.clear()
                for i in range(page_count):
                    self.combo_pdf_page.addItem(f"Page {i + 1}")
                self.combo_pdf_page.blockSignals(False)
                
                self.current_pdf_page = 0
                self.combo_pdf_page.setCurrentIndex(0)
                self.render_pdf_page()
            else:
                self.pdf_doc = None
                img = Image.open(file_path)
                self.pil_image = img.convert("RGB")
                self.image_width, self.image_height = self.pil_image.size
                
                # Performance optimization: Convert PIL Image to QPixmap ONCE on load
                buffer = BytesIO()
                self.pil_image.save(buffer, format="PNG")
                self.q_pixmap = QPixmap()
                self.q_pixmap.loadFromData(buffer.getvalue())
            
            # Default scale to 100%
            self.slider_page_scale.setValue(100)
            
            self.retranslate_ui()
            self.update_controls_visibility()
            self.update_preview()
            self.zoom_fit_all()
            
        except Exception as e:
            QMessageBox.critical(self, t["msg_load_error_title"], f"An error occurred:\n{str(e)}")
            self.status_bar.showMessage(t["status_error_loading"])
        finally:
            QApplication.restoreOverrideCursor()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                    self.load_file(file_path)
                    event.acceptProposedAction()

    def render_pdf_page(self):
        if not self.pdf_doc:
            return
            
        page_idx = self.combo_pdf_page.currentIndex()
        self.current_pdf_page = page_idx
        
        # Render PDF page to high-res QImage at 300 DPI
        pt_size = self.pdf_doc.pagePointSize(page_idx)
        dpi = 300.0
        scale = dpi / 72.0
        w = int(pt_size.width() * scale)
        h = int(pt_size.height() * scale)
        
        qimg = self.pdf_doc.render(page_idx, QSize(w, h))
        if qimg.isNull():
            raise Exception("QPdfDocument render returned null image")
            
        # Performance optimization: Cache QPixmap directly from QImage
        self.q_pixmap = QPixmap.fromImage(qimg)
        
        # Keep PIL image for crops
        qimg_rgba = qimg.convertToFormat(QImage.Format.Format_RGBA8888)
        width, height = qimg_rgba.width(), qimg_rgba.height()
        data = qimg_rgba.constBits().tobytes()
        pil_img = Image.frombytes("RGBA", (width, height), data)
        self.pil_image = pil_img.convert("RGB")
        self.image_width, self.image_height = self.pil_image.size

    def on_pdf_page_changed(self):
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            self.render_pdf_page()
            self.retranslate_ui()
            self.update_preview()
            self.zoom_fit_all()
        except Exception as e:
            t = TRANSLATIONS[self.current_lang]
            QMessageBox.critical(self, t["msg_error_title"], str(e))
        finally:
            QApplication.restoreOverrideCursor()

    def get_paper_size_mm(self):
        paper_idx = self.combo_paper_size.currentIndex()
        if paper_idx == len(PRESET_PAPERS): # Custom size
            return self.spin_custom_w.value(), self.spin_custom_h.value()
            
        if 0 <= paper_idx < len(PRESET_PAPERS):
            name, w, h = PRESET_PAPERS[paper_idx]
        else:
            w, h = 210, 297  # Fallback to A4
            
        is_landscape = self.combo_orientation.currentIndex() == 1
        if is_landscape:
            w, h = h, w
        return w, h

    def get_margins_mm(self):
        return (
            self.spin_margin_left.value(),
            self.spin_margin_right.value(),
            self.spin_margin_top.value(),
            self.spin_margin_bottom.value()
        )

    def on_grid_settings_changed(self):
        self.update_preview()

    def on_slider_scale_changed(self, val):
        self.spin_page_scale.blockSignals(True)
        self.spin_page_scale.setValue(val)
        self.spin_page_scale.blockSignals(False)
        t = TRANSLATIONS[self.current_lang]
        self.lbl_page_scale.setText(t["lbl_page_scale"].format(val=val))
        self.update_preview()

    def on_spin_scale_changed(self, val):
        self.slider_page_scale.blockSignals(True)
        self.slider_page_scale.setValue(val)
        self.slider_page_scale.blockSignals(False)
        t = TRANSLATIONS[self.current_lang]
        self.lbl_page_scale.setText(t["lbl_page_scale"].format(val=val))
        self.update_preview()

    def on_optimize_seams_clicked(self):
        if self.pil_image is None or self.radio_mode_a.isChecked():
            return
            
        import numpy as np
        
        cols = self.spin_cols.value()
        rows = self.spin_rows.value()
        
        if rows <= 1:
            return # No horizontal seams to optimize
            
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        try:
            # 1. Convert PIL image to grayscale numpy array
            img_gray = np.array(self.pil_image.convert("L"))
            # Calculate horizontal differences (energy)
            diff = np.abs(np.diff(img_gray, axis=1))
            row_energy = np.sum(diff, axis=1)
            
            # Smooth row energy with a simple 5-pixel moving average to reduce noise
            window_size = 5
            smoothed_energy = np.convolve(row_energy, np.ones(window_size)/window_size, mode='same')
            
            # Get current layout parameters
            paper_w_mm, paper_h_mm = self.get_paper_size_mm()
            m_left, m_right, m_top, m_bottom = self.get_margins_mm()
            printable_w_mm = max(1.0, paper_w_mm - m_left - m_right)
            printable_h_mm = max(1.0, paper_h_mm - m_top - m_bottom)
            printable_ratio = printable_h_mm / printable_w_mm
            
            page_scale_factor = self.slider_page_scale.value() / 100.0
            w_rect = (self.image_width / cols) * page_scale_factor
            h_rect = w_rect * printable_ratio
            
            overlap_mm = self.spin_overlap.value()
            overlap_px = overlap_mm * (w_rect / printable_w_mm)
            
            # Run sequential split optimization
            positions = [0.0] * rows
            positions[0] = 0.0
            
            for r in range(1, rows):
                default_split = positions[r-1] + h_rect - overlap_px
                # Search window: +/- 15% of h_rect
                search_limit = int(h_rect * 0.15)
                search_start = max(0, int(default_split - search_limit))
                search_end = min(self.image_height - 1, int(default_split + search_limit))
                
                if search_end > search_start:
                    window_energy = smoothed_energy[search_start:search_end]
                    min_idx = np.argmin(window_energy)
                    optimal_split = search_start + min_idx
                    positions[r] = optimal_split
                else:
                    positions[r] = default_split
            
            # Update the page items in the scene
            for item in self.page_items:
                r = item.row_idx
                new_y = positions[r]
                item.setPos(item.pos().x(), new_y)
                item.fixed_y = new_y
                
            self.scene.update()
            t = TRANSLATIONS[self.current_lang]
            self.status_bar.showMessage(t["status_optimized"], 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Optimization Error", str(e))
        finally:
            QApplication.restoreOverrideCursor()

    def on_autofit_clicked(self):
        if self.pil_image is None:
            return
            
        paper_w_mm, paper_h_mm = self.get_paper_size_mm()
        m_left, m_right, m_top, m_bottom = self.get_margins_mm()
        
        printable_w_mm = max(1.0, paper_w_mm - m_left - m_right)
        printable_h_mm = max(1.0, paper_h_mm - m_top - m_bottom)
        printable_ratio = printable_h_mm / printable_w_mm
        
        cols = self.spin_cols.value()
        rows = self.spin_rows.value()
        
        w_base_px = self.image_width / cols
        h_base_px = w_base_px * printable_ratio
        total_grid_h_px = rows * h_base_px
        
        target_k = self.image_height / total_grid_h_px
        
        slider_val = int(target_k * 100)
        slider_val = max(10, min(slider_val, 300))
        
        self.slider_page_scale.blockSignals(True)
        self.spin_page_scale.blockSignals(True)
        self.slider_page_scale.setValue(slider_val)
        self.spin_page_scale.setValue(slider_val)
        self.slider_page_scale.blockSignals(False)
        self.spin_page_scale.blockSignals(False)
        
        t = TRANSLATIONS[self.current_lang]
        self.lbl_page_scale.setText(t["lbl_page_scale"].format(val=slider_val))
        self.update_preview()
        self.status_bar.showMessage(t["status_loaded"].format(name=os.path.basename(self.input_file_path)), 3000)

    def update_preview(self):
        if self.pil_image is None or self.q_pixmap is None:
            return
            
        self.scene.clear()
        self.page_items = []
        self.image_item = None
        self.mock_paper_item = None
        self.mock_printable_item = None
        self.mock_image_item = None
        
        is_mode_a = self.radio_mode_a.isChecked()
        
        # Performance optimization: Reuses pre-loaded self.q_pixmap directly without PNG serialization
        if is_mode_a:
            self.setup_mode_a_preview(self.q_pixmap)
        else:
            self.setup_mode_b_preview(self.q_pixmap)

    def setup_mode_a_preview(self, q_pixmap):
        scale_mm_to_px = 2.0
        
        paper_w_mm, paper_h_mm = self.get_paper_size_mm()
        m_left, m_right, m_top, m_bottom = self.get_margins_mm()
        
        paper_w = paper_w_mm * scale_mm_to_px
        paper_h = paper_h_mm * scale_mm_to_px
        
        p_left = m_left * scale_mm_to_px
        p_right = m_right * scale_mm_to_px
        p_top = m_top * scale_mm_to_px
        p_bottom = m_bottom * scale_mm_to_px
        
        printable_w = max(1.0, paper_w - p_left - p_right)
        printable_h = max(1.0, paper_h - p_top - p_bottom)
        
        self.mock_paper_item = QGraphicsRectItem(0, 0, paper_w, paper_h)
        self.mock_paper_item.setBrush(QBrush(QColor(255, 255, 255)))
        self.mock_paper_item.setPen(QPen(QColor(100, 100, 100), 1))
        self.scene.addItem(self.mock_paper_item)
        
        self.mock_printable_item = QGraphicsRectItem(p_left, p_top, printable_w, printable_h)
        self.mock_printable_item.setPen(QPen(QColor(0, 122, 255, 120), 1, Qt.PenStyle.DashLine))
        self.scene.addItem(self.mock_printable_item)
        
        dpi_100_scale = 2.0 / (150.0 / 25.4)
        user_scale = self.spin_scale_pct.value() / 100.0
        final_scale = dpi_100_scale * user_scale
        
        self.mock_image_item = QGraphicsPixmapItem(q_pixmap)
        self.mock_image_item.setScale(final_scale)
        self.scene.addItem(self.mock_image_item)
        
        img_w = q_pixmap.width() * final_scale
        img_h = q_pixmap.height() * final_scale
        
        if self.chk_center_h.isChecked():
            x = p_left + (printable_w - img_w) / 2
        else:
            x = p_left
            
        if self.chk_center_v.isChecked():
            y = p_top + (printable_h - img_h) / 2
        else:
            y = p_top
            
        self.mock_image_item.setPos(x, y)
        self.scene.setSceneRect(QRectF(-20, -20, paper_w + 40, paper_h + 40))

    def setup_mode_b_preview(self, q_pixmap):
        self.image_item = QGraphicsPixmapItem(q_pixmap)
        self.scene.addItem(self.image_item)
        
        paper_w_mm, paper_h_mm = self.get_paper_size_mm()
        m_left, m_right, m_top, m_bottom = self.get_margins_mm()
        
        printable_w_mm = max(1.0, paper_w_mm - m_left - m_right)
        printable_h_mm = max(1.0, paper_h_mm - m_top - m_bottom)
        printable_ratio = printable_h_mm / printable_w_mm
        
        cols = self.spin_cols.value()
        rows = self.spin_rows.value()
        
        page_scale_factor = self.slider_page_scale.value() / 100.0
        w_rect = (self.image_width / cols) * page_scale_factor
        h_rect = w_rect * printable_ratio
        
        # Overlap margin calculation in pixels
        overlap_mm = self.spin_overlap.value()
        overlap_px = overlap_mm * (w_rect / printable_w_mm)
        
        boundary_rect = QRectF(0, 0, self.image_width, self.image_height)
        
        for r in range(rows):
            for c in range(cols):
                page_num = c + r * cols + 1
                # Default positions overlap by overlap_px
                default_x = c * (w_rect - overlap_px)
                default_y = r * (h_rect - overlap_px)
                
                rect = QRectF(0, 0, w_rect, h_rect)
                item = DraggablePageItem(rect, r, c, page_num)
                item.setPos(default_x, default_y)
                
                # Connect interaction callbacks
                item.on_changed_callback = self.on_page_item_moved
                
                self.scene.addItem(item)
                self.page_items.append(item)
                
        self.update_drag_constraints()
        self.scene.setSceneRect(boundary_rect)

    def update_drag_constraints(self):
        if not self.page_items:
            return
            
        cols = self.spin_cols.value()
        
        lock_x = self.chk_lock_h.isChecked()
        lock_y = self.chk_lock_v.isChecked()
        
        boundary_rect = QRectF(0, 0, self.image_width, self.image_height)
        
        for item in self.page_items:
            paper_w_mm, paper_h_mm = self.get_paper_size_mm()
            m_left, m_right, m_top, m_bottom = self.get_margins_mm()
            printable_w_mm = max(1.0, paper_w_mm - m_left - m_right)
            printable_h_mm = max(1.0, paper_h_mm - m_top - m_bottom)
            printable_ratio = printable_h_mm / printable_w_mm
            
            w_rect = item.rect().width()
            h_rect = item.rect().height()
            
            # Overlap margin calculation
            overlap_mm = self.spin_overlap.value()
            overlap_px = overlap_mm * (w_rect / printable_w_mm)
            
            fixed_x = item.col_idx * (w_rect - overlap_px)
            fixed_y = item.row_idx * (h_rect - overlap_px)
            
            item.set_constraints(lock_x, lock_y, fixed_x, fixed_y, boundary_rect)

    def on_page_item_moved(self, item, pos):
        rect = item.rect()
        x_start = int(pos.x())
        y_start = int(pos.y())
        x_end = int(x_start + rect.width())
        y_end = int(y_start + rect.height())
        
        t = TRANSLATIONS[self.current_lang]
        self.status_bar.showMessage(
            t["status_dragging"].format(num=item.page_num, x1=x_start, x2=x_end, y1=y_start, y2=y_end),
            2000
        )

    def reset_layout(self):
        if self.pil_image is None or self.radio_mode_a.isChecked():
            return
            
        self.update_preview()
        t = TRANSLATIONS[self.current_lang]
        self.status_bar.showMessage(t["status_reset"], 3000)

    def zoom_fit_all(self):
        if self.pil_image is None:
            return
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.update_zoom_label(self.view.transform().m11())

    def zoom_fit_width(self):
        if self.pil_image is None:
            return
        rect = self.scene.sceneRect()
        view_w = self.view.viewport().width() - 30
        if view_w <= 0:
            return
        scale_factor = view_w / rect.width()
        self.view.setTransform(QTransform().scale(scale_factor, scale_factor))
        self.update_zoom_label(scale_factor)

    def zoom_in(self):
        if self.pil_image is None:
            return
        current_scale = self.view.transform().m11()
        if current_scale * 1.2 < 100.0:
            self.view.scale(1.2, 1.2)
            self.update_zoom_label(self.view.transform().m11())

    def zoom_out(self):
        if self.pil_image is None:
            return
        current_scale = self.view.transform().m11()
        if current_scale / 1.2 > 0.001:
            self.view.scale(1.0 / 1.2, 1.0 / 1.2)
            self.update_zoom_label(self.view.transform().m11())

    def update_zoom_icons(self):
        is_light = self.current_theme == "light"
        icon_color = QColor("#1d1d1f") if is_light else QColor("#ffffff")
        
        # Zoom In
        pixmap_in = QPixmap(32, 32)
        pixmap_in.fill(Qt.GlobalColor.transparent)
        painter_in = QPainter(pixmap_in)
        painter_in.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen_in = QPen(icon_color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter_in.setPen(pen_in)
        painter_in.drawLine(8, 16, 24, 16)
        painter_in.drawLine(16, 8, 16, 24)
        painter_in.end()
        self.btn_zoom_in.setIcon(QIcon(pixmap_in))
        self.btn_zoom_in.setIconSize(QSize(16, 16))
        self.btn_zoom_in.setText("")
        
        # Zoom Out
        pixmap_out = QPixmap(32, 32)
        pixmap_out.fill(Qt.GlobalColor.transparent)
        painter_out = QPainter(pixmap_out)
        painter_out.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen_out = QPen(icon_color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter_out.setPen(pen_out)
        painter_out.drawLine(8, 16, 24, 16)
        painter_out.end()
        self.btn_zoom_out.setIcon(QIcon(pixmap_out))
        self.btn_zoom_out.setIconSize(QSize(16, 16))
        self.btn_zoom_out.setText("")

    def export_to_pdf(self):
        if self.pil_image is None:
            return
            
        t = TRANSLATIONS[self.current_lang]
        file_path, _ = QFileDialog.getSaveFileName(
            self, t["btn_export"], "", "PDF Document (*.pdf)"
        )
        if not file_path:
            return
            
        if not file_path.lower().endswith('.pdf'):
            file_path += '.pdf'
            
        self.status_bar.showMessage(t["status_exporting"].format(name=os.path.basename(file_path)))
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        try:
            paper_w_mm, paper_h_mm = self.get_paper_size_mm()
            m_left, m_right, m_top, m_bottom = self.get_margins_mm()
            
            if self.is_pdf:
                # --- Vector PDF Lossless Crop Engine (using pypdf) ---
                from pypdf import PdfReader, PdfWriter, Transformation
                from pypdf.generic import RectangleObject
                
                reader = PdfReader(self.input_file_path)
                writer = PdfWriter()
                
                # Conversion factor from pixel to points (72 points per inch)
                pt_size = self.pdf_doc.pagePointSize(self.current_pdf_page)
                rx = pt_size.width() / self.image_width
                ry = pt_size.height() / self.image_height
                
                dpmm = 72.0 / 25.4 # points per mm
                
                paper_w_pt = paper_w_mm * dpmm
                paper_h_pt = paper_h_mm * dpmm
                
                p_left = m_left * dpmm
                p_right = m_right * dpmm
                p_top = m_top * dpmm
                p_bottom = m_bottom * dpmm
                
                printable_w = paper_w_pt - p_left - p_right
                printable_h = paper_h_pt - p_top - p_bottom
                
                if self.radio_mode_a.isChecked():
                    user_scale = self.spin_scale_pct.value() / 100.0
                    scale = 0.48 * user_scale
                    
                    scaled_w = self.image_width * scale
                    scaled_h = self.image_height * scale
                    
                    if self.chk_center_h.isChecked():
                        x = p_left + (printable_w - scaled_w) / 2
                    else:
                        x = p_left
                        
                    if self.chk_center_v.isChecked():
                        y = p_bottom + (printable_h - scaled_h) / 2
                    else:
                        y = paper_h_pt - p_top - scaled_h
                        
                    src_page = reader.pages[self.current_pdf_page]
                    blank_page = writer.add_blank_page(width=paper_w_pt, height=paper_h_pt)
                    
                    trans = Transformation().scale(scale, scale).translate(x, y)
                    blank_page.merge_transformed_page(src_page, trans)
                    
                else:
                    sorted_items = sorted(self.page_items, key=lambda x: (x.row_idx, x.col_idx))
                    
                    for item in sorted_items:
                        pos = item.pos()
                        rect = item.rect()
                        
                        px_x = pos.x()
                        px_y = pos.y()
                        px_w = rect.width()
                        px_h = rect.height()
                        
                        pdf_left = px_x * rx
                        pdf_right = (px_x + px_w) * rx
                        pdf_top = pt_size.height() - (px_y * ry)
                        pdf_bottom = pt_size.height() - ((px_y + px_h) * ry)
                        
                        orig_page = reader.pages[self.current_pdf_page]
                        src_page = orig_page.clone(writer)
                        blank_page = writer.add_blank_page(width=paper_w_pt, height=paper_h_pt)
                        
                        rect_obj = RectangleObject((pdf_left, pdf_bottom, pdf_right, pdf_top))
                        src_page.mediabox = rect_obj
                        src_page.cropbox = rect_obj
                        
                        crop_w = max(0.1, pdf_right - pdf_left)
                        crop_h = max(0.1, pdf_top - pdf_bottom)
                        
                        scale_x = printable_w / crop_w
                        scale_y = printable_h / crop_h
                        
                        trans = Transformation().translate(-pdf_left, -pdf_bottom).scale(scale_x, scale_y).translate(p_left, p_bottom)
                        blank_page.merge_transformed_page(src_page, trans)
                
                with open(file_path, "wb") as f:
                    writer.write(f)
                    
                QMessageBox.information(
                    self, t["msg_success_title"],
                    t["msg_export_success"].format(pages=len(writer.pages), path=file_path)
                )
                self.status_bar.showMessage(t["status_exported"].format(name=os.path.basename(file_path)), 5000)
                
            else:
                # --- Original Raster Image Export Engine (using Pillow) ---
                dpi = 300.0
                dpmm = dpi / 25.4
                
                paper_w_px = int(paper_w_mm * dpmm)
                paper_h_px = int(paper_h_mm * dpmm)
                
                p_left = int(m_left * dpmm)
                p_right = int(m_right * dpmm)
                p_top = int(m_top * dpmm)
                p_bottom = int(m_bottom * dpmm)
                
                printable_w = paper_w_px - p_left - p_right
                printable_h = paper_h_px - p_top - p_bottom
                
                pdf_pages = []
                
                if self.radio_mode_a.isChecked():
                    page_canvas = Image.new("RGB", (paper_w_px, paper_h_px), "white")
                    
                    dpi_100_ratio = dpi / 150.0
                    user_scale = self.spin_scale_pct.value() / 100.0
                    final_scale = dpi_100_ratio * user_scale
                    
                    scaled_w = int(self.image_width * final_scale)
                    scaled_h = int(self.image_height * final_scale)
                    
                    scaled_w = max(1, scaled_w)
                    scaled_h = max(1, scaled_h)
                    
                    resized_img = self.pil_image.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
                    
                    if self.chk_center_h.isChecked():
                        x = p_left + (printable_w - scaled_w) // 2
                    else:
                        x = p_left
                        
                    if self.chk_center_v.isChecked():
                        y = p_top + (printable_h - scaled_h) // 2
                    else:
                        y = p_top
                    
                    page_canvas.paste(resized_img, (x, y))
                    pdf_pages.append(page_canvas)
                    
                else:
                    if not self.page_items:
                        raise Exception(t["msg_no_pages_defined"])
                    
                    sorted_items = sorted(self.page_items, key=lambda x: (x.row_idx, x.col_idx))
                    
                    for item in sorted_items:
                        pos = item.pos()
                        rect = item.rect()
                        
                        x = int(pos.x())
                        y = int(pos.y())
                        w = int(rect.width())
                        h = int(rect.height())
                        
                        x = max(0, min(x, self.image_width - 1))
                        y = max(0, min(y, self.image_height - 1))
                        w = max(1, min(w, self.image_width - x))
                        h = max(1, min(h, self.image_height - y))
                        
                        crop_box = (x, y, x + w, y + h)
                        cropped = self.pil_image.crop(crop_box)
                        
                        page_canvas = Image.new("RGB", (paper_w_px, paper_h_px), "white")
                        
                        # Scale to printable width/height
                        resized_cropped = cropped.resize((printable_w, printable_h), Image.Resampling.LANCZOS)
                        
                        page_canvas.paste(resized_cropped, (p_left, p_top))
                        pdf_pages.append(page_canvas)
                
                if pdf_pages:
                    pdf_pages[0].save(
                        file_path,
                        save_all=True,
                        append_images=pdf_pages[1:],
                        resolution=dpi
                    )
                    
                    QMessageBox.information(
                        self, t["msg_success_title"],
                        t["msg_export_success"].format(pages=len(pdf_pages), path=file_path)
                    )
                    self.status_bar.showMessage(t["status_exported"].format(name=os.path.basename(file_path)), 5000)
                else:
                    raise Exception("No pages generated to export.")
                
        except Exception as e:
            QMessageBox.critical(self, t["msg_export_failed_title"], f"Failed to export PDF:\n{str(e)}")
            self.status_bar.showMessage(t["status_export_failed"])
        finally:
            QApplication.restoreOverrideCursor()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
