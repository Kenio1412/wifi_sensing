# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sub.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QPushButton, QSizePolicy,
    QTextBrowser, QWidget)

class Ui_Sub(object):
    def setupUi(self, Sub):
        if not Sub.objectName():
            Sub.setObjectName(u"Sub")
        Sub.resize(400, 300)
        self.back_Button = QPushButton(Sub)
        self.back_Button.setObjectName(u"back_Button")
        self.back_Button.setGeometry(QRect(160, 240, 75, 24))
        self.text_Browser = QTextBrowser(Sub)
        self.text_Browser.setObjectName(u"text_Browser")
        self.text_Browser.setGeometry(QRect(60, 20, 256, 192))

        self.retranslateUi(Sub)

        QMetaObject.connectSlotsByName(Sub)
    # setupUi

    def retranslateUi(self, Sub):
        Sub.setWindowTitle(QCoreApplication.translate("Sub", u"Dialog", None))
        self.back_Button.setText(QCoreApplication.translate("Sub", u"\u8fd4\u56de", None))
    # retranslateUi

