import time

from PyQt5.QtWidgets import QGroupBox, QGridLayout, QPushButton, QComboBox, QLabel
from PyQt5.QtCore import QTimer


class _LaneControllerSection(QGroupBox):
    def __init__(self, name: str, list_modes: list, on_trial, on_start, on_stop, add_log):
        super().__init__(name)

        self.__show_trial = False
        self.__program_is_not_running = True

        self.__name = name
        self.__add_log = add_log

        self.__on_trial = on_trial
        self.__on_start = on_start
        self.__on_stop = on_stop

        self.__layout = QGridLayout()
        self.setLayout(self.__layout)

        self.__btn_trial = QPushButton("Próbne")
        self.__btn_start = QPushButton("Start")
        self.__btn_stop = QPushButton("Stop")
        self.__options_combobox = QComboBox()
        self.__options_label = QLabel("")

        self.__options_combobox.addItems(list_modes)

        self.__btn_trial.clicked.connect(self.__click_trial)
        self.__btn_start.clicked.connect(self.__click_start)
        self.__btn_stop.clicked.connect(self.__click_stop)

        self.__layout.addWidget(self.__options_combobox, 0, 0)
        self.__layout.addWidget(self.__options_label, 1, 0)
        self.__layout.addWidget(self.__btn_trial, 0, 1)
        self.__layout.addWidget(self.__btn_start, 0, 2)
        self.__layout.addWidget(self.__btn_stop, 1, 1, 1, 2)

        self.__toggle_view(True)

    def __toggle_view(self, show_start):
        self.__program_is_not_running = show_start
        self.__options_combobox.setVisible(show_start)
        self.__btn_trial.setVisible(show_start and self.__show_trial)
        self.__btn_start.setVisible(show_start)
        self.__options_label.setVisible(not show_start)
        self.__btn_stop.setVisible(not show_start)

    def __click_trial(self):
        self.__add_log(5, "START TRIAL", self.__name)
        self.__options_label.setText("Próbne")
        self.__on_trial()
        self.__toggle_view(False)

    def __click_start(self):
        mode = self.__options_combobox.currentText()
        self.__add_log(5, "START GAME", self.__name + " | " + mode)
        self.__options_label.setText(mode)
        self.__on_start(mode)
        self.__toggle_view(False)

    def __click_stop(self):
        self.__add_log(5, "STOP", self.__name)
        self.__on_stop()
        self.__toggle_view(True)

    def show_start_layout(self):
        QTimer.singleShot(0, self.__click_stop)

    def set_visible_trial_button(self, show):
        self.__show_trial = show
        self.__btn_trial.setVisible(show and self.__program_is_not_running)


