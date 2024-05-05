from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QTranslator
from PyQt5.QtQuick import QQuickItem
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from CameraService import QPicamera2Item, QPicamera2ItemService
from NetService import NetService, NetSignalType, ConnectionStatus
from NetMessageUtil import *
from threading import Timer, Lock
from SerialService import SerialService, SerialMessageType
from RfidService import RfidService, RfidServiceMsg

class Forms():
    RootWindow = 0
    MainScreen = 1
    Auth = 2
    Process = 3

class Transition():
    Pop = 0
    Push = 1

class ProcessSigs:
    #   Status Define:
    #   0:Success
    #   1:Failed_Timed_Out
    #   2:Failed_Bad_Identity
    #   3:Failed_Bad_Card
    #   4:Failed_Mechanical_Failure
    #   5:Failed_Hardware_Fault
    #   6:Authorized
    #   7:Request Expired
    #   8:Prepare
    #   9:Insert
    #   10:Not Detected
    #   11:Invalid Card
    #   12:Detected
    success = 0
    failed_timeout = 1
    failed_bad_identity = 2
    failed_bad_card = 3
    failed_mechanical = 4
    failed_hardware = 5
    authorized = 6
    expired = 7
    prepare = 8
    insert = 9
    not_detected = 10
    invalid = 11
    detected = 12



class TimeoutCheck:
    def __init__(self, handler, timeout) -> None:
        self._finished = False
        self._timedout = False
        self._lock = Lock()
        self._handler = handler
        self._timeiv = timeout
        self._timer = Timer(timeout, self.gen_handler)
        pass

    def start(self):
        self._timer.start()

    def gen_handler(self):
        with self._lock:
            if not self._finished:
                self._timedout = True
                self._handler()
        pass

    def check_timeout_on_finished(self):
        with self._lock:
            self._finished = True
            rtv = self._timedout
            self._timedout = True
            self._timer.cancel()
            return rtv
        
    def reset(self):
        with self._lock:
            self._timedout = False
            self._finished = False
            self._timer = Timer(self._timeiv,self.gen_handler)
        pass



