from UI.main_ui import Ui_main
from UI.sub import SubWindow

from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import QCoreApplication, QRect

import config


class MainWindow(QDialog,Ui_main):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Raspberry Pi Data Collector")
        self.action_Button.clicked.connect(self.action_button_clicked)
        
    
    def action_button_clicked(self):
        dataIP = self.dataIP_Line.text()
        if dataIP != "":
            config.raspberry_pi_ip = dataIP

        dataPass = self.dataPass_Line.text()
        if dataPass != "":
            config.raspberry_pi_password = dataPass
        
        csiIP = self.csiIP_Line.text()
        """
        TODO: 这里需要添加CSI的IP地址和密码
        """
        csiPass = self.csiPass_Line.text()
        # print(f"Data IP: {dataIP}")
        # print(f"Data Password: {dataPass}")
        # print(f"CSI IP: {csiIP}")
        # print(f"CSI Password: {csiPass}")

        # 打开子窗口
        self.sub_window = SubWindow()
        # self.sub_window.text_Browser.append(f"Data IP: {dataIP}")
        # self.sub_window.text_Browser.append(f"Data Password: {dataPass}")
        # self.sub_window.text_Browser.append(f"CSI IP: {csiIP}")
        # self.sub_window.text_Browser.append(f"CSI Password: {csiPass}")
        self.sub_window.show()