# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QIcon

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1215, 853)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.cmBox_RoutingName = QtWidgets.QComboBox(self.centralWidget)
        self.cmBox_RoutingName.setGeometry(QtCore.QRect(290, 120, 311, 25))
        self.cmBox_RoutingName.setObjectName("cmBox_RoutingName")
        self.lnEdit_Prog = QtWidgets.QLineEdit(self.centralWidget)
        self.lnEdit_Prog.setGeometry(QtCore.QRect(140, 30, 711, 25))
        self.lnEdit_Prog.setObjectName("lnEdit_Prog")
        self.pBtn_file = QtWidgets.QPushButton(self.centralWidget)
        self.pBtn_file.setGeometry(QtCore.QRect(850, 30, 61, 25))
        self.pBtn_file.setObjectName("pBtn_file")
        self.label = QtWidgets.QLabel(self.centralWidget)
        self.label.setGeometry(QtCore.QRect(40, 30, 101, 21))
        self.label.setObjectName("label")
        self.graphicsView = QtWidgets.QGraphicsView(self.centralWidget)
        self.graphicsView.setGeometry(QtCore.QRect(140, 430, 781, 192))
        self.graphicsView.setObjectName("graphicsView")
        self.lcdNumber = QtWidgets.QLCDNumber(self.centralWidget)
        self.lcdNumber.setGeometry(QtCore.QRect(1090, 110, 71, 61))
        font = QtGui.QFont()
        font.setPointSize(50)
        self.lcdNumber.setFont(font)
        self.lcdNumber.setProperty("intValue", 2)
        self.lcdNumber.setObjectName("lcdNumber")
        self.spinBox_jobCount = QtWidgets.QSpinBox(self.centralWidget)
        self.spinBox_jobCount.setGeometry(QtCore.QRect(140, 210, 151, 21))
        self.spinBox_jobCount.setObjectName("spinBox_jobCount")
        self.listWidget_activeProg = QtWidgets.QListWidget(self.centralWidget)
        self.listWidget_activeProg.setGeometry(QtCore.QRect(140, 260, 341, 131))
        self.listWidget_activeProg.setObjectName("listWidget_activeProg")
        self.label_2 = QtWidgets.QLabel(self.centralWidget)
        self.label_2.setGeometry(QtCore.QRect(140, 70, 191, 21))
        self.label_2.setObjectName("label_2")
        self.lnEdit_loadStart = QtWidgets.QLineEdit(self.centralWidget)
        self.lnEdit_loadStart.setGeometry(QtCore.QRect(330, 70, 121, 25))
        self.lnEdit_loadStart.setObjectName("lnEdit_loadStart")
        self.label_3 = QtWidgets.QLabel(self.centralWidget)
        self.label_3.setGeometry(QtCore.QRect(460, 70, 21, 21))
        self.label_3.setObjectName("label_3")
        self.lnEdit_loadEnd = QtWidgets.QLineEdit(self.centralWidget)
        self.lnEdit_loadEnd.setGeometry(QtCore.QRect(490, 70, 121, 25))
        self.lnEdit_loadEnd.setObjectName("lnEdit_loadEnd")
        self.lnEdit_loadStep = QtWidgets.QLineEdit(self.centralWidget)
        self.lnEdit_loadStep.setGeometry(QtCore.QRect(660, 70, 121, 25))
        self.lnEdit_loadStep.setObjectName("lnEdit_loadStep")
        self.label_4 = QtWidgets.QLabel(self.centralWidget)
        self.label_4.setGeometry(QtCore.QRect(620, 70, 41, 21))
        self.label_4.setObjectName("label_4")
        self.cmBox_SimulationSpan = QtWidgets.QComboBox(self.centralWidget)
        self.cmBox_SimulationSpan.setGeometry(QtCore.QRect(290, 170, 311, 25))
        self.cmBox_SimulationSpan.setObjectName("cmBox_SimulationSpan")
        self.label_5 = QtWidgets.QLabel(self.centralWidget)
        self.label_5.setGeometry(QtCore.QRect(140, 120, 191, 21))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.centralWidget)
        self.label_6.setGeometry(QtCore.QRect(140, 170, 191, 21))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.centralWidget)
        self.label_7.setGeometry(QtCore.QRect(40, 210, 101, 21))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.centralWidget)
        self.label_8.setGeometry(QtCore.QRect(920, 110, 161, 51))
        font = QtGui.QFont()
        font.setPointSize(28)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.centralWidget)
        self.label_9.setGeometry(QtCore.QRect(40, 260, 101, 21))
        self.label_9.setObjectName("label_9")
        self.pBtn_Run = QtWidgets.QPushButton(self.centralWidget)
        self.pBtn_Run.setGeometry(QtCore.QRect(40, 710, 131, 51))
        font = QtGui.QFont()
        font.setPointSize(22)
        self.pBtn_Run.setFont(font)
        self.pBtn_Run.setObjectName("pBtn_Run")
        MainWindow.setCentralWidget(self.centralWidget)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1215, 28))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        #2017-10-10 ZhangYu
        self.pBtn_Run.clicked.connect(self.pBtn_RunClicked)
        self.pBtn_file.clicked.connect(self.pBtn_fileClicked)
    def pBtn_fileClicked(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName,_ = QFileDialog.getOpenFileName(None, '', '/Users/zhangyu/ndnSIM20170130/ns-3/src/ndnSIM/examples/', 'All Files (*);;Python Files (*.py)', '', options)
        if fileName:
                self.lnEdit_Prog.setText(fileName)          
    def pBtn_RunClicked(self):
        self.listWidget_activeProg.addItem('item1')

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ndnSIM Simulation Main Controller-----2017-10-8"))
        self.pBtn_file.setText(_translate("MainWindow", "浏览..."))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p>仿真执行程序:</p></body></html>"))
        self.label_2.setText(_translate("MainWindow", "<html><head/><body><p>InterestsPerSec---------From:</p></body></html>"))
        self.label_3.setText(_translate("MainWindow", "<html><head/><body><p>To:</p></body></html>"))
        self.label_4.setText(_translate("MainWindow", "<html><head/><body><p>Step:</p></body></html>"))
        self.label_5.setText(_translate("MainWindow", "<html><head/><body><p>RoutingName:</p></body></html>"))
        self.label_6.setText(_translate("MainWindow", "<html><head/><body><p>SimulationSpan:</p></body></html>"))
        self.label_7.setText(_translate("MainWindow", "<html><head/><body><p>进程数量:</p></body></html>"))
        self.label_8.setText(_translate("MainWindow", "<html><head/><body><p>CPU占用:</p></body></html>"))
        self.label_9.setText(_translate("MainWindow", "<html><head/><body><p>当前运行进程：</p></body></html>"))
        self.pBtn_Run.setText(_translate("MainWindow", "开始仿真"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