class QMLSigHub(QObject):
    videoFeedStart = pyqtSignal(QPicamera2Item)
    videoFeedStop = pyqtSignal()
    loadForm = pyqtSignal(str,int,name = 'loadForm')
    resultReceived = pyqtSignal(int,name = "resultReceived")


            
    

    
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.formStatus = Forms.MainScreen
        self.netService:NetService = None
        self.serialService:SerialService = None
        self.rfidService:RfidService = None
        self.qrInfo:bytes = None
        self.faceInfo:bytes = None
        self.authTimeout = TimeoutCheck(self.returnToMain,30)
        self.lang = "en"
        self.app = None
        self.engine = None
        self.trans = QTranslator()
        self.trans.load('lang/mls.qm')

        self.inprocess:EDGeneral = None
        return
    
    def registerEnginee(self, app:QGuiApplication, engine:QQmlApplicationEngine):
        self.app = app
        self.engine = engine

    def registerQML(self,root:QObject):
        root.newFormLoaded.connect(self.newFormLoadHandle)
        root.langChanged.connect(self.langChangedHandle)
        root.cleanForm.connect(self.cleanHandle)
        root.returnToMain.connect(self.returnToMainAsync)

    def registerCameeraService(self,obj:QPicamera2ItemService):
        self.videoFeedStart.connect(obj.register_camearitem)
        self.videoFeedStop.connect(obj.quit)
        obj.qr_decode.connect(self.QRDecodeHandle)
        obj.face_detect.connect(self.FaceDetectedHandle)

    def registerNetService(self, obj:NetService):
        obj.net_message.connect(self.NetMessageHandle)
        self.netService = obj
        self.netService.run()

    def registerSerialService(self, obj:SerialService):
        # obj.responseSignal.connect(self.SerialResponseHandle)
        self.serialService = obj

    def registerRfidService(self, obj:RfidService):
        # obj.rfid_signal.connect(self.RfidResponseHandle)
        self.rfidService = obj
        
    def delayedReturn(self, delay:int):
        self._delayThread = Timer(delay, self.returnToMain)
        self._delayThread.start()
        pass


    def returnToMain(self):
        self.cleanHandle()
        self.loadForm.emit("MainScreen.qml",Transition.Pop) #Lock is not necessary here.

    @pyqtSlot()
    def returnToMainAsync(self):
        if not self.authTimeout.check_timeout_on_finished():
            self.returnToMain()
    

    
    @pyqtSlot()
    def cleanHandle(self):
        match self.formStatus:
            case Forms.MainScreen:
                pass
            case Forms.Auth:
                self.videoFeedStop.emit()
                pass
            case Forms.Process:
                pass
            case _:
                raise RuntimeError("Undefined Form ID")

    @pyqtSlot(QQuickItem)
    def newFormLoadHandle(self,obj:QQuickItem):
        formID:int = obj.property("formID")
            
        self.formStatus = formID

        match self.formStatus:
            case Forms.MainScreen:
                pass
            case Forms.Auth:
                cameraViewObj:QPicamera2Item = obj.findChild(QPicamera2Item,"cameraViewItem")
                self.videoFeedStart.emit(cameraViewObj)
                self.authTimeout.reset()
                self.authTimeout.start()
                pass
            case Forms.Process:
                if (self.qrInfo != None):
                    print('[MQTT] Publishing Request')
                    msg = QRAuthRequestMsg()
                    msg.token = self.qrInfo
                    self.inprocess = EDIssue(self, msg)
                    self.inprocess.start()
                    # self.netService.ExpectResponseSlot(
                    #     QRAuthRequestMsg.toBytes(self.qrInfo),
                    #     NetMessageType.QRAuthResponse,
                    #     5)          
                    self.qrInfo = None
                elif (self.faceInfo != None):
                    print('[MQTT] Publishing Request')
                    msg = FRAuthRequestMsg()
                    msg.img = self.faceInfo
                    self.inprocess = EDIssue(self, msg)
                    self.inprocess.start()
                    # self.netService.ExpectResponseSlot(
                    #     FRAuthRequestMsg.toBytes(self.faceInfo),
                    #     NetMessageType.FRAuthResponse,
                    #     5)          
                    self.faceInfo = None
                else:
                    self.inprocess = EDReturn(self)
                    self.inprocess.start()
                #self.resultReceived.emit(2)
                pass
            case _:
                raise RuntimeError("Undefined Form ID")
            
    @pyqtSlot(str)
    def langChangedHandle(self, lang:str):
        if (lang != self.lang):
            self.lang = lang
            match (lang):
                case 'en':
                    self.app.removeTranslator(self.trans)
                    self.engine.retranslate()
                case 'zh':
                    self.app.installTranslator(self.trans)
                    self.engine.retranslate()

                case _:
                    raise RuntimeError("Unsupported Language")
            
    @pyqtSlot(bytes)
    def QRDecodeHandle(self, code:bytes):
        if not self.authTimeout.check_timeout_on_finished():
            self.qrInfo = code
            self.cleanHandle()
            self.loadForm.emit("Process.qml",Transition.Push)
        pass

    @pyqtSlot(bytes)
    def FaceDetectedHandle(self, code:bytes):
        if not self.authTimeout.check_timeout_on_finished():
            self.faceInfo = code
            self.cleanHandle()
            self.loadForm.emit("Process.qml",Transition.Push)
        pass

    @pyqtSlot(int,object)
    def NetMessageHandle(self, status:int, data:int|bytes|None):
    
    #   Status Define:
    #   0:Success
    #   1:Failed_Timed_Out
    #   2:Failed_Bad_Identity
    #   3:Failed_Bad_Card
    
        match (status):
            case NetSignalType.connection:
                if data == ConnectionStatus.disconnected:
                    # self.netService.reset()
                    print("[MQTT] Disconnected")
                else:
                    print("[MQTT] Connected")
                pass




