import sys
from PyQt5.QtWidgets import QWidget, QFileDialog, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QMessageBox, \
    QSpacerItem, QScrollArea
from PyQt5.QtGui import QPixmap, QImage, QCursor
from PyQt5.QtCore import Qt
import fitz


class PDFViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF 阅读器")
        self.setGeometry(100, 100, 800, 600)

        # 创建布局
        self.layout = QVBoxLayout(self)

        # 创建导航栏布局
        self.navigator_widget = QWidget(self)
        self.navigator_widget.setMaximumHeight(60)
        self.navigator_widget.setStyleSheet("background-color: #F2F2F2")
        self.navigator_layout = QHBoxLayout(self.navigator_widget)
        self.file_name_lbl = QLabel(self.navigator_widget)
        self.open_btn = QPushButton("打开", self.navigator_widget)
        self.open_btn.clicked.connect(self.open_pdf)
        self.prev_btn = QPushButton("上一页", self.navigator_widget)
        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn = QPushButton("下一页", self.navigator_widget)
        self.next_btn.clicked.connect(self.next_page)
        self.page_ipt = QLineEdit(self.navigator_widget)
        self.page_ipt.setPlaceholderText("输入页码")
        self.page_separator_lbl = QLabel(self.navigator_widget)
        self.page_separator_lbl.setText("/")
        self.page_max_lbl = QLabel(self.navigator_widget)
        self.page_max_lbl.setText("0")
        self.go_btn = QPushButton("跳转", self.navigator_widget)
        self.go_btn.clicked.connect(self.go_to_page)
        self.zoom_in_btn = QPushButton("放大", self.navigator_widget)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_ipt = QLineEdit(self.navigator_widget)
        self.zoom_ipt.setText("100%")
        self.zoom_ipt.setEnabled(False)
        self.zoom_out_btn = QPushButton("缩小", self.navigator_widget)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.close_btn = QPushButton("关闭", self.navigator_widget)
        self.close_btn.clicked.connect(self.close_pdf)

        self.navigator_layout.addWidget(self.file_name_lbl)
        self.navigator_layout.addWidget(self.open_btn)
        self.navigator_layout.addWidget(self.prev_btn)
        self.navigator_layout.addWidget(self.next_btn)
        self.navigator_layout.addWidget(self.page_ipt)
        self.navigator_layout.addWidget(self.page_separator_lbl)
        self.navigator_layout.addWidget(self.page_max_lbl)
        self.navigator_layout.addWidget(self.go_btn)
        self.navigator_layout.addWidget(self.zoom_in_btn)
        self.navigator_layout.addWidget(self.zoom_ipt)
        self.navigator_layout.addWidget(self.zoom_out_btn)
        self.navigator_layout.addWidget(self.close_btn)
        self.layout.addWidget(self.navigator_widget)

        # 创建一个 QScrollArea 并设置其背景为透明
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: rgba(125, 0, 0, 1);")

        # 创建页面布局
        self.viewer_widget = QWidget(self.scroll_area)
        self.viewer_widget.setMouseTracking(True)
        self.viewer_widget.setStyleSheet("background-color: #DBDBDB")
        self.viewer_layout = QVBoxLayout(self.viewer_widget)
        self.page_lbl = QLabel(self.viewer_widget)
        self.page_lbl.setAlignment(Qt.AlignCenter)
        self.viewer_layout.addWidget(self.page_lbl)

        # 将滚动内容设置为滚动区域的窗口部件
        self.scroll_area.setWidget(self.viewer_widget)
        # 将滚动区域添加到布局中
        self.layout.addWidget(self.scroll_area)

        # 文件参数
        self.doc = None
        self.current_page = 0

        # 拖动相关变量
        self.last_mouse_position = None
        self.page_pixmap = None

        # 鼠标事件
        self.page_lbl.mousePressEvent = self.mouse_press
        self.page_lbl.mouseMoveEvent = self.mouse_move
        self.page_lbl.mouseReleaseEvent = self.mouse_release

        # 缩放参数
        self.zoom_factor = 100

    def open_pdf(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "打开 PDF 文件", "", "PDF 文件 (*.pdf);;所有文件 (*)", options=options)

        if file_name:
            self.load_pdf(file_name)

    def load_pdf(self, file_name):
        # 加载PDF文件
        self.doc = fitz.open(file_name)
        self.current_page = 0
        self.file_name_lbl.setText(self.doc.name.split("/")[-1])
        self.page_ipt.setText(str(self.current_page + 1))
        self.page_max_lbl.setText(str(len(self.doc)))
        self.render_page()

    def render_page(self):
        if self.doc and 0 <= self.current_page < len(self.doc):
            page = self.doc[self.current_page]
            pix = page.get_pixmap(matrix=fitz.Matrix(self.zoom_factor / 100, self.zoom_factor / 100))
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(img)
            self.page_lbl.setPixmap(pixmap)
            # self.center_page()
            self.setWindowTitle(f"PDF 阅读器 - 第 {self.current_page + 1} 页")

    def center_page(self):
        # 居中页面
        self.page_lbl.setAlignment(Qt.AlignCenter)
        self.page_lbl.resize(self.page_lbl.pixmap().size())

    def prev_page(self):
        if self.doc and self.current_page > 0:
            self.current_page -= 1
            self.page_ipt.setText(str(self.current_page + 1))
            self.render_page()

    def next_page(self):
        if self.doc and self.current_page <len(self.doc) - 1:
            self.current_page += 1
            self.page_ipt.setText(str(self.current_page + 1))
            self.render_page()

    def go_to_page(self):
        if self.doc:
            try:
                page_number = int(self.page_ipt.text()) - 1
                if 0 <= page_number < len(self.doc):
                    self.current_page = page_number
                    self.render_page()
                else:
                    QMessageBox.warning(self, "警告", f"请输入有效页码（1 - {len(self.doc)}）")
            except ValueError:
                QMessageBox.warning(self, "警告", "请输入有效的数字页码")

    def zoom_in(self):
        if self.doc:
            self.zoom_factor += 10
            self.zoom_ipt.setText(f"{self.zoom_factor}%")
            self.render_page()

    def zoom_out(self):
        if self.doc:
            self.zoom_factor -= 10
            self.zoom_factor = max(10, self.zoom_factor)
            self.zoom_ipt.setText(f"{self.zoom_factor}%")
            self.render_page()

    def close_pdf(self):
        if self.doc:
            self.doc.close()
            self.doc = None
            self.file_name_lbl.clear()
            self.page_lbl.clear()
            self.page_max_lbl.setText("0")

    def mouse_press(self, event):
        if not self.scroll_area.verticalScrollBar().isVisible() and not self.scroll_area.horizontalScrollBar().isVisible():
            return
            # 鼠标左键按下时记录鼠标位置
        self.last_mouse_position = event.globalPos()

    def mouse_move(self, event):
        if self.last_mouse_position is not None:
            # 计算移动的距离
            delta = event.globalPos() - self.last_mouse_position
            self.page_lbl.move(self.page_lbl.x() + delta.x(), self.page_lbl.y() + delta.y())
            self.last_mouse_position = event.globalPos()

    def mouse_release(self, event):
        self.last_mouse_position = None





