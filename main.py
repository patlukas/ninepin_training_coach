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
APP_VERSION = "1.0.10"


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
            lane_controller = LaneController(i, self.__on_add_message_to_send, self.__config["break_between_recv_msg_and_send_ping_to_lane"], self.__log_management.add_log)
            self.__list_lane_controller.append(lane_controller)
            self.__layout.addWidget(lane_controller.get_section(), i, 0)
        self.__layout.setMenuBar(self.__create_menu_bar())
        self.__layout.addWidget(self.__log_table, 0, 1, self.__config["number_of_lane"], 1)

    def __create_menu_bar(self):
        menu_bar = QMenuBar(self)

        view_menu = menu_bar.addMenu("Widok")
        action = QAction("Pokaż logi", self)
        action.setCheckable(True)
        action.triggered.connect(lambda checked: self.__set_visible_log_table(checked))
        view_menu.addAction(action)

        settings_menu = menu_bar.addMenu("Ustawienia")
        options = [
            ["change_next_layout=no", "Przy zmianie: następny układ: nie zmieniaj"],
            ["change_next_layout=yes", "Przy zmienie: następny układ: ustaw jako 000 (default)", True],
            None,
            ["change_knocked_down=no", "Przy zmienie: zbite: nie zmieniaj (default)", True],
            ["change_knocked_down=all", "Przy zmienie: zbite: ustaw że zbito wszystkie kręgle"],
            ["change_knocked_down=null", "Przy zmienie: zbite: ustaw że nie zbito żadego kręgle"],
            None,
            ["add_removed_pins=no", "Przy zmianie: dodaj liczbę usuwanych kręgli: Nie (default)", True],
            ["add_removed_pins=yes", "Przy zmianie: dodaj liczbę usuwanych kręgli: Tak"],
            None,
            ["time_speed=normal", "Brak edycji czasu (default)", True],
            ["time_speed=fast", "Szybszy czas [0.1]"],
            ["time_speed=very_fast", "Dużo szybszy czas [1.0]"],
            ["time_speed=extreme", "Ekstremalnie szybki czas [5.0]"],
            None,
            ["trial=0", "Próbne: Bez zmian (default)", True],
            ["trial=1", "Próbne: Podnieś"],
            ["trial=2", "Próbne: Podnieś i zatrzymaj"],
            None,
            ["mode=1", "Tryb 1 (default)", True],
            ["mode=2", "Tryb 2"],
            ["mode=3", "Tryb 3"],
            ["mode=4", "Tryb 4"],
            ["mode=5", "Tryb 5"],
            ["mode=6", "Tryb 6"],
            ["mode=7", "Tryb 7"]
        ]
        for option in options:
            if option is None:
                settings_menu.addSeparator()
                continue
            key = option[0]
            name = option[1]
            default = False if len(option) < 3 else option[2]
            action = QAction(name, self)
            action.setCheckable(True)
            action.setChecked(default)
            action.triggered.connect(lambda checked, k=key: self.__set_settings(k, checked))
            settings_menu.addAction(action)
            self.__settings_menu[key] = action
            if default:
                self.__set_settings(key, True)

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

    def __set_settings(self, name, value):
        list_related_options = [
            [["change_next_layout=no", "change_next_layout=yes"], "change_next_layout=yes"],
            [["change_knocked_down=no", "change_knocked_down=all", "change_knocked_down=null"], "change_knocked_down=no"],
            [["add_removed_pins=no", "add_removed_pins=yes"], "add_removed_pins=no"],
            [["time_speed=normal", "time_speed=fast", "time_speed=very_fast", "time_speed=extreme"], "time_speed=normal"],
            [["trial=0", "trial=1", "trial=2"], "trial=0"],
            [["mode=1", "mode=2", "mode=3", "mode=4", "mode=5", "mode=6", "mode=7"], "mode=1"]
        ]

        list_option_to_enable = []

        for related_options, default_option in list_related_options:
            all_option_is_false = not value
            if name not in related_options:
                continue
            for option in related_options:
                if option != name and option in self.__settings_menu:
                    if self.__settings_menu[option].isChecked():
                        if value:
                            self.__set_settings(option, False)
                            self.__settings_menu[option].setChecked(False)
                        else:
                            all_option_is_false = False
            if all_option_is_false and default_option is not None:
                list_option_to_enable.append(default_option)

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
