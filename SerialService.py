from serial import Serial
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class SerialMessageType:
    storeToReader   =  b'\x11'
    readerToStore   = b'\x12'
    exitToReader    = b'\x14'
    readerToExit    = b'\x18'
    ack          = b'\x20'
    inPosition   = b'\x2A'
    failure      = b'\x2F'
    timeout      = b'\xFF'


class SerialService (QObject):

    responseSignal = pyqtSignal(bytes)

    def __init__(self, device:str) -> None:
        super().__init__(parent=None)
        self.ser = Serial(device,9600)
        self.serLock = threading.Lock()
        self._pollThread = threading.Thread(target=self.read_from_serial)
        self._pollThread.daemon = True
        self._pollThread.start()
        self.promise:threading.Timer = None
        pass

    def expect_response(self,data:bytes):
        with self.serLock:
            self.promise = threading.Timer(5,self.timeout)
            self.promise.start()
            self.write_to_serial(data)

    def timeout(self):
        with self.serLock:
            self.promise = None
            self.responseSignal.emit(SerialMessageType.timeout)

    def write_to_serial(self,data:bytes):
        self.ser.write(data)  # Encode string data to bytes and write to serial port

    # Function to read data from serial port on a separate thread
    def read_from_serial(self):
        while True:
            with self.serLock:
                if self.ser.in_waiting > 0:
                    data = self.ser.read()
                    print(f"Received data: {data}")
                    if (self.promise != None):
                        self.promise.cancel() 
                        match (data):
                            case SerialMessageType.ack:
                                self.responseSignal.emit(data)
                                self.promise = threading.Timer(10, self.timeout)
                                self.promise.start()
                                pass
                            case SerialMessageType.inPosition:
                                self.responseSignal.emit(data)
                                self.promise = None
                                pass
                            case SerialMessageType.failure:
                                self.responseSignal.emit(data)
                                self.promise = None
                                pass
                            case _:
                                continue

            time.sleep(0.1)  # Short delay to prevent high CPU usage




