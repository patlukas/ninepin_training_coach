import serial
import time
from typing import Union


class ComManagerError(Exception):
    """
    List code:
        "10-000" - wrong type of variable
        "10-001" - error during port creation, wrong parameters e.g. baud rate, data bits
        "10-002" - error during port creation, port not exists or is used
        "10-003" - trying to read data from an unopened port
        "10-004" - trying to send data to an unopened port
        "10-005" - trying to close unopened port
    """

    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__()


class ComManager:
    def __init__(self, port_name: str, timeout: Union[int, float, None], write_timeout: Union[int, float, None], add_log):
        # TODO: Change list dict to list class(?) in __list_to_send
        # TODO: Add default time_wait, add default priority, and if it not set in msg then get this values
        self.__port_name = port_name
        self.__send_lane_pointer = 0
        self.__waiting_bytes_to_send = b""
        self.__waiting_bytes_to_recv = b""
        self.__list_to_send = [
            {"time_last_send": 0, "messages": []},
            {"time_last_send": 0, "messages": []},
            {"time_last_send": 0, "messages": []},
            {"time_last_send": 0, "messages": []},
            {"time_last_send": 0, "messages": []},
            {"time_last_send": 0, "messages": []}
        ]
        self.__list_to_recv = []
        self.__add_log = add_log
        self.__com_port = self.__create_port(timeout, write_timeout)

        self.__default_time_wait_between_msg_on_lane = 700
        self.__list_func_for_analyze_msg_to_send = []
        self.__list_func_for_analyze_msg_to_recv = []

        """
        # lane_pointer: X
        # list_to_send: [
        #     { // lane 1
        #       "time_last_send": time,
        #       messages: [
        #         {message: bytes, time_wait: int, priority: int}, 
        #         ...
        #       ]  
        #     }, 
        #     ...
        # ]
        # -------------
        
        # Recv from PC:
        # 1. zapisanie bajtów w self.__waiting_bytes_to_send
        # 2. odczyt w pętli cąłych wiadomości (które kończą się na \r) i zapisywanie wiadomości do __list_to_send
        #     sprawdzeie czy wiadomość nie jest specjalna (A) 
        #         TAK:
        #             Dodanie wiadomości przygotowanych przez (A)
        #         NIE:
        #             jest to ping i jest ping w kolejce:
        #                 TAK:
        #                     pomiń wiadomość
        #                 NIE:
        #                     dodanie normalnej wiadomości do listy z ustawionym parametrami
        #                         priorytet: 3
        #                         time wait: default (np -1) 
                    
            
        (A) Specjalne wiadomości od PC:
            - ustawienie próbnych
                - wiadomości na koniec listy funkcja może zwracać w listy [add_to_front], [add_to_end]
                    Próbne: priorytet 3, time_wait: -1
                    Podnieś: priorytet 3, time_wait: -1
                    Zatrzymaj: priorytet 3, time_wait: -1
            
            
        # Send to Lane:
        #     Wskaźnik na X (0,5) jeżeli wiadomość będzie wysłana z X to (X+1)%6
        #     Sprawdzanie na kóry tor wysłąć wiadmomość aczynając od X. Kryteria aby rozpatrywać wiadomość:
        #     time_now > time_last_send + time_wait. 
        #     coś w stylu:
        #         p = -1
        #         p_priority: -1
        #         for i in range(6):
        #             j = (lane_pointer+i)%6
        #             if len(list_to_send[j]["messages"]) == 0:
        #                continue
        #             if time_now <= list_to_send[j]["time_last_send"] + list_to_send[j]["messages"][0]["time_wait"]
        #                 continue
        #             if list_to_send[j]["messages"][0]["priority"] > p_priority:
        #                p = j
        #                p_priority = list_to_send[j]["messages"][0]["priority"]
        #         
        #         if p == -1:
        #             nie nie wysyłą
        #         wysyła wiadomość z "p"
        #         usuwa pierwszą wiadomosć z "p"
        #         list_to_send[p]["time_last_send"] = time_now
        #         if p == lane_pointer:
        #             lane_pointer = (lane_pointer + 1) % 6
                    
        
        
        # Recv from Lane:
        #     1. dodanie odebrnaych danych do __waiting_bytes_to_recv (?)
        #     2.  odczyt w pętli cąłych wiadomości (które kończą się na \r)
        #         sprawdzeie czy wiadomość nie jest specjalna (B)
        #         TAK:
        #             Dodanie wiadomości przygotowanych przez (B) do listy z wiadomościami do wysłąnia DO LANE !!!
        #         dodanie wiadomości do __bytes_to_recv
                
        (B) Specjalne wiadomości od LANE:
            - trzeci rzut do ukłądu i tor obserwowanyp pod tym względem
                - wiadomości na POCZĄTEK  listy - funkcja może zwracać w listy [add_to_front], [add_to_end]
                    STOP: priorytet 8, time_wait: -1
                    LAYOUT priorytet 5, time_wait: -1
                    CLEAR priorytet 6, time_wait: -1
                    ENTER priorytet 6, time_wait: -1
                    "Z" priorytet 3, time_wait: 1500 
                    Podnieś: priorytet 5, time_wait: -1
            
            
        
        Send to PC:
            odczyt pierwszej wiadomości z __bytes_to_recv
        
        Pytania:
            Czy system poradzi sobie z nadmiernymi wiadomościami od Lane, można odrzucać Pongi w przpadku odpowwiedniej liczby przesłanych wiadomości do kompa
                albo zrobić licznik odebrane od PC, wysłane do PC, odrzucone pingi i R_PC = S_to_PC + odrzucone_pingi
        
        """

    def __create_port(self, timeout: Union[float, None], write_timeout: Union[float, None]) -> serial.Serial:
        try:
            com_port = serial.Serial(self.__port_name, 9600, timeout=timeout, write_timeout=write_timeout)
            return com_port
        except ValueError as e:
            raise ComManagerError("10-001", "ValueError while create {} port: parameter are out of range, "
                                            "e.g. baud rate, data bits| {}".format(self.__port_name, e))
        except serial.SerialException as e:
            raise ComManagerError("10-002", "SerialException while create {} port: In case the device can not be "
                                            "found or can not be configured| {}".format(self.__port_name, e))

    def read(self) -> bytes:
        if self.__com_port is None:
            return b""

        in_waiting = self.__com_port.in_waiting
        if in_waiting == 0:
            return b""

        data_read = self.__com_port.read(in_waiting)
        self.__waiting_bytes_to_recv += data_read

        return self.__analyze_bytes_to_recv()

    def send(self) -> (int, bytes):
        if self.__com_port is None:
            self.__add_log(10, "COM", "Port {} is closed or not was be created, so I can't send data".format(self.__port_name))

        if self.__com_port.out_waiting > 0:
            return 0, b""

        count_lane = len(self.__list_to_send)

        try:
            time_now = time.time() * 1000
            msg_lane_index = -1
            msg_lane_priority = -1
            for i in range(count_lane):
                lane_index = (self.__send_lane_pointer + i) % count_lane
                list_msg = self.__list_to_send[lane_index]["messages"]

                if len(list_msg) == 0:
                    continue

                priority = list_msg[0]["priority"]

                time_wait = list_msg[0]["time_wait"]
                if time_wait == -1:
                    time_wait = self.__default_time_wait_between_msg_on_lane

                if time_now < self.__list_to_send[lane_index]["time_last_send"] + time_wait:
                    continue

                if priority > msg_lane_priority:
                    msg_lane_index = lane_index
                    msg_lane_priority = priority

            if msg_lane_index == -1:
                return 0, b""

            sent_bytes = b""
            while True:
                sent_bytes += self.__list_to_send[msg_lane_index]["messages"][0]["message"]
                self.__list_to_send[msg_lane_index]["messages"].pop(0)
                if len(self.__list_to_send[msg_lane_index]["messages"]) == 0:
                    break
                if self.__list_to_send[msg_lane_index]["messages"][0]["time_wait"] != -2:
                    break
            number_sent_bytes = self.__com_port.write(sent_bytes)
            self.__list_to_send[msg_lane_index]["time_last_send"] = time_now

            if len(sent_bytes) != number_sent_bytes:
                self.__add_log(10, "NEW_3", "Not send all bytes: '{}' {} {}".format(sent_bytes, len(sent_bytes), number_sent_bytes))

            if msg_lane_index == self.__send_lane_pointer:
                self.__send_lane_pointer = (self.__send_lane_pointer + 1) % count_lane

            return len(sent_bytes), sent_bytes
        except serial.SerialTimeoutException as e:
            return -1, b""

    def add_bytes_to_send(self, new_bytes_to_send: bytes) -> int:
        if type(new_bytes_to_send) != bytes:
            self.__add_log(10, "COM", "Wrong type of data to send: '{}' have type '{}'".format(new_bytes_to_send, type(new_bytes_to_send).__name__))
        else:
            if new_bytes_to_send[-1:] != b"\r":
                self.__add_log(10, "COM", "Wrong end of data to send, should have '\r' as last sign: '{}'".format(new_bytes_to_send[-1:]))
            else:
                self.__waiting_bytes_to_send += new_bytes_to_send
                self.__analyze_bytes_to_send()

    def __analyze_bytes_to_send(self):
        # TODO: jest to ping i jest ping w kolejce: pomiń msg
        # TODO change error msg, add more logs
        while b"\r" in self.__waiting_bytes_to_send:
            index_first_special_sign = self.__waiting_bytes_to_send.index(b"\r") + 1
            msg = self.__waiting_bytes_to_send[:index_first_special_sign]
            self.__add_log(4, "MSG_SEND", "{}".format(msg))
            self.__waiting_bytes_to_send = self.__waiting_bytes_to_send[index_first_special_sign:]
            list_front_msg, list_end_msg = self.__analyze_special_msg_to_send(msg)
            if len(list_front_msg) + len(list_end_msg) == 0:
                list_end_msg = [{"message": msg, "time_wait": -1, "priority": 3}]
            try:
                lane_index = int(chr(msg[1]))
                if lane_index >= len(self.__list_to_send):
                    self.__add_log(10, "NEW_2", "Error: Wrong lane_index {}".format(lane_index))
                    return
                self.__list_to_send[lane_index]["messages"] = list_front_msg + self.__list_to_send[lane_index]["messages"] + list_end_msg
            except ValueError as e:
                self.__add_log(10, "NEW_1", "Error: {}".format(e))
                return

    def __analyze_special_msg_to_send(self, msg):
        # TODO: Add more logs
        for func in self.__list_func_for_analyze_msg_to_send:
            list_front_msg, list_end_msg = func(msg)
            if len(list_front_msg) + len(list_end_msg) != 0:
                return list_front_msg, list_end_msg
        return [], []

    def add_func_to_analyze_msg_to_send(self, func):
        # TODO: Add log
        self.__list_func_for_analyze_msg_to_send.append(lambda msg: func(msg))

    def __analyze_bytes_to_recv(self):
        # TODO: jest to ping i jest ping w kolejce: pomiń msg
        # TODO change error msg, add more logs
        recv_msg = b""
        while b"\r" in self.__waiting_bytes_to_recv:
            index_first_special_sign = self.__waiting_bytes_to_recv.index(b"\r") + 1
            msg = self.__waiting_bytes_to_recv[:index_first_special_sign]
            self.__add_log(4, "MSG_RECV", "{}".format(msg))
            self.__waiting_bytes_to_recv = self.__waiting_bytes_to_recv[index_first_special_sign:]
            list_front_msg_to_send, list_end_msg_to_send = self.__analyze_special_msg_to_recv(msg)
            self.__list_to_recv.append(msg)
            recv_msg += msg
            try:
                lane_index = int(chr(msg[3]))
                if lane_index >= len(self.__list_to_send):
                    self.__add_log(10, "NEW_4", "Error: Wrong lane_index {}".format(lane_index))
                    return recv_msg
                self.__list_to_send[lane_index]["messages"] = list_front_msg_to_send + self.__list_to_send[lane_index]["messages"] + list_end_msg_to_send
            except ValueError as e:
                self.__add_log(10, "NEW_5", "Error: {}".format(e))
                return recv_msg
        return recv_msg

    def __analyze_special_msg_to_recv(self, msg):
        # TODO: Add more logs
        for func in self.__list_func_for_analyze_msg_to_recv:
            list_front_msg, list_end_msg = func(msg)
            if len(list_front_msg) + len(list_end_msg) != 0:
                return list_front_msg, list_end_msg
        return [], []

    def add_func_to_analyze_recv_msg(self, func):
        # TODO: Add log
        self.__list_func_for_analyze_msg_to_recv.append(lambda msg: func(msg))

    def close(self) -> None:
        if self.__com_port is None:
            return
        self.__com_port.close()
        self.__com_port = None
