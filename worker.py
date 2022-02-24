import os
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
import sys
def trap_exc_during_debug(*args):
    # when app raises uncaught exception, print info
    print(args)


# install exception hook: without this, uncaught exception would cause application to exit
sys.excepthook = trap_exc_during_debug
class Worker(QObject):
    """
    Must derive from QObject in order to emit signals, connect slots to other signals, and operate in a QThread.
    """
    sig_done = pyqtSignal(int)  # worker id: emitted at end of work()
    sig_msg = pyqtSignal(str,str)  # message to be shown to user

    def __init__(self, id: int,path:str,model,root,app):
        super().__init__()
        self.__id = id
        self.__abort = False
        self.__path=path
        self.__model=model
        self.root=root
        self.app=app

    @pyqtSlot()
    def work(self):
        if self.__model!=None:
            for root, dirs, files in os.walk(self.__path):
                for file in files:
                    fullname = root + '/' + file
                    # print(fullname)
                    self.app.processEvents()
                    predict_label=self.__model.main(fullname)
                    self.sig_msg.emit(fullname, predict_label)
                    if self.__abort:
                        break
                if self.__abort:
                    break
        else:
            QtWidgets.QMessageBox.information(self.root, 'Information', 'Please Load Your Model')
        self.sig_done.emit(self.__id)

    def abort(self):
        # print("I am at worker abaort")
        self.__abort = True