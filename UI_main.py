import UI_Qt.WITRN_UI as Design
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog
import Transfer
import csv


class UiApp(QtWidgets.QMainWindow, Design.Ui_MainWindow, QtCore.QTimer, QtCore.QThread):
    timer = QtCore.QTimer()
    timer_file = QtCore.QTimer()

    volts: float
    current: float
    temp: float
    watt: float
    time_save: float

    flag_temp = True

    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.ON_Button.clicked.connect(self.OKButClic)
        self.Start_file.clicked.connect(self.StartButClic)
        self.searchBut.clicked.connect(self.file_Search)

        self.typetempdat.stateChanged.connect(self.TempBox)
        self.typetempdat.setText("Inner temperature")
        self.typetempdat.setChecked(True)

        self.tr = Transfer.Data(self)
        self.tr.voltSG.connect(self.PR)

        self.timer_file.timeout.connect(self.timeout_file)

    def TempBox(self):
        if self.typetempdat.isChecked():
            self.typetempdat.setText("Inner temperature")
            self.flag_temp = True
        else:
            self.typetempdat.setText("External temperature")
            self.flag_temp = False

    def PR(self, ToTaL, RuN_TiMe, VoLtAgE, CuRrEnT, Dp, Dn, Wh, Ah, temOut, temIn):
        self.voltageLab.setText(str(round(VoLtAgE, 3)) + " V")
        self.volts = round(VoLtAgE, 3)

        self.currentLab.setText(str(round(CuRrEnT, 3)) + " A")
        self.current = round(CuRrEnT, 3)

        self.wattLab.setText(str(round(VoLtAgE * CuRrEnT, 3)) + " W")
        self.watt = round(VoLtAgE * CuRrEnT, 3)

        if self.flag_temp:
            self.temperature.setText("C: " + str(round(temIn, 2)))
            self.temp = round(temIn, 2)
        else:
            self.temperature.setText("C: " + str(round(temOut, 2)))
            self.temp = round(temOut, 2)

        self.D_plus.setText("D+: " + str(round(Dp, 2)))
        self.D_min.setText("D-: " + str(round(Dn, 2)))

        self.accumEnerg.setText(str(round(Wh, 3)) + "Ah")
        self.accumCapas.setText(str(round(Ah, 3)) + "Wh")

        self.timeBoot.setText("R: " + ToTaL)
        self.timeRec.setText("T: " + RuN_TiMe)
        self.time_save = ToTaL

    def OKButClic(self) -> None:
        if(self.ON_Button.text() == 'Connect'):
            self.ON_Button.setText("Disconnect")
            print(self.ModelComboBox.currentText())
            if self.ModelComboBox.currentText() == "A2":
                self.tr.runA2()
            if self.ModelComboBox.currentText() == "U3":
                self.tr.runU3()
            if self.ModelComboBox.currentText() == "A2L":
                self.tr.runA2L()
            return

        if(self.ON_Button.text() == 'Disconnect'):
            self.ON_Button.setText("Connect")
            Transfer.QThread.exit()
            return

    def file_Search(self):
        self.file = QFileDialog.getOpenFileName()
        print(self.file[0])

    def timeout_file(self):
        self.Start_file.setDisabled(False)
        list = []
        list.append(self.time_save)
        list.append(self.volts)
        list.append(self.current)
        list.append(self.watt)
        list.append(self.temp)
        with open(self.file[0], 'a') as F:
            self.Fwriter = csv.writer(F)
            self.Fwriter.writerow(list)

    def StartButClic(self) -> None:
        if(self.Start_file.text() == 'Start'):
            self.Start_file.setText("Stop")
            self.timer_file.start(self.recInterList.value() * 1000)
            self.Start_file.setEnabled(False)
            return


        if(self.Start_file.text() == 'Stop'):
            self.Start_file.setText("Start")
            self.timer_file.stop()
            return



def main():
    app = QtWidgets.QApplication(sys.argv)
    window = UiApp()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
