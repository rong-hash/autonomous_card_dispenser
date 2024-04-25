from mfrc522.RawMFRC522 import RawMFRC522
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class RfidService(QObject):
    rfid_write_done = pyqtSignal()
    rfid_read_done = pyqtSignal(bytes)

    def __init__(self, parent: QObject | None = ...) -> None:
        super().__init__(parent)
        self.reader = RawMFRC522()

    @pyqtSlot(int)
    def write_rfid(self, data: int):
        self.reader(data)
        self.rfid_write_done.emit()