from serial import Serial
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class Tasklet:
    new_card_to_reader = 0
    reader_to_exit = 1
    exit_to_reader = 2
    reader_to_store = 3
    write = 4
    validate = 5
    success = 6
    fail = 7
    def __init__(self) -> None:
        self.step = 0
        self.seq = []
        self.c_uid:int
        self.c_sec1:bytes
        self.c_sec2:bytes
        self.req_id:int
        pass
    @staticmethod
    def issueTasklet(uid, sec1, sec2, req_id):
        tasklet = Tasklet()
        tasklet.seq = [Tasklet.new_card_to_reader,Tasklet.write, Tasklet.reader_to_exit, Tasklet.success]
        tasklet.c_uid = uid
        tasklet.c_sec1 = sec1
        tasklet.c_sec2 = sec2
        tasklet.req_id = req_id
        return tasklet

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

    responseSignal = pyqtSignal(bytes,Tasklet)

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
        self.curtask:Tasklet = None
        pass

    def expect_response(self,data:bytes, task:Tasklet):
        with self.serLock:
            self.curtask = task
            self.promise = threading.Timer(5,self.timeout)
            self.promise.start()
            self.write_to_serial(data)

    def timeout(self):
        with self.serLock:
            if self.promise != None:
                self.promise = None
                self.responseSignal.emit(SerialMessageType.timeout, self.curtask)

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
                    data = self.ser.read(self.ser.in_waiting)
                    print(f"Received data: {data}")
                    if (self.promise != None):
                        self.promise.cancel() 
                        match (data):
                            case SerialMessageType.ack:
                                self.responseSignal.emit(data, self.curtask)
                                self.promise = threading.Timer(15, self.timeout)
                                self.promise.start()
                                pass
                            case SerialMessageType.inPosition:
                                self.responseSignal.emit(data, self.curtask)
                                self.promise = None
                                pass
                            case SerialMessageType.failure:
                                self.responseSignal.emit(data, self.curtask)
                                self.promise = None
                                pass
                            case _:
                                continue

            time.sleep(0.1)  # Short delay to prevent high CPU usage


if __name__ == '__main__':
    ser = SerialService('/dev/ttyAMA0')
    while True:
        pass