class EDGeneral(QObject):
    def __init__(self, source:QMLSigHub, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.sighub = source

    def start(self):
        pass
    

class EDIssue(EDGeneral):
    def __init__(self, source:QMLSigHub, msg:QRAuthRequestMsg|FRAuthRequestMsg) -> None:
        super().__init__(source)
        self.msg = msg

    def start(self):
        self.sighub.netService.net_message.connect(self.verifyHandle)

        if isinstance(self.msg,QRAuthRequestMsg):
            bin = QRAuthRequestMsg.toBytes(self.msg.token)
            self.sighub.netService.ExpectResponseSlot(bin,NetMessageType.QRAuthResponse,5)
        else:
            bin = FRAuthRequestMsg.toBytes(self.msg.img)
            self.sighub.netService.ExpectResponseSlot(bin,NetMessageType.FRAuthResponse,5)

    @pyqtSlot(int,object)
    def verifyHandle(self, status:int, data:int|bytes|None):
        if status == NetSignalType.response:
            obj = unpackMsg(data)
            if obj == None: return
            if isinstance(obj, QRAuthResponseMsg) or isinstance(obj,FRAuthResponseMsg):

                match (obj.err):
                    case ErrCode.success:
                        self.card = obj.card
                        self.req_id = obj.id
                        self.sighub.serialService.responseSignal.connect(self.preWriteHandle)
                        self.sighub.resultReceived.emit(ProcessSigs.authorized)
                        self.sighub.serialService.expect_response(SerialMessageType.storeToReader)
                    case ErrCode.invalid:
                        self.sighub.resultReceived.emit(ProcessSigs.failed_bad_identity)
                        self.sighub.delayedReturn(5)
                    case ErrCode.expired:
                        self.sighub.resultReceived.emit(ProcessSigs.expired)
                        self.sighub.delayedReturn(5)
                    case _: 
                        raise RuntimeError("Unknown Response")
                
                self.sighub.netService.net_message.disconnect(self.verifyHandle)

                
        elif status == NetSignalType.timeout:
            self.sighub.resultReceived.emit(ProcessSigs.failed_timeout)
            self.sighub.delayedReturn(5)
            self.sighub.netService.net_message.disconnect(self.verifyHandle)
        pass
    
    @pyqtSlot(bytes)
    def preWriteHandle(self, data:bytes):
        match (data):
            case SerialMessageType.ack:
                pass
            case SerialMessageType.inPosition:
                self.sighub.rfidService.rfid_signal.connect(self.writeHandle)
                print('write triggerred')
                self.sighub.resultReceived.emit(ProcessSigs.prepare)
                self.sighub.rfidService.new_card(self.card.sec1,self.card.sec2,self.req_id, self.card.uid)
                self.sighub.serialService.responseSignal.disconnect(self.preWriteHandle)
            case SerialMessageType.failure:
                self.sighub.resultReceived.emit(ProcessSigs.failed_mechanical)
                self.sighub.delayedReturn(5)
                self.sighub.serialService.responseSignal.disconnect(self.preWriteHandle)
            case SerialMessageType.timeout:
                self.sighub.resultReceived.emit(ProcessSigs.failed_mechanical)
                self.sighub.delayedReturn(5)
                self.sighub.serialService.responseSignal.disconnect(self.preWriteHandle)
            case _:
                pass
        
        pass

    @pyqtSlot(int, tuple)
    def writeHandle(self, status, data):
        match (status):
            case RfidServiceMsg.write_done: 
                print('write done!')
                self.sighub.netService.net_message.connect(self.serverAckHandle)
                self.sighub.netService.ExpectResponseSlot(IssueNotificationMsg.toBytes(data[0])
                                                   ,NetMessageType.ServerAck
                                                   ,5)
                self.sighub.rfidService.rfid_signal.disconnect(self.writeHandle)
                pass

            case RfidServiceMsg.failure:
                self.sighub.resultReceived.emit(ProcessSigs.failed_hardware)
                self.sighub.delayedReturn(45)
                self.sighub.serialService.expect_response(SerialMessageType.readerToStore)
                self.sighub.rfidService.rfid_signal.disconnect(self.writeHandle)
                pass
            case _:
                pass
        pass

    @pyqtSlot(int,object)
    def serverAckHandle(self, status:int, data:int|bytes|None):
        print('serverAckHandle')
        if status == NetSignalType.response:
            obj = unpackMsg(data)
            if obj == None: return
            if isinstance(obj, ServerAckMsg):

                match (obj.err):
                    case ErrCode.success:
                        self.sighub.serialService.responseSignal.connect(self.finalHandle)
                        self.sighub.serialService.expect_response(SerialMessageType.readerToExit)
                    # case ErrCode.invalid:
                    #     pass
                    case ErrCode.expired:
                        self.sighub.resultReceived.emit(ProcessSigs.expired)
                        self.sighub.serialService.expect_response(SerialMessageType.readerToStore)
                        self.sighub.delayedReturn(45)
                    case _: 
                        raise RuntimeError(f"Unknown Response:{str(obj.err)}")
                
                self.sighub.netService.net_message.disconnect(self.serverAckHandle)

        elif status == NetSignalType.timeout:
            self.sighub.resultReceived.emit(ProcessSigs.failed_timeout)
            self.sighub.serialService.expect_response(SerialMessageType.readerToStore)
            self.sighub.delayedReturn(45)
            self.sighub.netService.net_message.disconnect(self.serverAckHandle)
        pass

    @pyqtSlot(bytes)
    def finalHandle(self, data:bytes):
        match (data):
            case SerialMessageType.ack:
                pass
            case SerialMessageType.inPosition:
                self.sighub.resultReceived.emit(ProcessSigs.success)
                self.sighub.delayedReturn(45)
                self.sighub.serialService.responseSignal.disconnect(self.finalHandle)
            case SerialMessageType.failure:
                self.sighub.resultReceived.emit(ProcessSigs.failed_mechanical)
                self.sighub.serialService.expect_response(SerialMessageType.readerToStore)
                self.sighub.delayedReturn(45)
                self.sighub.serialService.responseSignal.disconnect(self.finalHandle)
            case SerialMessageType.timeout:
                self.sighub.resultReceived.emit(ProcessSigs.failed_mechanical)
                self.sighub.serialService.expect_response(SerialMessageType.readerToStore)
                self.sighub.delayedReturn(45)
                self.sighub.serialService.responseSignal.disconnect(self.finalHandle)
            case _:
                pass
        
        pass

class EDReturn(EDGeneral):
    def __init__(self, source:QMLSigHub) -> None:
        super().__init__(source)

    def start(self):
        self.sighub.serialService.responseSignal.connect(self.detectHandle)        
        self.sighub.serialService.expect_response(SerialMessageType.cardDetect)
        self.sighub.resultReceived.emit(ProcessSigs.insert)
    
    @pyqtSlot(bytes)
    def detectHandle(self, data:bytes):
        match (data):
            case SerialMessageType.ack:
                pass
            case SerialMessageType.inPosition:
                self.sighub.rfidService.rfid_signal.connect(self.readHandle)
                self.sighub.resultReceived.emit(ProcessSigs.detected)
                self.sighub.rfidService.verify_card()
                self.sighub.serialService.responseSignal.disconnect(self.detectHandle)
            case SerialMessageType.failure:
                self.sighub.resultReceived.emit(ProcessSigs.failed_mechanical)
                self.sighub.delayedReturn(5)
                self.sighub.serialService.responseSignal.disconnect(self.detectHandle)
            case SerialMessageType.timeout:
                self.sighub.resultReceived.emit(ProcessSigs.not_detected)
                self.sighub.delayedReturn(5)
                self.sighub.serialService.responseSignal.disconnect(self.detectHandle)
            case _:
                pass
        
        pass

    @pyqtSlot(int, tuple)
    def readHandle(self, status, data):
        match (status):
            case RfidServiceMsg.read_done: 
                print('read done!')
                self.sighub.netService.net_message.connect(self.serverAckHandle)
                self.sighub.netService.ExpectResponseSlot(ReturnNotificationMsg.toBytes(data[0],data[1])
                                                   ,NetMessageType.ServerAck
                                                   ,5)
                self.sighub.rfidService.rfid_signal.disconnect(self.readHandle)
                pass

            case RfidServiceMsg.failure:
                self.sighub.resultReceived.emit(ProcessSigs.invalid)
                self.sighub.serialService.expect_response(SerialMessageType.readerToExit)
                self.sighub.delayedReturn(45)
                self.sighub.rfidService.rfid_signal.disconnect(self.readHandle)
                pass
            case _:
                pass
        pass


    @pyqtSlot(int,object)
    def serverAckHandle(self, status:int, data:int|bytes|None):
        print('serverAckHandle')
        if status == NetSignalType.response:
            obj = unpackMsg(data)
            if obj == None: return
            if isinstance(obj, ServerAckMsg):

                match (obj.err):
                    case ErrCode.success:
                        # self.sighub.serialService.responseSignal.connect(self.finalHandle)
                        self.sighub.resultReceived.emit(ProcessSigs.success)
                        self.sighub.serialService.expect_response(SerialMessageType.readerToStore)
                        self.sighub.delayedReturn(10)
                    # case ErrCode.expired:
                    #     pass
                    case ErrCode.invalid:
                        self.sighub.resultReceived.emit(ProcessSigs.invalid)
                        self.sighub.serialService.expect_response(SerialMessageType.readerToExit)
                        self.sighub.delayedReturn(30)
                    case _: 
                        raise RuntimeError(f"Unknown Response:{str(obj.err)}")
                
                self.sighub.netService.net_message.disconnect(self.serverAckHandle)

        elif status == NetSignalType.timeout:
            self.sighub.resultReceived.emit(ProcessSigs.failed_timeout)
            self.sighub.serialService.expect_response(SerialMessageType.readerToExit)
            self.sighub.delayedReturn(45)
            self.sighub.netService.net_message.disconnect(self.serverAckHandle)
        pass