class _LaneCommunicationManager:
    def __init__(self, lane_number, on_send_message, show_start_layout, on_get_message):
        self.__lane_number = lane_number
        self.__message_head = b"3" + str(self.__lane_number).encode('Windows-1250') + b"38"
        self.__on_send_message = on_send_message
        self.__on_get_message = on_get_message
        self.__throws_to_current_layout = 0
        self.__show_start_layout = show_start_layout
        self.__run = False
        self.__mode = ""
        self.__change_knocked_down = "no"
        self.__change_next_layout = "no"
        self.__time_speed = "normal"
        self.__trial = "0"
        self.__add_removed_pins = "no"
        self.__full_layout_mode = 1
        self.__time_break_after_recv = 0.3

    def trial(self):
        self.__on_send_message(self.__message_head + b"E1")
        self.__on_send_message(self.__message_head + b"P00E0320")
        if self.__trial == "1" or self.__trial == "2":
            self.__on_send_message(self.__message_head + b"T41")
        if self.__trial == "2":
            self.__on_send_message(self.__message_head + b"T14")
        self.__run = True

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
            fallen_pins = message[26:29]
            # fallen_pins == b"000" is a special case where a player doesn't hit any pins in a full roll
            if next_layout != b"000" or fallen_pins == b"000":
                self.__throws_to_current_layout += 1
            else:
                self.__throws_to_current_layout = 0
            if self.__mode == "Optymistyczne zbierane":
                self.__analyse_optimistic_clearoff(next_layout, message)
            elif "Zbierane na " in self.__mode:
                self.__analyse_max_throw_clearoff(message)
        time.sleep(self.__time_break_after_recv)
        self.__on_send_message(self.__message_head, 2)

    def on_analyze_recv_message(self, message):

        if not self.__run:
            return [], []
        if message[4:6] == b"i0":
            self.__show_start_layout()
            return [], []

        ping = self.__on_get_message(self.__message_head)

        front_msg, end_msg = [], []
        if message[4:5] in [b"w", b"g", b"h", b"f"]:
            next_layout = message[17:20]
            fallen_pins = message[26:29]
            # fallen_pins == b"000" is a special case where a player doesn't hit any pins in a full roll

            if next_layout != b"000" or fallen_pins == b"000":
                self.__throws_to_current_layout += 1
            else:
                self.__throws_to_current_layout = 0
            print(self.__throws_to_current_layout, next_layout, fallen_pins)
            if self.__mode == "Optymistyczne zbierane":
                front_msg, end_msg = self.__analyse_optimistic_clearoff(next_layout, message)
            elif "Zbierane na " in self.__mode:
                front_msg, end_msg = self.__analyse_max_throw_clearoff(message)
        end_msg.append(ping)
        return front_msg, end_msg

    def __analyse_optimistic_clearoff(self, next_layout, message):
        next_layout_invert = self.__invert_bits(next_layout)
        if next_layout_invert in [b"001", b"002", b"004", b"008", b"010", b"020", b"040", b"080", b"100"]:
            x = 1
        elif next_layout_invert in [b"006", b"018", b"030", b"0C0", b"028"]:
            x = 2
        elif next_layout_invert == b"038":
            x = 3
        else:
            return [], []
        return self.__send_message_to_end_layout(
            self.__add_to_hex(message[5:8], x),
            message[8:11],
            self.__add_to_hex(message[11:14], x),
            message[14:17],
            message[17:20],
            message[20:23],
            message[23:26],
            message[26:29],
            message[29:-2]
        )

    def __analyse_max_throw_clearoff(self, message):
        max_throw = int(self.__mode.replace("Zbierane na ", ""))
        if self.__throws_to_current_layout < max_throw:
            return [], []
        self.__throws_to_current_layout = 0
        return self.__send_message_to_end_layout(
            message[5:8],
            message[8:11],
            message[11:14],
            message[14:17],
            message[17:20],
            message[20:23],
            message[23:26],
            message[26:29],
            message[29:-2]
        )

    def __send_message_to_end_layout(self, number_of_throw, last_throw_result, lane_sum, total_sum, next_layout,
                                     number_of_x, time_to_end, fallen_pins, options):
        time_to_end = self.__get_time(time_to_end)

        b_click = lambda msg, priority=3, time_wait=-1: self.__on_get_message(self.__message_head + msg, priority, time_wait)

        b_stop = lambda time_wait=-1, priority=9: b_click(b"T40", priority, time_wait)
        b_layout = lambda time_wait=-1, priority=5: b_click(b"T16", priority, time_wait)
        b_clear = lambda time_wait=-1, priority=6: b_click(b"T22", priority, time_wait)
        b_enter = lambda time_wait=-1, priority=6: b_click(b"T24", priority, time_wait)
        b_pick_up = lambda time_wait=-1, priority=7: b_click(b"T41", priority, time_wait)

        z = lambda time_wait=-1, priority=5: self.__on_get_message(
            self.__message_head +
            b"Z" +
            number_of_throw +
            last_throw_result +
            lane_sum +
            total_sum +
            b"000" +
            number_of_x +
            time_to_end +
            fallen_pins +
            options,
            priority,
            time_wait
        )

        pins = self.__count_beaten_pins(next_layout)
        total_sum_1 = self.__add_to_hex(total_sum, pins)
        lane_sum_1 = self.__add_to_hex(lane_sum, pins)

        z_1 = lambda time_wait=-1, priority=5: self.__on_get_message(
            self.__message_head +
            b"Z" +
            number_of_throw +
            last_throw_result +
            lane_sum_1 +
            total_sum_1 +
            next_layout +
            number_of_x +
            time_to_end +
            fallen_pins +
            options,
            priority,
            time_wait
        )

        list_full_layout_modes = {
            1: [b_stop(), b_layout(), b_clear(), b_enter(), z(1500), b_pick_up()],  # A,5000
            2: [b_stop(), b_layout(300), b_clear(300), b_enter(), z(1500), b_pick_up(300)],  # B,3800
            3: [b_stop(0), b_layout(300), b_clear(300), b_enter(), z(1500), b_pick_up(300)],  # C,3100
            4: [b_stop(0), b_layout(200), b_clear(200), b_enter(), z(1000), b_pick_up(200)],  # D,2300
            5: [b_stop(0), b_layout(200), b_clear(200), b_enter(1000), z(1000), b_pick_up(200)],  # E,2600
            6: [b_stop(0), b_layout(200), b_clear(200), b_enter(1000), z(200), b_pick_up(200)],  # F,1800
            7: [b_stop(0), b_layout(200), b_clear(200), b_enter(200), z(1000), b_pick_up(200)],  # G,1800
            8: [b_stop(0), b_layout(200), b_clear(200), b_enter(200), z(200), b_pick_up(1000)],  # H,1800
            9: [b_stop(0), b_layout(50), b_clear(50), b_enter(1000), z(1000), b_pick_up(50)],  # I,2150
            10: [b_stop(0), b_layout(50), b_clear(50), b_enter(1000), z(50), b_pick_up(50)],  # J,1200
            11: [b_stop(0), b_layout(50), b_clear(50), b_enter(50), z(1000), b_pick_up(50)],  # K,1200
            12: [b_stop(0), b_layout(50), b_clear(50), b_enter(50), z(50), b_pick_up(1000)],  # L,1200
            13: [b_stop(0), b_layout(0), b_clear(0), b_enter(1000), z(0), b_pick_up(0)],  #
            14: [b_stop(0), b_layout(0), b_clear(0), b_enter(0), z(1000), b_pick_up(0)],  #
            15: [b_stop(0), b_layout(0), b_clear(0), b_enter(0), z(0), b_pick_up(1000)],  #
            16: [b_stop(0), b_layout(0), b_clear(0), b_enter(800), z(0), b_pick_up(0)],  #
            17: [b_stop(0), b_layout(0), b_clear(0), b_enter(0), z(800), b_pick_up(0)],  #
            18: [b_stop(0), b_layout(0), b_clear(0), b_enter(0), z(0), b_pick_up(800)],  #
            19: [b_stop(0), b_layout(0), b_clear(0), b_enter(700), z(0), b_pick_up(0)],  #
            20: [b_stop(0), b_layout(0), b_clear(0), b_enter(0), z(700), b_pick_up(0)],  #
            21: [b_stop(0), b_layout(0), b_clear(0), b_enter(0), z(0), b_pick_up(700)],  #
            22: [b_stop(0), b_layout(0), b_clear(0), b_enter(600), z(0), b_pick_up(0)],  #
            23: [b_stop(0), b_layout(0), b_clear(0), b_enter(0), z(600), b_pick_up(0)],  #
            24: [b_stop(0), b_layout(0), b_clear(0), b_enter(0), z(0), b_pick_up(600)],  #
            25: [b_stop(0), b_layout(0), b_clear(0), b_enter(500), z(0), b_pick_up(0)],  #
            26: [b_stop(0), b_layout(0), b_clear(0), b_enter(0), z(500), b_pick_up(0)],  #
            27: [b_stop(0), b_layout(0), b_clear(0), b_enter(0), z(0), b_pick_up(500)],  #

            28: [b_stop(800), z_1(1500), b_layout(800), b_clear(800), b_enter(800), b_pick_up(800)],  # Tryb 28
            29: [b_stop(0), z_1(1500), b_layout(200), b_clear(200), b_enter(800), b_pick_up(800)],  # Tryb 29
            30: [b_stop(0), z_1(1500), b_layout(800), b_clear(300), b_enter(800), b_pick_up(800)],  # Tryb 30
            31: [b_stop(0), z_1(1500), b_layout(300), b_clear(300), b_enter(800), b_pick_up(800)],  # Tryb 31
            32: [b_stop(0), z_1(1500), b_layout(300), b_clear(300), b_enter(300), b_pick_up(800)],  # Tryb 32
            33: [b_stop(0), z_1(1500), b_layout(300), b_clear(300), b_enter(300), b_pick_up(300)],  # Tryb 33
            34: [b_stop(0), z_1(800), b_layout(800), b_clear(0), b_enter(800), b_pick_up(800)],  # Tryb 34
            35: [b_stop(0), z_1(800), b_layout(0), b_clear(0), b_enter(800), b_pick_up(800)],  # Tryb 35
            36: [b_stop(0), z_1(800), b_layout(0), b_clear(0), b_enter(0), b_pick_up(800)],  # Tryb 36
            37: [b_stop(0), z_1(800), b_layout(0), b_clear(0), b_enter(800), b_pick_up(0)],  # Tryb 37
            38: [b_stop(0), z_1(0), b_layout(800), b_clear(0), b_enter(800), b_pick_up(800)],  # Tryb 38
            39: [b_stop(0), z_1(0), b_layout(800), b_clear(0), b_enter(800), b_pick_up(0)],  # Tryb 39
            40: [b_stop(0), z_1(0), b_layout(800), b_clear(0), b_enter(0), b_pick_up(800)],  # Tryb 40
            41: [b_stop(0), z_1(0), b_layout(0), b_clear(0), b_enter(800), b_pick_up(800)],  # Tryb 41
            42: [b_stop(0), z_1(0), b_layout(0), b_clear(0), b_enter(800), b_pick_up(0)],  # Tryb 42
            43: [b_stop(0), z_1(0), b_layout(0), b_clear(0), b_enter(0), b_pick_up(800)],  # Tryb 43
            44: [b_stop(0), z_1(700), b_layout(0), b_clear(0), b_enter(700), b_pick_up(700)],  # Tryb 44
            45: [b_stop(0), z_1(700), b_layout(0), b_clear(0), b_enter(0), b_pick_up(700)],  # Tryb 45
            46: [b_stop(0), z_1(700), b_layout(0), b_clear(0), b_enter(700), b_pick_up(0)],  # Tryb 46
            47: [b_stop(0), z_1(0), b_layout(0), b_clear(0), b_enter(700), b_pick_up(700)],  # Tryb 47
            48: [b_stop(0), z_1(0), b_layout(0), b_clear(0), b_enter(700), b_pick_up(0)],  # Tryb 48
            49: [b_stop(0), z_1(0), b_layout(0), b_clear(0), b_enter(0), b_pick_up(700)],  # Tryb 49
            50: [b_stop(0), z_1(600), b_layout(0), b_clear(0), b_enter(600), b_pick_up(600)],  # Tryb 50
            51: [b_stop(0), z_1(600), b_layout(0), b_clear(0), b_enter(0), b_pick_up(600)],  # Tryb 51
            52: [b_stop(0), z_1(600), b_layout(0), b_clear(0), b_enter(600), b_pick_up(0)],  # Tryb 52
            53: [b_stop(0), z_1(0), b_layout(0), b_clear(0), b_enter(600), b_pick_up(600)],  # Tryb 53
            54: [b_stop(0), z_1(0), b_layout(0), b_clear(0), b_enter(600), b_pick_up(0)],  # Tryb 54
            55: [b_stop(0), z_1(0), b_layout(0), b_clear(0), b_enter(0), b_pick_up(600)],  # Tryb 55

        }

        if self.__full_layout_mode in list_full_layout_modes.keys():
            mode = list_full_layout_modes[self.__full_layout_mode]
        else:
            mode = list_full_layout_modes[1]

        return mode, []

    @staticmethod
    def __count_beaten_pins(layout):
        hex_str = layout.decode('Windows-1250')
        value = int(hex_str, 16)
        ones_count = bin(value).count('1')
        return ones_count

    @staticmethod
    def __get_next_layout(current_value, next_layout):
        if next_layout == "000":
            return b"000"
        if next_layout == "001":
            return b"001"
        return current_value

    @staticmethod
    def __get_knocked_down(current_value, return_option):
        """
        :param return_option: no - return current value, all - return full layout, null - return empty layout
        """
        if return_option == "all":
            return b"1FF"
        if return_option == "null":
            return b"000"
        if return_option == "001":
            return b"001"
        return current_value

    def __get_time(self, current_value):
        values = {
            "fast": 1,
            "very_fast": 10,
            "extreme": 50
        }
        if self.__time_speed in values:
            return self.__sub_to_hex(current_value, values[self.__time_speed])
        return current_value

    @staticmethod
    def __add_to_hex(hex_bytes, x):
        hex_str = hex_bytes.decode('Windows-1250')
        hex_value = int(hex_str, 16)
        new_hex_value = hex_value + x

        new_hex_str = hex(new_hex_value)[2:].upper().zfill(3)
        new_hex_bytes = new_hex_str.encode('Windows-1250')

        return new_hex_bytes

    @staticmethod
    def __sub_to_hex(hex_bytes, x):
        hex_str = hex_bytes.decode('Windows-1250')
        hex_value = int(hex_str, 16)
        if x >= hex_value:
            return b"000"
        new_hex_value = hex_value - x

        new_hex_str = hex(new_hex_value)[2:].upper().zfill(3)
        new_hex_bytes = new_hex_str.encode('Windows-1250')

        return new_hex_bytes

    @staticmethod
    def __invert_bits(hex_bytes):
        hex_str = hex_bytes.decode('Windows-1250')
        int_value = int(hex_str, 16)
        bit_length = 9
        mask = (1 << bit_length) - 1
        inverted_value = int_value ^ mask
        inverted_hex = format(inverted_value, '03X')
        inverted_bytes = inverted_hex.encode('Windows-1250')
        return inverted_bytes

    def set_settings(self, name, value):
        if name.split("=")[0] == "mode":
            self.__full_layout_mode = int(name.split("=")[1])
        elif name.split("=")[0] == "change_next_layout":
            self.__change_next_layout = name.split("=")[1]
        elif name.split("=")[0] == "change_knocked_down":
            self.__change_knocked_down = name.split("=")[1]
        elif name.split("=")[0] == "time_speed":
            self.__time_speed = name.split("=")[1]
        elif name.split("=")[0] == "trial":
            self.__trial = name.split("=")[1]
        elif name.split("=")[0] == "add_removed_pins":
            self.__add_removed_pins = name.split("=")[1]
        elif name.split("=")[0] == "time_wait":
            self.__time_break_after_recv = float(name.split("=")[1])


class LaneController:
    def __init__(self, lane_number, on_send_message, add_log, on_get_message):
        self.__communication_manager = _LaneCommunicationManager(lane_number, on_send_message, self.__show_start_layout, on_get_message)
        self.__modes = [
            "Zbierane na 1",
            "Zbierane na 2",
            "Zbierane na 3",
            "Zbierane na 4",
            "Zbierane na 5",
            "Optymistyczne zbierane"
        ]
        self.__section = _LaneControllerSection(
            "Tor {}".format(lane_number+1),
            self.__modes,
            self.__communication_manager.trial,
            self.__communication_manager.start,
            self.__communication_manager.stop,
            add_log
        )

    def get_section(self):
        return self.__section

    def __show_start_layout(self):
        self.__section.show_start_layout()

    def on_recv_message(self, message: bytes):
        self.__communication_manager.analyze_message(message)

    def on_analyze_recv_message(self, message: bytes):
        return self.__communication_manager.on_analyze_recv_message(message)

    def set_settings(self, name, value):
        self.__communication_manager.set_settings(name, value)

    def set_visible_trial_button(self, show):
        self.__section.set_visible_trial_button(show)
