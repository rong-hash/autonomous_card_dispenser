import numpy as np
# from mfrc522.RawMFRC522 import RawMFRC522
# from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
# import threading

# class RfidService(QObject):
#     rfid_write_done = pyqtSignal()
#     rfid_read_done = pyqtSignal(bytes)

#     def __init__(self, parent: QObject | None = ...) -> None:
#         super().__init__(parent)
#         self.reader = RawMFRC522()

#     def write_attempt(self,data:bytes,block:int, key:list):
#         pass

#     @pyqtSlot(int)
#     def write_rfid(self, data: int):
#         self.reader(data)
#         self.rfid_write_done.emit()

def key_encode(data:bytes, uid:bytes) -> bytes:
    if (len(uid) != 4): raise ValueError()
    npuid = np.frombuffer(uid,dtype=np.uint8)
    npuid = np.repeat(npuid,len(data)//4)
    npdata = np.frombuffer(data,dtype=np.uint8)
    result = np.bitwise_xor(npuid,npdata)
    return result.tobytes()
    
    pass

if __name__ == '__main__':
    print(key_encode(bytes([1,2,3,4,5,6,7,8]),bytes([223,132,130,230])))