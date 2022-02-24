from PyQt5.Qt import *
from PyQt5 import QtWidgets,QtGui
from PyQt5.QtCore import pyqtSignal
import sys
global ConfMat
ConfMat={}
try:
    xrange(5)
except:
    xrange=range
class radioGroup(QGroupBox):

    def __init__(self):
        super(radioGroup, self).__init__()

        # Create an array of radio buttons
        moods = [QRadioButton("TP"), QRadioButton("TN"), QRadioButton("FP"),QRadioButton("FN")]
        self.currentbutton=None
        # Set a radio button to be checked by default
        # moods[0].setChecked(True)

        # Radio buttons usually are in a vertical layout
        button_layout = QHBoxLayout()

        # Create a button group for radio buttons
        self.mood_button_group = QButtonGroup()

        for i in xrange(len(moods)):
            # Add each radio button to the button layout
            button_layout.addWidget(moods[i])
            # Add each radio button to the button group & give it an ID of i
            self.mood_button_group.addButton(moods[i], i)
            # Connect each radio button to a method to run when it's clicked
            # moods[i].clicked.connect(self.radio_button_clicked)
            moods[i].toggled.connect(self.radio_button_clicked)
            moods[i].setStyleSheet("border:none")
        # Set the layout of the group box to the button layout
        self.setLayout(button_layout)
    def radio_button_clicked(self):
        # print(self.mood_button_group.checkedId())
        # print(self.mood_button_group.checkedButton().text())
        self.currentbutton=self.mood_button_group.checkedButton().text()
