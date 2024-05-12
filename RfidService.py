import numpy as np
from mfrc522.RawMFRC522 import RawMFRC522
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import threading
import json
from RPi.GPIO import cleanup

class RfidServiceMsg:
    write_done = 0
    read_done = 1
    failure = 2

class RfidService(QObject):
    rfid_signal = pyqtSignal(int, tuple)

    def __init__(self, parent: QObject) -> None:
        super().__init__(parent)
        keyfile = open('rfid_keys.json')
        self.keymgn = json.load(keyfile)
        keyfile.close()
        self.reader = RawMFRC522()
        self.wt:threading.Thread|None = None


    def write_attempt(self,data:bytes,block:int, key:list):
        pass

    
    def new_card_work(self, sec1:bytes, sec2:bytes, req_id:int):
        uid = self.reader.read_id_times(3)
        if uid != None:
            if len(uid) == 4:        
                keyC = bytes.fromhex(self.keymgn['ps_key_c'])
                keyA = bytes.fromhex(self.keymgn['ps_key_a'])
                sec1 = key_encode(sec1,uid)
                sec2 = key_encode (sec2,uid)
                req_id = req_id.to_bytes(length = 4, byteorder='little') + np.random.randint(256,size=44,dtype=np.uint8).tobytes()
                req_id = key_encode(req_id,uid)
                _, dt, _ = self.reader.write_sector_times(8*4+3,keyC,sec1,3)
                if dt != None:
                    _, dt, _ = self.reader.write_sector_times(9*4+3,keyC,sec2,3)
                    if dt != None:
                        _, dt, _ = self.reader.write_sector_times(15*4+3,keyA,req_id,3)
                        if dt != None:
                            self.rfid_signal.emit(RfidServiceMsg.write_done,(int.from_bytes(uid,"little"),))
                            self.wt = None
                            return
        self.rfid_signal.emit(RfidServiceMsg.failure, tuple())
        self.wt = None
        print('RFID Failure')
        return
    
    def verfiy_card_work(self):
        uid = self.reader.read_id_times(3)
        if uid != None:
            if len(uid) == 4:
                keyA = bytes.fromhex(self.keymgn['ps_key_a'])
                _, dt, _ = self.reader.read_sector_times(15*4+3,keyA,3)
                if dt != None:
                    dt = bytes(dt)
                    req_id = key_encode(dt[0:4],uid)
                    self.rfid_signal.emit(RfidServiceMsg.read_done,(int.from_bytes(uid,"little"),int.from_bytes(req_id,"little")))
                    print(int.from_bytes(req_id,"little"))
                    self.wt = None
                    return
        self.rfid_signal.emit(RfidServiceMsg.failure, tuple())
        print('RFID Failure')
        self.wt = None
        return

    def new_card(self,sec1:bytes,sec2:bytes,req_id:int, uid:int):
        if self.wt != None: 
            return #AppService should ensure that only one thread is running
        req_id = req_id & 0xFFFFFFFF
        uidbin = uid.to_bytes(4,'little')
        sec1 = key_encode(sec1, uidbin)
        sec2 = key_encode(sec2, uidbin)
        self.wt = threading.Thread(target=self.new_card_work,args=(sec1,sec2,req_id))
        self.wt.start()

    def verify_card(self):
        if self.wt != None: 
            return
        self.wt = threading.Thread(target=self.verfiy_card_work)
        self.wt.start()
    
    def __del__(self):
        cleanup()

