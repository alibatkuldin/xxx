# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.chat_history = QPushButton(self.centralwidget)
        self.chat_history.setObjectName(u"chat_history")
        self.chat_history.setGeometry(QRect(180, 200, 130, 40))
        self.call_history = QPushButton(self.centralwidget)
        self.call_history.setObjectName(u"call_history")
        self.call_history.setGeometry(QRect(180, 300, 130, 40))
        self.browser_history = QPushButton(self.centralwidget)
        self.browser_history.setObjectName(u"browser_history")
        self.browser_history.setGeometry(QRect(180, 400, 130, 40))
        self.image = QPushButton(self.centralwidget)
        self.image.setObjectName(u"image")
        self.image.setGeometry(QRect(480, 100, 130, 40))
        self.audio = QPushButton(self.centralwidget)
        self.audio.setObjectName(u"audio")
        self.audio.setGeometry(QRect(480, 200, 130, 40))
        self.text = QPushButton(self.centralwidget)
        self.text.setObjectName(u"text")
        self.text.setGeometry(QRect(480, 300, 130, 40))
        self.geolocation = QPushButton(self.centralwidget)
        self.geolocation.setObjectName(u"geolocation")
        self.geolocation.setGeometry(QRect(480, 400, 130, 40))
        self.extraction = QPushButton(self.centralwidget)
        self.extraction.setObjectName(u"extraction")
        self.extraction.setGeometry(QRect(180, 100, 130, 40))
        self.printlabel = QLabel(self.centralwidget)
        self.printlabel.setObjectName(u"printlabel")
        self.printlabel.setGeometry(QRect(190, 490, 421, 31))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 25))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.chat_history.setText(QCoreApplication.translate("MainWindow", u"Chat History", None))
        self.call_history.setText(QCoreApplication.translate("MainWindow", u"Call History", None))
        self.browser_history.setText(QCoreApplication.translate("MainWindow", u"Browser History", None))
        self.image.setText(QCoreApplication.translate("MainWindow", u"Image", None))
        self.audio.setText(QCoreApplication.translate("MainWindow", u"Audio", None))
        self.text.setText(QCoreApplication.translate("MainWindow", u"Text", None))
        self.geolocation.setText(QCoreApplication.translate("MainWindow", u"Geolocation", None))
        self.extraction.setText(QCoreApplication.translate("MainWindow", u"Extraction", None))
        self.printlabel.setText(QCoreApplication.translate("MainWindow", u"PrintLabel", None))
    # retranslateUi

