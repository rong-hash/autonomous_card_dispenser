import struct

class NetMessageType:
    QRAuthResponse = b'\x10'
    QRAuthRequest = b'\x11'
    FRAuthResponse = b'\x12'
    FRAuthRequest = b'\x13'
    InitNotification = b'\x20'
    IssueNotification = b'\x21'
    ReturnNotification = b'\x22'
    RegisterNotification = b'\x23'
    ServerAck = b'\x2F'
    RemoteCmd = b'\x30'
    TermAck = b'\x3F'
    LastwillMsg = b'\x50'
class ErrCode:
    success = 0
    invalid = 1
    expired = 2

class ICInfo:
    uid:int
    room:int
    sec1:bytes
    sec2:bytes
    


class QRAuthResponseMsg():
    id:int
    err:ErrCode
    card:ICInfo = ICInfo()
    @staticmethod
    def toBytes(req_id, err,card) -> bytes:
        return struct.pack(
            '=1sIi',
            NetMessageType.QRAuthResponse,
            req_id,
            err) + struct.pack(
                'II64s64s',
                card.uid,
                card.room,
                card.sec1,
                card.sec2
            )

class QRAuthRequestMsg():
    id:int
    token:bytes
    @staticmethod
    def toBytes(token) -> bytes:
        return struct.pack(
            '=1sI32s',
            NetMessageType.QRAuthRequest,
            0x0 , 
            token)


class FRAuthResponseMsg():
    id:int
    err:ErrCode
    card:ICInfo
    @staticmethod
    def toBytes(req_id, err,card) -> bytes:
        return struct.pack(
            '=1sIi',
            NetMessageType.FRAuthResponse,
            req_id,
            err) + struct.pack(
                'II64s64s',
                card.uid,
                card.room,
                card.sec1,
                card.sec2
            )  

class FRAuthRequestMsg():
    id:int
    img:bytes
    @staticmethod
    def toBytes(img) -> bytes:
        return struct.pack(
            '=1sI',
            NetMessageType.FRAuthRequest,
            0x0) + img

class ServerAckMsg():
    err:ErrCode
    @staticmethod
    def toBytes(err:ErrCode) -> bytes:
        return struct.pack(
            '=1sI',
            NetMessageType.ServerAck,
            err) 
    
def unpackMsg(raw:bytes) -> object|None:
    if (len(raw) == 0): return None
    msgType = raw[0:1]
    obj = None
    match(msgType):
        case NetMessageType.QRAuthResponse:
            if len(raw) < 9: return None
            obj = QRAuthResponseMsg()
            obj.id, obj.err = struct.unpack('Ii',raw[1:9])
            if obj.err == ErrCode.success:
                obj.card = ICInfo()
                obj.card.uid, obj.card.room, obj.card.sec1, obj.card.sec2 = struct.unpack('II64s64s',raw[9:])
            
            pass
        case NetMessageType.QRAuthRequest:
            if len(raw) < 37: return None
            obj = QRAuthRequestMsg()
            obj.id = struct.unpack('I',raw[1:5])
            obj.token = raw[5:]
            pass
        case NetMessageType.FRAuthResponse:
            if len(raw) < 9: return None
            obj = FRAuthResponseMsg()
            obj.id, obj.err = struct.unpack('Ii',raw[1:9])
            if obj.err == ErrCode.success:
                obj.card = ICInfo()
                obj.card.uid, obj.card.room, obj.card.sec1, obj.card.sec2 = struct.unpack('II64s64s',raw[9:])
            pass
        case NetMessageType.FRAuthRequest:
            if len(raw) < 5: return None
            obj = FRAuthRequestMsg()
            obj.id = struct.unpack('I',raw[1:5])
            obj.img = raw[5:]
            pass
        case NetMessageType.InitNotification:
            pass
        case NetMessageType.IssueNotification:
            pass
        case NetMessageType.ReturnNotification:
            pass
        case NetMessageType.RegisterNotification:
            pass
        case NetMessageType.ServerAck:
            if len(raw) < 5: return None
            obj = ServerAckMsg()
            obj.err = struct.unpack('i',raw[1:5])
            pass
        case NetMessageType.RemoteCmd:
            pass
        case NetMessageType.TermAck:
            pass
        case NetMessageType.LastwillMsg:
            pass
        case _:
            return None
    return obj

if __name__ == '__main__':
    btobj = QRAuthRequestMsg.toBytes(b'abcd0000000000000000000000000000')
    print(btobj)
    print(len(btobj))