from ui.sub_ui import Ui_Sub

from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import QCoreApplication, QRect


class SubWindow(QDialog, Ui_Sub):
    def __init__(self):
        super(SubWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Raspberry Pi Data Collector - Sub Window")
        # self.setWindowIcon(QIcon("icon.png"))  # 设置窗口图标
        self.back_Button.clicked.connect(self.back_button_clicked)
    
    def back_button_clicked(self):
        self.close()