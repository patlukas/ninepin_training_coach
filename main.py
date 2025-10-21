import sys
import os
import time

from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QMessageBox,
    QMenuBar,
    QAction,
    QGridLayout, QLabel
)
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QThread, Qt

from com_manager import ComManager, ComManagerError
from config_reader import ConfigReader, ConfigReaderError
from gui.log_table import LogTable
from lane_controller import LaneController
from log_management import LogManagement

APP_NAME = "NTC"
EXE_NAME = "TK"
APP_VERSION = "1.0.12"


class WorkerThread(QThread):
    def __init__(self, com_manager, loop_interval, after_recv_msg, max_time_between_next_send, add_log):
        super().__init__()
        self.__after_recv_msg = after_recv_msg
        self.__com_manager = com_manager
        self.__running = False
        self.__loop_time_interval = loop_interval
        self.__max_time_between_next_send = max_time_between_next_send
        self.__add_log = add_log

    def run(self):
        self.__add_log(5, "RUN", "")
        self.__running = True
        time_next_send = 0
        while self.__running:
            read_bytes = self.__com_manager.read()
            if read_bytes != b"":
                for msg in read_bytes.split(b"\r"):
                    if msg != b"":
                        self.__add_log(2, "RECV", msg)
                        self.__after_recv_msg(msg)
                time_next_send = 0
            if time.time() > time_next_send:
                number_sent_bytes, sent_msg = self.__com_manager.send()
                if number_sent_bytes > 0:
                    self.__add_log(2, "SEND", sent_msg)
                    time_next_send = time.time() + self.__max_time_between_next_send
            self.msleep(int(self.__loop_time_interval*1000))

    def stop(self):
        self.__running = False


