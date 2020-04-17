try:
    from PyQt5 import uic
    from PyQt5 import QtGui, QtWidgets
except ModuleNotFoundError:
    print("Module Not Found")

class Controller(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi("GUI.ui",self)