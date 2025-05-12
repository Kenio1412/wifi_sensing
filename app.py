
import sys
import os
# 添加 ui 文件所在目录到系统路径
ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
sys.path.append(ui_path)
# sys.path.append("../ui")

from ui.main import MainWindow

from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import QCoreApplication, QRect
from PySide6.QtGui import QIcon



if __name__ == "__main__":
    app = QApplication(sys.argv)

    ui = MainWindow()
    ui.show()

    sys.exit(app.exec())



