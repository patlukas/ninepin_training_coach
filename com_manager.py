import serial
from typing import Union

class ComManager:
    def __init__(self, port_name: str, timeout: Union[int, float, None], write_timeout: Union[int, float, None]):
        self.__port_name = port_name
        self.__bytes_to_send = b""
        self.__bytes_to_recv = b""
        self.__com_port = self.__create_port(timeout, write_timeout)

    def __create_port(self, timeout: Union[float, None], write_timeout: Union[float, None]) -> serial.Serial:
        try:
            com_port = serial.Serial(self.__port_name, 9600, timeout=timeout, write_timeout=write_timeout)
            return com_port
        except ValueError as e:
            print("ValueError", e)
        except serial.SerialException as e:
            print("serial.SerialException", e)

    def read(self) -> bytes:
        if self.__com_port is None:
            return b""

        in_waiting = self.__com_port.in_waiting
        if in_waiting == 0:
            return b""

        data_read = self.__com_port.read(in_waiting)
        self.__bytes_to_recv += data_read

        try:
            data_read.decode('Windows-1250')
        except UnicodeError as e:
            print("UnicodeError", e)

        if b"\r" not in self.__bytes_to_recv:
            return b""

        index = self.__bytes_to_recv.rindex(b"\r") + 1
        data_received, self.__bytes_to_recv = self.__bytes_to_recv[:index], self.__bytes_to_recv[index:]
        return data_received

    def send(self) -> (int, bytes):
        if self.__com_port is None:
            return -2, b""

        if self.__com_port.out_waiting > 0 or self.__bytes_to_send == b"" or b"\r" not in self.__bytes_to_send:
            return 0, b""

        try:
            index_first_special_sign = self.__bytes_to_send.index(b"\r") + 1
            number_sent_bytes = self.__com_port.write(self.__bytes_to_send[:index_first_special_sign])
            sent_bytes = self.__bytes_to_send[:number_sent_bytes]
            self.__bytes_to_send = self.__bytes_to_send[number_sent_bytes:]

            return len(sent_bytes), sent_bytes
        except serial.SerialTimeoutException as e:
            return -1, b""

    def add_bytes_to_send(self, new_bytes_to_send: bytes) -> int:
        if type(new_bytes_to_send) != bytes:
            print("Wrong type of data to send: '{}' have type '{}'".format(new_bytes_to_send, type(new_bytes_to_send).__name__))
        else:
            if new_bytes_to_send[-1:] != b"\r":
                print("Wrong end of data to send, should have '\r' as last sign: '{}'".format(new_bytes_to_send[-1:]))
            else:
                if new_bytes_to_send not in self.__bytes_to_send:
                    self.__bytes_to_send += new_bytes_to_send
        return len(self.__bytes_to_send)

    def close(self) -> None:
        if self.__com_port is None:
            print("Port {} is closed or not was be created, so I can't close port".format(self.__port_name))
        self.__com_port.close()
        self.__com_port = None
