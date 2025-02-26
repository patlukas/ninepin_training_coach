import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QMessageBox,
    QMenuBar,
    QAction,
    QGridLayout
)
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QThread

from com_manager import ComManager
from lane_controller import LaneController

APP_VERSION = "1.0.2"
COM_PORT = "COM1"


class WorkerThread(QThread):
    def __init__(self, com_manager, loop_interval, after_recv_msg):
        super().__init__()
        self.__after_recv_msg = after_recv_msg
        self.__com_manager = com_manager
        self.__running = False
        self.__loop_time_interval = loop_interval

    def run(self):
        print("RUN")
        self.__running = True
        last_job_was_to_send = False
        while self.__running:
            read_bytes = self.__com_manager.read()
            if read_bytes != b"":
                for msg in read_bytes.split(b"\r"):
                    if msg != b"":
                        self.__after_recv_msg(msg)
                last_job_was_to_send = False

            if not last_job_was_to_send:
                number_sent_bytes, sent_msg = self.__com_manager.send()
                if number_sent_bytes > 0:
                    if len(sent_msg) != 7:
                        print("SENT: ", sent_msg)
                    last_job_was_to_send = True
            self.msleep(self.__loop_time_interval)

    def stop(self):
        self.__running = False


class GUI(QDialog):
    def __init__(self):
        super().__init__()
        self.__com_manager = ComManager(COM_PORT, 0.1, 0.1)
        self.__list_lane_controller = []
        self.__init_window()
        self.__layout = QGridLayout()
        self.__settings_menu = {}
        self.setLayout(self.__layout)

        self.__thread = WorkerThread(self.__com_manager, 200, self.__recv_msg)

        self.__set_layout()
        self.__init_program()
        self.__thread.start()

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
        for i in range(6):
            lane_controller = LaneController(i, self.__on_add_message_to_send)
            self.__list_lane_controller.append(lane_controller)
            self.__layout.addWidget(lane_controller.get_section(), i, 0)

    def __create_menu_bar(self):
        menu_bar = QMenuBar(self)

        settings_menu = menu_bar.addMenu("Ustawienia")
        options = [
            ["change_next_layout", "Przy zmienie ustaw next layout jako 000"],
            None,
            ["change_all_knocked_down", "Przy zmienie ustaw że zbito wszystkie kręgle"],
            ["change_no_knocked_down", "Przy zmienie ustaw że nie zbito żadego kręgle"],
            None,
            ["pick_up", "Podnoś po zmianie"],
            None,
            ["time_speed", "Szybszy czas"],
            ["time_very_speed", "Dużo szybszy czas"],
        ]
        for option in options:
            if option is None:
                settings_menu.addSeparator()
                continue
            key, name = option
            action = QAction(name, self)
            action.setCheckable(True)
            action.triggered.connect(lambda checked, k=key: self.__set_settings(k, checked))
            settings_menu.addAction(action)
            self.__settings_menu[key] = action

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

    def __on_add_message_to_send(self, message):
        self.__com_manager.add_bytes_to_send(message + self.__calculate_control_sum(message) + b"\r")

    @staticmethod
    def __calculate_control_sum(message):
        sum_ascii = 0
        for x in message:
            sum_ascii += x
        checksum = bytes(hex(sum_ascii).split("x")[-1].upper()[-2:], 'utf-8')
        return checksum

    def __recv_msg(self, msg):
        lane_index = int(msg[3:4])
        if lane_index < len(self.__list_lane_controller):
            self.__list_lane_controller[lane_index].on_recv_message(msg)

    def __set_settings(self, name, value):
        related_options = [
            ["change_all_knocked_down", "change_no_knocked_down"], ["change_no_knocked_down", "change_all_knocked_down"],
            ["time_speed", "time_very_speed"], ["time_very_speed", "time_speed"]
        ]
        for option_a, option_b in related_options:
            if name == option_a and value and option_b in self.__settings_menu:
                if self.__settings_menu[option_b].isChecked():
                    self.__set_settings(option_b, False)
                    self.__settings_menu[option_b].setChecked(False)
        for lane_controller in self.__list_lane_controller:
            lane_controller.set_settings(name, value)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GUI()
    ex.show()
    sys.exit(app.exec_())
