"""This module creates a log file and writes the logs to a log file"""
import os
from datetime import datetime


class LogManagement:
    def __init__(self):
        if not os.path.exists("logs") or not os.path.isdir("logs"):
            os.makedirs("logs")
        self.__name = "logs/" + self.__get_file_name()
        open(self.__name, "w").close()
        self.__index = 0
        self.__log_list = []

    def __get_file_name(self) -> str:
        filename = "logs_{}.log".format(self.__get_datetime())
        return filename

    @staticmethod
    def __get_datetime(with_ms: bool = False) -> str:
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        hour = now.strftime("%H")
        minute = now.strftime("%M")
        second = now.strftime("%S")
        datetime_str = "{}_{}_{}__{}_{}_{}".format(year, month, day, hour, minute, second)
        if with_ms:
            millisecond = now.strftime("%f")[:3]
            datetime_str += "_{}".format(millisecond)
        return datetime_str

    def add_log(self, priority, code: str, message: str) -> None:
        if type(code) != str:
            code = str(code)
        if type(message) != str:
            message = str(message)
        self.__index += 1
        date = self.__get_datetime(True)
        data = [self.__index, date, priority, code, message]
        if priority > 2:
            self.__log_list.append(data)
        new_line = "{}.\t{}\t{}\t{}\t{}".format(self.__index, date, priority, code.ljust(14), message)
        if priority > 3:
            print(new_line)

        if not os.path.exists("logs") or not os.path.isdir("logs"):
            os.makedirs("logs")
        with open(self.__name, "a") as file:
            file.write(new_line + "\n")

        if len(self.__log_list) > 500:
            self.__log_list.pop(0)

    def get_logs(self, number_logs: int):
        """
        This func return 'number_logs' logs which have priority is minimum min_priority

        :param number_logs: maximum number of logs can be returned, but errors will be additional returned
        :return: list[logs]
        """
        data = []
        for log in self.__log_list[::-1]:
            if len(data) >= number_logs:
                break
            data.append(log)
        return data
