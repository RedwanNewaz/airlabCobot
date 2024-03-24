import py_trees
from py_trees import common
from PyQt6.QtWidgets import QTableWidgetItem

class WriteTable(py_trees.behaviour.Behaviour):
    def __init__(self, tableWidget, cobotInputTxt, camInputTxt):
        self.tableWidget = tableWidget
        self.cobotInputTxt = cobotInputTxt
        self.camInputTxt = camInputTxt
        self.data = []
        self.clicked = False
        super(WriteTable, self).__init__("write table")
    def populate_table(self, data, header):
        # Set the table dimensions and headers
        self.tableWidget.setRowCount(len(data))  # Set number of rows
        self.tableWidget.setColumnCount(len(header))  # Set number of columns
        self.tableWidget.setHorizontalHeaderLabels(header)  # Set column headers

        for i, row in enumerate(data):
            for j, cell in enumerate(row):
                item = QTableWidgetItem(str(cell))
                self.tableWidget.setItem(i, j, item)

    def isValidInput(self, text):
        if not "," in text:
            return False
        data = list(map(float, text.split(",")))
        return len(data) == 2
    def update(self) -> common.Status:
        if not self.clicked:
            return self.status.FAILURE
        camText = self.camInputTxt.toPlainText()
        robotText = self.cobotInputTxt.text()

        if(self.isValidInput(camText) and self.isValidInput(robotText)):
            self.data.append([robotText, camText])
            header = ['cobot', 'realsense']
            self.populate_table(self.data, header)
            self.logger.info(f"updating table {robotText}")
        else:
            self.logger.error("[!] invalid input")
        self.clicked = False
        return self.status.RUNNING