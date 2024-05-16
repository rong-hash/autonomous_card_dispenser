from serial import Serial
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


class SerialMessageType:
    storeToReader   =  b'\x11'
    readerToStore   = b'\x12'
    exitToReader    = b'\x14'
    readerToExit    = b'\x18'
    cardDetect   = b'\x17'
    ack          = b'\x20'
    inPosition   = b'\x2A'
    failure      = b'\x2F'
    overflow    = b'\x28'
    storeToReader_nr   =  b'\x41'
    readerToStore_nr   = b'\x42'
    exitToReader_nr    = b'\x44'
    readerToExit_nr    = b'\x48'
    homeposition = b'\x49'
    timeout      = b'\xFF'


class SerialService (QObject):

    responseSignal = pyqtSignal(bytes)

    def __init__(self, device:str) -> None:
        super().__init__(parent=None)
        self.ser = Serial(device,115200)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.serLock = threading.Lock()
        self._pollThread = threading.Thread(target=self.read_from_serial)
        self._pollThread.daemon = True
        self._pollThread.start()
        self.promise:threading.Timer = None
        pass

    def expect_response(self,data:bytes):
        with self.serLock:
            if self.promise != None:
                print("Serial is Busy")
                return
            self.promise = threading.Timer(5,self.timeout)
            self.promise.start()
            self.write_to_serial(data)
    
    def order(self, data:bytes):
        with self.serLock:
            self.write_to_serial(data)

    def timeout(self):
        with self.serLock:
            if self.promise != None:
                self.promise = None
                self.responseSignal.emit(SerialMessageType.timeout)

    def write_to_serial(self,data:bytes):
        self.ser.write(data)  # Encode string data to bytes and write to serial port

    # Function to read data from serial port on a separate thread
    def read_from_serial(self):
        # while True:
        #     data = self.ser.read(128)
        #     if b'EOF' in data:
        #         print(data)
        #         break
        #     print(data)
        # ser.close()
        while True:
            with self.serLock:
                if self.ser.in_waiting > 0:
                    data = self.ser.read(1)
                    print(f"Received data: {data}")
                    if (self.promise != None):
                        self.promise.cancel() 
                        match (data):
                            case SerialMessageType.ack:
                                self.responseSignal.emit(data)
                                self.promise = threading.Timer(40, self.timeout)
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
                            case SerialMessageType.overflow:
                                self.responseSignal.emit(data)
                                self.promise = None
                                pass
                            case _:
                                continue

            time.sleep(0.1)  # Short delay to prevent high CPU usage


if __name__ == '__main__':
    ser = SerialService('/dev/ttyAMA0')
    ser.write_to_serial(SerialMessageType.exitToReader)
    while True:
        pass

