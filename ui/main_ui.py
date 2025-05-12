# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QWidget)

class Ui_main(object):
    def setupUi(self, main):
        if not main.objectName():
            main.setObjectName(u"main")
        main.resize(475, 587)
        self.setting_Button = QPushButton(main)
        self.setting_Button.setObjectName(u"setting_Button")
        self.setting_Button.setGeometry(QRect(350, 430, 75, 23))
        self.dataIP_Label = QLabel(main)
        self.dataIP_Label.setObjectName(u"dataIP_Label")
        self.dataIP_Label.setGeometry(QRect(70, 130, 101, 16))
        self.dataPass_label = QLabel(main)
        self.dataPass_label.setObjectName(u"dataPass_label")
        self.dataPass_label.setGeometry(QRect(70, 170, 71, 16))
        self.csiIP_Label = QLabel(main)
        self.csiIP_Label.setObjectName(u"csiIP_Label")
        self.csiIP_Label.setGeometry(QRect(70, 220, 101, 16))
        self.csiPass_IP = QLabel(main)
        self.csiPass_IP.setObjectName(u"csiPass_IP")
        self.csiPass_IP.setGeometry(QRect(70, 280, 61, 16))
        self.dataIP_Line = QLineEdit(main)
        self.dataIP_Line.setObjectName(u"dataIP_Line")
        self.dataIP_Line.setGeometry(QRect(220, 120, 151, 31))
        self.dataPass_Line = QLineEdit(main)
        self.dataPass_Line.setObjectName(u"dataPass_Line")
        self.dataPass_Line.setGeometry(QRect(220, 170, 151, 31))
        self.dataPass_Line.setEchoMode(QLineEdit.EchoMode.Password)
        self.csiIP_Line = QLineEdit(main)
        self.csiIP_Line.setObjectName(u"csiIP_Line")
        self.csiIP_Line.setGeometry(QRect(220, 210, 151, 31))
        self.csiPass_Line = QLineEdit(main)
        self.csiPass_Line.setObjectName(u"csiPass_Line")
        self.csiPass_Line.setGeometry(QRect(220, 260, 151, 31))
        self.csiPass_Line.setEchoMode(QLineEdit.EchoMode.Password)
        self.action_Button = QPushButton(main)
        self.action_Button.setObjectName(u"action_Button")
        self.action_Button.setGeometry(QRect(180, 410, 75, 23))

        self.retranslateUi(main)

        QMetaObject.connectSlotsByName(main)
    # setupUi

    def retranslateUi(self, main):
        main.setWindowTitle(QCoreApplication.translate("main", u"Dialog", None))
        self.setting_Button.setText(QCoreApplication.translate("main", u"setting", None))
        self.dataIP_Label.setText(QCoreApplication.translate("main", u"rasberry_data", None))
        self.dataPass_label.setText(QCoreApplication.translate("main", u"password", None))
        self.csiIP_Label.setText(QCoreApplication.translate("main", u"raspberry_csi", None))
        self.csiPass_IP.setText(QCoreApplication.translate("main", u"password", None))
        self.action_Button.setText(QCoreApplication.translate("main", u"action", None))
    # retranslateUi

