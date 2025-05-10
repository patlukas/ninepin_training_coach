"""This module read configuration from config.json"""
import json
import os


class ConfigReaderError(Exception):
    """
        List code:
            12-000 - FileNotFoundError - if config.json does not exist
            12-001 - ValueError - if config.json format is not correct
            12-002 - KeyError - if config doesn't have required fields
        """
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__()


class ConfigReader:
    def get_configuration(self) -> dict:
        """
        This method get configuration from config.json

        :return: dict with config
        :raises:
            ConfigReaderError
                12-000 - FileNotFoundError - if config.json does not exist
                12-001 - ValueError - if config.json format is not correct
                12-002 - KeyError - if config doesn't have required fields
        """
        try:
            file = open("config.json")
        except FileNotFoundError:
            raise ConfigReaderError("12-000", "Nie znaleziono pliku {}".format(os.path.abspath("config.json")))
        try:
            data = json.load(file)
        except ValueError:
            raise ConfigReaderError("12-001", "Niewłaściwy format danych w pliku {}"
                                    .format(os.path.abspath("config.json")))
        for key in self.__get_required_config_settings():
            if key not in data:
                raise ConfigReaderError("12-002", "KeyError - W pliku config.json nie ma: " + key)
        return data

    @staticmethod
    def __get_required_config_settings() -> list:
        list_settings = [
            "number_of_lane",
            "com_port",
            "com_timeout",
            "com_write_timeout",
            "loop_com_communication_break",
            "max_time_between_next_send"
        ]
        return list_settings
