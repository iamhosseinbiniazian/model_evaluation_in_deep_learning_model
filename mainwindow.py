from RadioGroup import radioGroup
from ui_mainwindow import Ui_MainWindow
from PyQt5.Qt import *
from PyQt5 import QtWidgets,QtGui
from LoadModule import import_module
import os
from worker import Worker
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5 import QtCore
import math
import io
class ImageWidget(QWidget):

    def __init__(self, imagePath, parent):
        super(ImageWidget, self).__init__(parent)
        self.picture = QtGui.QPixmap(imagePath)
        self.picture=self.picture.scaled(200,200)
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.picture)
class MainWindow(QMainWindow, Ui_MainWindow):
    sig_abort_workers = pyqtSignal()
    def __init__(self,app):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.module=None
        self.NUM_THREADS=1
        self.app=app
        self.setMenuBar(self.menubar)
        self.rButton.setEnabled(False)
        self.sButton.setEnabled(False)
        self.tables=[]
        self.allRadioButton=[]
        self.numImgPerPage=5
        # self.tableWidget.setColumnCount(3)
        self.actionModel_Directory.triggered.connect(self.Load_Model)
        self.actionImage_Directory.triggered.connect(self.Load_Image_Path)
        self.actionExit.triggered.connect(self.Exit)
        # header = self.tableWidget.horizontalHeader()
        # header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        # header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.rButton.clicked.connect(self.start_threads)
        self.sButton.clicked.connect(self.abort_workers)
        self.__workers_done = None
        self.__threads = None
        # stylesheet = "::section{Background-color:rgb(190,1,1);border-radius:14px;}"
        # self.tableWidget.verticalHeader().setStyleSheet(stylesheet)
        self.nButton.clicked.connect(self.__next_page)
        self.pButton.clicked.connect(self.__previous_page)
        self.cButton.clicked.connect(self.callConfMat)
    def start_threads(self):
        self.rButton.setDisabled(True)
        self.sButton.setEnabled(True)

        self.__workers_done = 0
        self.__threads = []
        worker = Worker(1,self.image_path,self.module,self,self.app)
        thread = QThread()
        thread.setObjectName('thread_' + str(1))
        self.__threads.append((thread, worker))  # need to store worker too otherwise will be gc'd
        worker.moveToThread(thread)
        # get progress messages from worker:
        worker.sig_done.connect(self.on_worker_done)
        worker.sig_msg.connect(self.show_Image)

        # control worker:
        self.sig_abort_workers.connect(worker.abort)

        # get read to start worker:
        # self.sig_start.connect(worker.work)  # needed due to PyCharm debugger bug (!); comment out next line
        thread.started.connect(worker.work)
        thread.start()  # this will emit 'started' and start thread's event loop
    @pyqtSlot(str, str)
    def show_Image(self,fullname:str,label:str):
        if (len(self.tables)==0)or (self.tables[-1].rowCount()==self.numImgPerPage):
            self.tables.append(self.create_new_table())
            self.stacked_widget.addWidget(self.tables[-1])
        rowPosition = self.tables[-1].rowCount()
        self.tables[-1].insertRow(rowPosition)
        image = ImageWidget(fullname, self)
        self.tables[-1].setCellWidget(rowPosition, 0, image)
        self.tables[-1].setItem(rowPosition, 1, QTableWidgetItem(label))
        r=radioGroup()
        self.allRadioButton.append(r)
        self.tables[-1].setCellWidget(rowPosition, 2,r)
        self.tables[-1].setRowHeight(rowPosition,image.picture.height())
    def __next_page(self):
        self.pButton.setDisabled(False)
        idx = self.stacked_widget.currentIndex()
        if idx < self.stacked_widget.count() - 1:
            self.stacked_widget.setCurrentIndex(idx + 1)
        if self.stacked_widget.currentIndex()==self.stacked_widget.count()-1:
            self.nButton.setDisabled(True)

    def __previous_page(self):
        self.nButton.setDisabled(False)
        idx = self.stacked_widget.currentIndex()
        if idx>0:
            self.stacked_widget.setCurrentIndex(idx -1)
        if self.stacked_widget.currentIndex()==0:
            self.pButton.setDisabled(True)

        # else:
        #     self.stacked_widget.setCurrentIndex(0)
    @pyqtSlot(int)
    def on_worker_done(self, worker_id):
        self.__workers_done += 1
        if self.__workers_done == self.NUM_THREADS:
            self.rButton.setEnabled(True)
            self.sButton.setDisabled(True)
            # self.__threads=None
        for thread, worker in self.__threads:
            thread.quit()
            thread.wait()
            thread.terminate()
    @pyqtSlot()
    def abort_workers(self):
        self.sig_abort_workers.emit()
        # print('I am at aboart Function')
        for thread, worker in self.__threads:
            thread.quit()
            thread.wait()
            thread.terminate()
        self.rButton.setEnabled(True)
        self.sButton.setDisabled(True)
    def Load_Model(self):
        filename=QtWidgets.QFileDialog.getOpenFileName(self,caption="Load Model",directory='.',
                                                       filter="All Files(*.*)")
        filename=filename[0]
        directory=filename.split('/')
        file=directory[-1]
        file=file.split('.')
        module_name=file[0]
        directory='/'.join(directory[:-1])
        self.module=import_module(directory,module_name)
    def Load_Image_Path(self):
        path=QtWidgets.QFileDialog.getExistingDirectory(self,caption="Load Image Path",directory='.')
        self.image_path=path
        self.rButton.setEnabled(True)
    def create_new_table(self):
        _translate = QtCore.QCoreApplication.translate
        tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        tableWidget.setStyleSheet("\n"
                                       "    background-color: #f0f0f0;\n"
                                       "    alternate-background-color: #e6e6e6; /* related with QListView background  */\n"
                                       "    border: 1px solid #c3c3c3; \n"
                                       "    selection-color: white;\n"
                                       "    selection-background-color: #5e90fa; /* should be similar to QListView::item selected background-color */\n"
                                       "    show-decoration-selected: 1; /* make the selection span the entire width of the view */\n"
                                       "    border-radius: 10px;\n"
                                       "")
        tableWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        tableWidget.setShowGrid(True)
        tableWidget.setObjectName("tableWidget")
        tableWidget.setColumnCount(3)
        tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        item.setFont(font)
        tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)
        tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)
        tableWidget.setHorizontalHeaderItem(2, item)
        tableWidget.horizontalHeader().setVisible(True)
        tableWidget.horizontalHeader().setCascadingSectionResizes(True)
        tableWidget.horizontalHeader().setSortIndicatorShown(False)
        tableWidget.horizontalHeader().setStretchLastSection(False)
        tableWidget.verticalHeader().setCascadingSectionResizes(True)
        tableWidget.verticalHeader().setSortIndicatorShown(False)
        tableWidget.verticalHeader().setStretchLastSection(False)
        tableWidget.setColumnCount(3)
        item = tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Image"))
        item = tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Predicted Label"))
        item = tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Metrics!?"))
        header = tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        stylesheet = "::section{Background-color:rgb(190,1,1);border-radius:14px;}"
        tableWidget.verticalHeader().setStyleSheet(stylesheet)
        return tableWidget
    def Exit(self):
        if self.__threads!=None:
            for thread, worker in self.__threads:
                del thread
                # thread.quit()
                # thread.wait()
        self.close()
    def callConfMat(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Text File(*.txt)", options=options)
        # if fileName:
        #     print(fileName)
        TP=0
        TN=0
        FP=0
        FN=0
        for r in self.allRadioButton:
            if r.currentbutton=='TP':
                TP+=1
            if r.currentbutton=='TN':
                TN+=1
            if r.currentbutton=='FP':
                FP+=1
            if r.currentbutton=='FN':
                FN+=1
        Sensitivity=(TP)/(TP+FN)
        Specificity=(TN)/(FP+TN)
        Precision=(TP)/(TP+FP)
        Negative_Predictive_Value=(TN)/(TN+FN)
        Positive_Predictive_Value=(TP)/(TP+FP)
        False_Positive_Rate=(FP)/(FP+TN)
        False_Discovery_Rate=(FP)/(FP+TP)
        False_Negative_Rate=(FN)/(FN+TP)
        Accuracy=(TP+TN)/(TP+TN+FP+FN)
        F1_Score=(2*TP)/((2*TP)+FP+FN)
        Matthews_Correlation_Coefficient=((TP*TN)-(FP*FN))/(math.sqrt((TP+FP)*(TP+FN)*(TN+FP)*(TN+FN)))
        with io.open(fileName,mode='w',encoding='utf-8') as file:
            file.write('TP=='+str(TP)+'\n')
            file.write('TN='+str(TN)+'\n')
            file.write('FP='+str(FP)+'\n')
            file.write('FN='+str(FN)+'\n')
            file.write('Sensitivity='+str(Sensitivity)+'\n')
            file.write('Specificity='+str(Specificity)+'\n')
            file.write('Precision='+str(Precision)+'\n')
            file.write('Negative_Predictive_Value='+str(Negative_Predictive_Value)+'\n')
            file.write('Positive_Predictive_Value='+str(Positive_Predictive_Value)+'\n')
            file.write('False_Positive_Rate='+str(False_Positive_Rate)+'\n')
            file.write('False_Discovery_Rate='+str(False_Discovery_Rate)+'\n')
            file.write('False_Negative_Rate='+str(False_Negative_Rate)+'\n')
            file.write('Accuracy='+str(Accuracy)+'\n')
            file.write('F1_Score='+str(F1_Score)+'\n')
            file.write('Matthews_Correlation_Coefficient='+str(Matthews_Correlation_Coefficient)+'\n')
        # print('TP=',TP)
        # print('TN=',TN)
        # print('FP=',FP)
        # print('FN=',FN)
