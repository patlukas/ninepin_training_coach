from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtGui



class LogTable(QTableWidget):
    def __init__(self, log_management):
        super().__init__()
        self.__log_management = log_management
        self.__is_visible = False
        self.setRowCount(0)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["Id", "Data", "Priorytet", "Kod", "Wiadomość"])
        self.verticalHeader().setVisible(False)
        self.set_visibility(self.__is_visible)

        self.__timer_update = QTimer(self)
        self.__timer_update.timeout.connect(self.__update_table)
        self.__timer_update.start(1000)

    def set_visibility(self, show):
        self.__is_visible = show
        self.setVisible(show)
        # self.adjustSize() #?

    def __update_table(self) -> int:
        if self.__log_management is None:
            return -1

        data = self.__log_management.get_logs(250)
        vertical_scroll_bar = self.verticalScrollBar()
        current_scroll_position = vertical_scroll_bar.value()
        if current_scroll_position > 3 and not self.__is_visible:
            return 0

        self.setRowCount(0)

        for index, log in enumerate(data):
            self.insertRow(index)
            for j, val in enumerate(log):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if j < 5:
                    item.setTextAlignment(Qt.AlignCenter)
                self.setItem(index, j, item)
                if int(log[2]) == 10:
                    item.setBackground(QtGui.QColor(255, 100, 100))
                elif int(log[2]) >= 5:
                    item.setBackground(QtGui.QColor(255, 255, 225))
        self.resizeColumnsToContents()
        self.__adjust_table_width(1000)
        return 1

    def __adjust_table_width(self, max_width: int) -> None:
        total_width = 0

        for col in range(self.columnCount()):
            total_width += self.columnWidth(col)

        total_width += self.verticalHeader().width()
        total_width += self.frameWidth() * 2

        if self.verticalScrollBar().isVisible():
            total_width += self.verticalScrollBar().width()

        if total_width > max_width > 0:
            total_width = max_width

        self.setFixedWidth(total_width)
        # self.adjustSize()