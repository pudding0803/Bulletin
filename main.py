from PyQt5 import QtWidgets

from WindowController import WindowController

if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = WindowController()
    window.show()
    sys.exit(app.exec_())
