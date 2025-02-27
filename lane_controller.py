import time

from PyQt5.QtWidgets import QGroupBox, QGridLayout, QPushButton, QComboBox, QLabel
from PyQt5.QtCore import QTimer


class _LaneControllerSection(QGroupBox):
    def __init__(self, name: str, list_modes: list, on_start, on_stop):
        super().__init__(name)

        self.__on_start = on_start
        self.__on_stop = on_stop

        self.__layout = QGridLayout()
        self.setLayout(self.__layout)

        self.__btn_start = QPushButton("Start")
        self.__btn_stop = QPushButton("Stop")
        self.__options_combobox = QComboBox()
        self.__options_label = QLabel("")

        self.__options_combobox.addItems(list_modes)

        self.__btn_start.clicked.connect(self.__click_start)
        self.__btn_stop.clicked.connect(self.__click_stop)

        self.__layout.addWidget(self.__options_combobox, 0, 0)
        self.__layout.addWidget(self.__options_label, 1, 0)
        self.__layout.addWidget(self.__btn_start, 0, 1)
        self.__layout.addWidget(self.__btn_stop, 1, 1)
        self.__toggle_view(True)

    def __toggle_view(self, show_start):
        self.__options_combobox.setVisible(show_start)
        self.__btn_start.setVisible(show_start)
        self.__options_label.setVisible(not show_start)
        self.__btn_stop.setVisible(not show_start)

    def __click_start(self):
        mode = self.__options_combobox.currentText()
        self.__options_label.setText(mode)
        self.__on_start(mode)
        self.__toggle_view(False)

    def __click_stop(self):
        self.__on_stop()
        self.__toggle_view(True)

    def show_start_layout(self):
        QTimer.singleShot(0, self.__click_stop)