class GUI(QDialog):
    def __init__(self):
        super().__init__()
        self.__log_management = LogManagement()
        self.__settings_menu = {}
        self.__list_lane_controller = []

        self.__init_window()
        self.__init_program()
        self.__layout = QGridLayout()
        self.setLayout(self.__layout)
        try:
            self.__config = ConfigReader().get_configuration()
            self.__com_manager = ComManager(self.__config["com_port"], self.__config["com_timeout"], self.__config["com_write_timeout"], self.__log_management.add_log)
            self.__log_table = LogTable(self.__log_management)
            self.__set_layout()

            self.__thread = WorkerThread(self.__com_manager, self.__config["loop_com_communication_break"], self.__recv_msg, self.__config["max_time_between_next_send"], self.__log_management.add_log)
            self.__thread.start()
        except ComManagerError as e:
            self.__set_error_layout("Problem z utworzneiem portu szeregowego", e.code, e.message)
        except ConfigReaderError as e:
            self.__set_error_layout("Problem z odczytaniem konfiguracji", e.code, e.message)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.__com_manager.close()
        event.accept()

    def __init_window(self) -> None:
        self.setWindowTitle("Trener Kręglarski")
        self.setWindowIcon(QtGui.QIcon('icon/icon.ico'))
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.move(300, 50)
        self.layout()

    def __init_program(self) -> None:
        self.__set_working_directory()

    def __set_error_layout(self, name, error_code, error_msg) -> None:
        head_label = QLabel("Błąd krytyczny")
        head_label.setAlignment(Qt.AlignCenter)
        head_label.setStyleSheet("font-size: 30px; color: red; margin-bottom: 25px")
        self.__layout.addWidget(head_label, 0, 0)

        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-size: 20px;  margin-bottom: 10px")
        self.__layout.addWidget(name_label, 1, 0)

        msg_label = QLabel(error_code + ": " + error_msg)
        msg_label.setWordWrap(True)
        self.__layout.addWidget(msg_label, 2, 0)

    def __set_layout(self) -> None:
        for i in range(self.__config["number_of_lane"]):
            lane_controller = LaneController(i, self.__on_add_message_to_send, self.__log_management.add_log)
            self.__list_lane_controller.append(lane_controller)
            self.__layout.addWidget(lane_controller.get_section(), i, 0)
        self.__layout.setMenuBar(self.__create_menu_bar())
        self.__layout.addWidget(self.__log_table, 0, 1, self.__config["number_of_lane"], 1)

    def __create_menu_bar(self):
        menu_bar = QMenuBar(self)

        view_menu = menu_bar.addMenu("Widok")
        options = [
            ["Pokaż logi", True, lambda checked: self.__set_visible_log_table(checked)],
            ["Pokaż przycisk uruchamiana próbnych", True, lambda checked: self.__set_visible_trial_button(checked)],
        ]
        for name, checkable, func in options:
            action = QAction(name, self)
            action.setCheckable(checkable)
            action.triggered.connect(func)
            view_menu.addAction(action)

        settings_menu = menu_bar.addMenu("Ustawienia")
        options = [
            [
                "Przy zmianie: następny układ",
                [
                    ["change_next_layout=no", "Nie zmieniaj"],
                    ["change_next_layout=000", "Ustaw jako 000", True],
                    ["change_next_layout=001", "Ustaw jako 001"],
                ],
                "change_next_layout="
            ],
            [
                "Przy zmienie: zbite",
                [
                    ["change_knocked_down=no", "Nie zmieniaj", True],
                    ["change_knocked_down=all", "Ustaw że zbito wszystkie kręgle"],
                    ["change_knocked_down=null", "Ustaw że nie zbito żadego kręgle"],
                    ["change_knocked_down=001", "Ustaw że zbito układ 001"],
                ],
                "change_knocked_down="
            ],
            [
                "Przy zmianie: dodaj liczbę usuwanych kręgli",
                [
                    ["add_removed_pins=no", "Nie", True],
                    ["add_removed_pins=yes", "Tak"],
                ],
                "add_removed_pins="
            ],
            None,
            [
                "Przyśpieszony zegar",
                [
                    ["time_speed=normal", "Nie", True],
                    ["time_speed=fast", "Szybszy czas [0.1]"],
                    ["time_speed=very_fast", "Dużo szybszy czas [1.0]"],
                    ["time_speed=extreme", "Ekstremalnie szybki czas [5.0]"],
                ],
                "time_speed="
            ],
            None,
            [
                "Próbne",
                [
                    ["trial=0", "Bez zmian", True],
                    ["trial=1", "Podnieś"],
                    ["trial=2", "Podnieś i zatrzymaj"],
                ],
                "trial="
            ],
            None,
            [
                "Czas przewy miedzy wiadomościami",
                [
                    ["time_wait=0.05", "0.05s"],
                    ["time_wait=0.1", "0.1s"],
                    ["time_wait=0.2", "0.2s"],
                    ["time_wait=0.3", "0.3s", True],
                    ["time_wait=0.5", "0.5s"],
                    ["time_wait=0.75", "0.75s"],
                    ["time_wait=1.5", "1.5s"],
                    ["time_wait=3.0", "3.0s"],
                    ["time_wait=5.0", "5.0s"],
                ],
                "time_wait="
            ],
            None,
            [
                "Tryb ustawiania pełnego układu",
                [
                    ["mode=1", "Tryb 1", True],
                    ["mode=2", "Tryb 2"],
                    ["mode=3", "Tryb 3"],
                    ["mode=4", "Tryb 4"],
                    ["mode=5", "Tryb 5"],
                    ["mode=6", "Tryb 6"],
                    ["mode=7", "Tryb 7"],
                    ["mode=8", "Tryb 8"],
                    ["mode=9", "Tryb 9"],
                    ["mode=10", "Tryb 10"],
                    ["mode=11", "Tryb 11"],
                    ["mode=12", "Tryb 12"],
                    ["mode=13", "Tryb 13"],
                    ["mode=14", "Tryb 14"],
                    ["mode=15", "Tryb 15"],
                    ["mode=16", "Tryb 16"],
                    ["mode=17", "Tryb 17"],
                    ["mode=18", "Tryb 18"],
                    ["mode=19", "Tryb 19"],
                    ["mode=20", "Tryb 20"],
                    ["mode=21", "Tryb 21"],
                    ["mode=22", "Tryb 22"]
                ],
                "mode="
            ]
        ]
        self.__add_option_to_menubar(settings_menu, options)

        help_menu = menu_bar.addMenu("Pomoc")
        about_action = QAction("O aplikacji", self)
        about_action.triggered.connect(self.__show_about)
        help_menu.addAction(about_action)

        return menu_bar

    def __add_option_to_menubar(self, menubar, options):
        for option in options:
            if option is None:
                menubar.addSeparator()
                continue
            if type(option[1]) == list:
                menubar_child = menubar.addMenu(option[0] + " | ")
                self.__settings_menu[option[2]] = menubar_child
                self.__add_option_to_menubar(menubar_child, option[1])
                continue
            key = option[0]
            name = option[1]
            default = False if len(option) < 3 else option[2]
            action = QAction(name, self)
            action.setCheckable(True)
            action.setChecked(default)
            action.triggered.connect(lambda checked, k=key: self.__set_settings(k, checked))
            menubar.addAction(action)
            self.__settings_menu[key] = action
            if default:
                self.__set_settings(key, True)

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

    def __on_add_message_to_send(self, message, priority=5):
        self.__log_management.add_log(priority, "ADD MSG", message)
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

    def __set_settings(self, name, value, nested=False):
        list_related_options = [
            ["change_next_layout=", ["no", "000", "001"], True],
            ["change_knocked_down=", ["no", "all", "null", "001"], True],
            ["add_removed_pins=", ["no", "yes"], True],
            ["time_speed=", ["normal", "fast", "very_fast", "extreme"], True],
            ["trial=", ["0", "1", "2"], True],
            ["time_wait=", ["0.05", "0.1", "0.2", "0.3", "0.5", "0.75", "1.5", "3.0", "5.0"], True],
            ["mode=", ["1", "2", "3", "4", "5", "6", "7", "8", "9"], True]
        ]

        list_option_to_enable = []

        for prefix, list_name, disable_uncheck in list_related_options:
            related_options = [prefix + name_body for name_body in list_name]
            if name not in related_options:
                continue
            if disable_uncheck and not nested and not value:
                list_option_to_enable.append(name)
                break
            for option in related_options:
                if option != name and option in self.__settings_menu:
                    if self.__settings_menu[option].isChecked():
                        if value:
                            self.__set_settings(option, False, True)
                            self.__settings_menu[option].setChecked(False)
            if value and prefix in self.__settings_menu:
                parent_title = self.__settings_menu[prefix].title()
                parent_title = "|".join(parent_title.split("|")[:-1]) + "| " + self.__settings_menu[name].text()
                self.__settings_menu[prefix].setTitle(parent_title)

        status = "enabled" if value else "disabled"
        self.__log_management.add_log(5, "SETTINGS", "\"" + name + "\" is " + status)
        for lane_controller in self.__list_lane_controller:
            lane_controller.set_settings(name, value)

        for option in list_option_to_enable:
            self.__set_settings(option, True)
            self.__settings_menu[option].setChecked(True)

    def __set_visible_log_table(self, show):
        self.__log_table.set_visibility(show)
        self.adjustSize()

    def __set_visible_trial_button(self, show):
        for lane_controller in self.__list_lane_controller:
            lane_controller.set_visible_trial_button(show)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GUI()
    ex.show()
    sys.exit(app.exec_())
