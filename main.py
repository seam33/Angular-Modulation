try:
    import sys
    from controller import Controller as cn
    from PyQt5 import QtWidgets
except ModuleNotFoundError:
    print("Module not Found")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    GUI = cn()
    GUI.show()
    sys.exit(app.exec())