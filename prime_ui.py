import sys, math
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi

# -------------------------------------------------------------------------------------------
# @desc - worker class for the long running task. In this case is to populate prime numbers
# -------------------------------------------------------------------------------------------
class Worker(QObject):
    finished = pyqtSignal()  # finish signal when task is finished
    sendProgressSignal = pyqtSignal(
        str
    )  # signal to be sent while task is still in progress

    # ---------------------------------------------------------------------------------
    # @desc initialize instances of the worker class. inherited from QObject
    # @params take number to be calculated to as a parameter.
    # @example if pass 17 as a parameter, it will populate prime numbers from 1 to 17
    # ---------------------------------------------------------------------------------
    def __init__(self, num_to):
        super().__init__()
        self.__num_to = num_to

    # --------------------------------------------------------------------
    # @desc run method. In this case will check if the number is prime.
    #       if prime, emit the signal and display on the textbrowser
    # --------------------------------------------------------------------
    def run(self):

        self.sendProgressSignal.emit(
            f"1, 2, 3"
        )  # emit signal to be displayed for initial 3 prime nums

        # loop through each number, find out if each number is prime.
        for num in range(3, self.__num_to + 1, 2):
            flag = False
            for i in range(2, int(math.sqrt(num)) + 1):
                if (
                    num % i
                ) == 0:  # if num is divisible by other num than itself, it's not prime
                    flag = False
                    break
                else:
                    flag = True

            if flag:  # if number is prime, emit signal to be displayed in textbrowser
                self.sendProgressSignal.emit(f"{num}")
                QApplication.processEvents()  # process queued events. this operation is thread-safe

        self.finished.emit()  # emit finished signal when task is finished


# -----------------------------------------------------------------------------
# @desc - class for the main GUI program. Contains UI and toggle color method
# -----------------------------------------------------------------------------
class GuiProgram(QDialog):

    # ---------------------------------------------------------------------------------------------------
    # @desc - initialize instances for the GUI program. Inherited from QDialog. Loads UI from .ui file
    # ---------------------------------------------------------------------------------------------------
    def __init__(self):
        super().__init__()
        self.ui = loadUi("prime_ui.ui", self)  # loads ui from .ui file
        self.ui.startButton.clicked.connect(
            self.runCalcTask
        )  # connect start button to runCalcTask() method
        self.ui.toggleButton.clicked.connect(
            self.toggle
        )  # connect toggle button to toggle() method

    # --------------------------------------------------------------------------------------------------
    # @desc - method to toggle color of the toggle button. Also display color text to the text browser
    # --------------------------------------------------------------------------------------------------
    def toggle(self):
        if self.ui.toggleButton.styleSheet() == "background-color: yellow;":
            self.ui.toggleButton.setStyleSheet("background-color: blue;")
            self.ui.numDisplay.insertPlainText("blue, ")
        else:
            self.ui.toggleButton.setStyleSheet("background-color: yellow;")
            self.ui.numDisplay.insertPlainText("yellow, ")
        self.ui.numDisplay.moveCursor(QTextCursor.End)
        self.ui.numDisplay.repaint()

    # --------------------------------------------------------------
    # @desc - method to display prime numbers to the textbrowser
    # --------------------------------------------------------------
    def reportPrimeNum(self, n):
        self.ui.numDisplay.insertPlainText(f"{n}, ")
        self.ui.numDisplay.moveCursor(QTextCursor.End)
        self.ui.numDisplay.repaint()

    # -----------------------------------------------------------------------------------------------------------
    # @desc - method to run the worker class, which is required to use QThread to run task in separated thread
    # ----------------------------------------------------------------------------------------------------------
    def runCalcTask(self):
        num_to = int(self.ui.lineEditNum.text())  # grab user input number

        self.thread = QThread()  # create thread object from QThread()

        self.worker = Worker(
            num_to
        )  # create worker object from worker class. Pass num_to as an argument

        self.worker.moveToThread(
            self.thread
        )  # move the worker object to thread in order to run it in the thread

        self.thread.started.connect(
            self.worker.run
        )  # connect run method in worker class to the starting of the thread
        self.worker.finished.connect(
            self.thread.quit
        )  # quit the thread when the thread's event loop is finished
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.sendProgressSignal.connect(
            self.reportPrimeNum
        )  # connect the sendProgressSignal to reportPrimeNum() method
        # this will call reportPrimeNum() when sending signal
        self.thread.start()  # start thread


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GuiProgram()
    window.show()
    sys.exit(app.exec())
