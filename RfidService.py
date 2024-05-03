import numpy as np
from mfrc522.RawMFRC522 import RawMFRC522
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import threading
import json
from RPi.GPIO import cleanup

class RfidService(QObject):
    rfid_write_done = pyqtSignal(int)
    rfid_failure = pyqtSignal()
    rfid_read_done = pyqtSignal(int,int)

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
        if uid == None:
            self.rfid_failure.emit()
            print('RFID Failure')
            return
        if len(uid) != 4:
            self.rfid_failure.emit()
            print('RFID Failure')
            return            
        keyC = bytes.fromhex(self.keymgn['ps_key_c'])
        keyA = bytes.fromhex(self.keymgn['ps_key_a'])
        sec1 = key_encode(sec1,uid)
        sec2 = key_encode (sec2,uid)
        req_id = req_id.to_bytes(length = 4, byteorder='little') + np.random.randint(256,size=44,dtype=np.uint8).tobytes()
        req_id = key_encode(req_id,uid)
        _, dt, _ = self.reader.write_sector_times(8*4+3,keyC,sec1,3)
        if dt == None:
            self.rfid_failure.emit()
            print('RFID Failure 1')
            return
        _, dt, _ = self.reader.write_sector_times(9*4+3,keyC,sec2,3)
        if dt == None:
            self.rfid_failure.emit()
            print('RFID Failure 2')
            return
        _, dt, _ = self.reader.write_sector_times(15*4+3,keyA,req_id,3)
        if dt == None:
            self.rfid_failure.emit()
            print('RFID Failure 4')
            return
        self.rfid_write_done.emit(int.from_bytes(uid,"little"))
        self.wt = None
    
    def verfiy_card_work(self):
        uid = self.reader.read_id_times(3)
        if uid == None:
            self.rfid_failure.emit()
            print('RFID Failure')
            return
        if len(uid) != 4:
            self.rfid_failure.emit()
            print('RFID Failure')
            return
        keyA = bytes.fromhex(self.keymgn['ps_key_a'])
        _, dt, _ = self.reader.read_sector_times(15*4+3,keyA,3)
        if dt == None:
            self.rfid_failure.emit()
            print('RFID Failure 4')
            return
        dt = bytes(dt)
        req_id = key_encode(dt[0:4],uid)
        self.rfid_read_done.emit(int.from_bytes(uid,"little"),int.from_bytes(req_id,"little"))
        print(int.from_bytes(req_id,"little"))
        self.wt = None
        pass

    def new_card(self,sec1:bytes,sec2:bytes,req_id:int):
        if self.wt != None: 
            return #AppService should ensure that only one thread is running
        req_id = req_id & 0xFFFFFFFF
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
    rs = RfidService(None)
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

    f = open('710a20.dump','rb')

    cd_dump = f.read()

    f.close()

    sec1 = cd_dump[8*64:8*64+48]
    sec2 = cd_dump[9*64:9*64+48]
    uid = cd_dump[0:4]


    sec1 = key_encode(sec1,uid)
    sec2 = key_encode(sec2,uid)

    # print ('uid')
    # print(uid.hex())
    # print('sec1')
    # printbin(sec1)

    # print('sec2')
    # printbin(sec2)

    # req_id = np.random.randint(256,size=4,dtype=np.uint8).tobytes()

    # rs.new_card(sec1,sec2,652)
    rs.verify_card()

    pass

        
    