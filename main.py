import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PDFViewer import PDFViewer


def main():
    app = QApplication(sys.argv)
    # app.setWindowIcon(QIcon("resources/icons/x64.ico"))
    app.setStyleSheet("background-color: #ADA996")
    pdf = PDFViewer()
    pdf.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