class _LaneCommunicationManager:
    def __init__(self, lane_number, on_send_message, show_start_layout, time_break_after_recv):
        self.__lane_number = lane_number
        self.__message_head = b"3" + str(self.__lane_number).encode('utf-8') + b"38"
        self.__on_send_message = on_send_message
        self.__throws_to_current_layout = 0
        self.__show_start_layout = show_start_layout
        self.__run = False
        self.__mode = ""
        self.__change_all_knocked_down = False
        self.__change_no_knocked_down = False
        self.__change_next_layout = False
        self.__pick_up = False
        self.__time_speed = False
        self.__time_very_speed = False
        self.__time_break_after_recv = time_break_after_recv

    def start(self, mode):
        self.__throws_to_current_layout = 0
        self.__mode = mode
        self.__run = True

        self.__on_send_message(self.__message_head + b"E1")
        self.__on_send_message(self.__message_head + b"IG0000633E70000000000")

    def stop(self):
        self.__on_send_message(self.__message_head + b"E0")
        self.__run = False

    def analyze_message(self, message):
        if not self.__run:
            return
        if message[4:6] == b"i0":
            self.__show_start_layout()
            return
        if message[4:5] in [b"w", b"g", b"h", b"f"]:

            next_layout = message[17:20]
            if next_layout != b"000":
                self.__throws_to_current_layout += 1
            else:
                self.__throws_to_current_layout = 0
            if self.__mode == "Optymistyczne zbierane":
                self.__analyse_optimistic_clearoff(next_layout, message)
            elif "Zbierane na " in self.__mode:
                self.__analyse_max_throw_clearoff(message)
        time.sleep(self.__time_break_after_recv)
        self.__on_send_message(self.__message_head)

    def __analyse_optimistic_clearoff(self, next_layout, message):
        next_layout_invert = self.__invert_bits(next_layout)
        if next_layout_invert in [b"001", b"002", b"004", b"008", b"010", b"020", b"040", b"080", b"100"]:
            x = 1
        elif next_layout_invert in [b"006", b"018", b"030", b"0C0", b"028"]:
            x = 2
        elif next_layout_invert == b"038":
            x = 3
        else:
            return
        self.__on_send_message(
            self.__message_head +
            b"Z" +
            self.__add_to_hex(message[5:8], x) +
            message[8:14] +
            self.__add_to_hex(message[14:17], x) +
            self.__get_next_layout(message[17:20], self.__change_next_layout) +
            message[20:23] +
            self.__get_time(message[23:26]) +
            self.__get_knocked_down(message[26:29], self.__change_all_knocked_down, self.__change_no_knocked_down) +
            message[29:-2]
        )
        if self.__pick_up:
            self.__on_send_message(self.__message_head + b"T41")

    def __analyse_max_throw_clearoff(self, message):
        max_throw = int(self.__mode.replace("Zbierane na ", ""))
        if self.__throws_to_current_layout < max_throw:
            return
        self.__on_send_message(
            self.__message_head +
            b"Z" +
            message[5:17] +
            self.__get_next_layout(message[17:20], self.__change_next_layout) +
            message[20:23] +
            self.__get_time(message[23:26]) +
            self.__get_knocked_down(message[26:29], self.__change_all_knocked_down, self.__change_no_knocked_down) +
            message[29:-2]
        )
        self.__throws_to_current_layout = 0
        if self.__pick_up:
            self.__on_send_message(self.__message_head + b"T41")

    @staticmethod
    def __get_next_layout(current_value, return_empty):
        if return_empty:
            return b"000"
        return current_value

    @staticmethod
    def __get_knocked_down(current_value, return_all, return_no):
        if return_all:
            return b"1FF"
        if return_no:
            return b"000"
        return current_value

    def __get_time(self, current_value):
        if self.__time_speed:
            return self.__sub_to_hex(current_value, 1)
        if self.__time_very_speed:
            return self.__sub_to_hex(current_value, 10)
        return current_value

    @staticmethod
    def __add_to_hex(hex_bytes, x):
        hex_str = hex_bytes.decode('utf-8')
        hex_value = int(hex_str, 16)
        new_hex_value = hex_value + x

        new_hex_str = hex(new_hex_value)[2:].upper().zfill(3)
        new_hex_bytes = new_hex_str.encode('utf-8')

        return new_hex_bytes

    @staticmethod
    def __sub_to_hex(hex_bytes, x):
        hex_str = hex_bytes.decode('utf-8')
        hex_value = int(hex_str, 16)
        if x >= hex_value:
            return b"000"
        new_hex_value = hex_value - x

        new_hex_str = hex(new_hex_value)[2:].upper().zfill(3)
        new_hex_bytes = new_hex_str.encode('utf-8')

        return new_hex_bytes

    @staticmethod
    def __invert_bits(hex_bytes):
        hex_str = hex_bytes.decode('utf-8')
        int_value = int(hex_str, 16)
        bit_length = 9
        mask = (1 << bit_length) - 1
        inverted_value = int_value ^ mask
        inverted_hex = format(inverted_value, '03X')
        inverted_bytes = inverted_hex.encode('utf-8')
        return inverted_bytes

    def set_settings(self, name, value):
        if name == "change_all_knocked_down":
            self.__change_all_knocked_down = value
        elif name == "change_no_knocked_down":
            self.__change_no_knocked_down = value
        elif name == "pick_up":
            self.__pick_up = value
        elif name == "change_next_layout":
            self.__change_next_layout = value
        elif name == "time_speed":
            self.__time_speed = value
        elif name == "time_very_speed":
            self.__time_very_speed = value


class LaneController:
    def __init__(self, lane_number, on_send_message, time_break_after_recv):
        self.__communication_manager = _LaneCommunicationManager(lane_number, on_send_message, self.__show_start_layout, time_break_after_recv)
        self.__modes = [
            "Zbierane na 2",
            "Zbierane na 3",
            "Zbierane na 4",
            "Zbierane na 5",
            "Optymistyczne zbierane"
        ]
        self.__section = _LaneControllerSection("Tor {}".format(lane_number+1), self.__modes, self.__communication_manager.start, self.__communication_manager.stop)

    def get_section(self):
        return self.__section

    def __show_start_layout(self):
        self.__section.show_start_layout()

    def on_recv_message(self, message: bytes):
        self.__communication_manager.analyze_message(message)

    def set_settings(self, name, value):
        self.__communication_manager.set_settings(name, value)