def key_encode(data:bytes, uid:bytes) -> bytes:
    if (len(uid) != 4): 
        raise ValueError("Data must be a multiple of 4")
    npuid = np.frombuffer(uid,dtype=np.uint8)
    npuid = np.tile(npuid,len(data)//4)
    npdata = np.frombuffer(data,dtype=np.uint8)
    result = np.bitwise_xor(npuid,npdata)
    return result.tobytes()

def printbin(binobj):
    for i in range(len(binobj)):
        print(f'{binobj[i]:02X},',end='')
        if i % 16 == 15:
            print()

def init_card():
    rs = RfidService(None)
    key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
    keymgn = json.load(open('rfid_keys.json'))
    keyA = bytes.fromhex(keymgn['ps_key_a'])
    keyC = bytes.fromhex(keymgn['ps_key_c'])
    keyD = bytes.fromhex(keymgn['ps_key_e'])
    for i in range (16):
        if i >= 8 and i <= 9:
            _, dt, _ = rs.reader.setkey_times(i*4+3,key,2,keyC,keyD,b'\x7f\x07\x88')
            pass
        else:
            _, dt, _ = rs.reader.setkey_times(i*4+3,key,2,keyA,keyA)
        
        if dt != None:
            print(f'Write to sector {i} success')
        else:
            print(f'Write to sector {i} failed')
        pass

def dump_info():
    rs = RfidService(None)
    keymgn = json.load(open('rfid_keys.json'))
    keyA = bytes.fromhex(keymgn['ps_key_a'])
    keyC = bytes.fromhex(keymgn['ps_key_c'])
    keyD = bytes.fromhex(keymgn['ps_key_e'])
    for i in range (16):
        if i >= 8 and i <= 9:
            _, dt, _ = rs.reader.read_sector_times(i*4+3,keyC,3)
            pass
        else:
            _, dt, _ = rs.reader.read_sector_times(i*4+3,keyA,3)
        
        if dt != None:
            print(f'Sector {i}')
            printbin(dt)
        else:
            print(f'Read from sector {i} failed')
        pass

if __name__ == '__main__':
    # print(key_encode(bytes([1,2,3,4,5,6,7,8]),bytes([223,132,130,230])))

    # key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

    # rs = RfidService(None)
    # obj = rs.reader.read_id_times(3)
    # if isinstance(obj,bytes):
    #     print(obj.hex())
    # else:
    #     print('Not Detected')

    rs = RawMFRC522(bus = 0, device = 1, pin_rst = 18)
    rs2 = RawMFRC522(bus = 0, device = 0, pin_rst = 22)
    for i in range(50):
        obj = rs.read_id_times(3)
        obj2 = rs2.read_id_times(3)
        print('1:',end='')
        if isinstance(obj,bytes):
            print(obj.hex())
        else:
            print('Not Detected')
        print('2:',end='')
        if isinstance(obj2,bytes):
            print(obj2.hex())
        else:
            print('Not Detected')
    cleanup()
    # keymgn = json.load(open('rfid_keys.json'))
    # keyA = bytes.fromhex(keymgn['ps_key_a'])
    # keyB = keyA
    # id, data, _= rs.reader.read_sector_times(63,key,20)
    # printbin(data)
    # rs.reader.setkey_times(63,key,5,keyA,keyB)

    # id, data, _= rs.reader.read_sector_times(63,key,20)
    # if (data != None): 
    #     printbin(data)
    #     rdt = np.random.randint(256,size=48,dtype=np.uint8).tobytes()
    #     id, data ,_= rs.reader.write_sector_times(63,key,rdt,20)
    #     if (data != None):
    #         id, data, _ = rs.reader.read_sector_times(63,key,20)
    #         if (data != None):
    #             printbin(data)
    # rdt = np.random.randint(256,size=48,dtype=np.uint8)
    # printbin(rdt.tobytes())
    
    # init_card()

    # dump_info()

    # f = open('710a20.dump','rb')

    # cd_dump = f.read()

    # f.close()

    # sec1 = cd_dump[8*64:8*64+48]
    # sec2 = cd_dump[9*64:9*64+48]
    # uid = cd_dump[0:4]


    # sec1 = key_encode(sec1,uid)
    # sec2 = key_encode(sec2,uid)

    # print ('uid')
    # print(uid.hex())
    # print('sec1')
    # printbin(sec1)

    # print('sec2')
    # printbin(sec2)

    # req_id = np.random.randint(256,size=4,dtype=np.uint8).tobytes()

    # rs.new_card(sec1,sec2,652)
    # rs.verify_card()

    pass

        
    