
import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QWidget,
    QGroupBox,
    QLabel,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QComboBox,
    QMenuBar,
    QAction,
    QHeaderView,
    QMenu, QGridLayout
)
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QTimer, Qt
from _thread import start_new_thread

APP_VERSION = "1.0.0"


class GUI(QDialog):
    def __init__(self):
        super().__init__()
        self.__init_window()
        self.__layout = QGridLayout()
        self.setLayout(self.__layout)

        self.__set_layout()
        self.__init_program()

    @staticmethod
    def closeEvent(event: QtGui.QCloseEvent) -> None:
        event.accept()

    def __init_window(self) -> None:
        self.setWindowTitle("Trener Kręglarski")
        self.setWindowIcon(QtGui.QIcon('icon/icon.ico'))
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setMinimumWidth(570)
        self.setMinimumHeight(300)
        self.move(300, 50)
        self.layout()

    def __init_program(self) -> None:
        self.__set_working_directory()

    def __set_layout(self) -> None:
        self.__layout.setMenuBar(self.__create_menu_bar())


    def __create_menu_bar(self):
        menu_bar = QMenuBar(self)

        help_menu = menu_bar.addMenu("Pomoc")
        about_action = QAction("O aplikacji", self)
        about_action.triggered.connect(self.__show_about)
        help_menu.addAction(about_action)

        return menu_bar

    def __show_about(self):
        about_text = (
                "<h3>Trener kręglarski - asystent treningu</h3>"
                "<p>Wersja: {}</p>".format(APP_VERSION) +
                "<p>Aplikacja wykonana w PyQt5.</p>"
        )
        QMessageBox.information(self, "O aplikacji", about_text)

    @staticmethod
    def __set_working_directory() -> None:
        """
        Set the working directory to the directory where the executable or script is located.
        """
        if hasattr(sys, 'frozen'):
            exe_directory = os.path.dirname(sys.executable)
        else:
            exe_directory = os.path.dirname(os.path.abspath(__file__))
        os.chdir(exe_directory)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GUI()
    ex.show()
    sys.exit(app.exec_())
