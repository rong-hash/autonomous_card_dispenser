from PyQt5.QtCore import QObject,QVariant, QMetaType, pyqtSlot, pyqtSignal
from PyQt5.QtQuick import QQuickItem
from CameraService import QPicamera2Item, QPicamera2ItemService
from NetService import NetService, NetSignalType, ConnectionStatus
from NetMessageUtil import *
from threading import Timer

class Forms():
    RootWindow = 0
    MainScreen = 1
    Auth = 2
    Process = 3

class Transition():
    Pop = 0
    Push = 1

class QMLSigHub(QObject):
    videoFeedStart = pyqtSignal(QPicamera2Item)
    videoFeedStop = pyqtSignal()
    loadForm = pyqtSignal(str,int,name = 'loadForm')
    resultReceived = pyqtSignal(int,name = "resultReceived")
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.formStatus = Forms.MainScreen
        self.netService:NetService = None
        self.qrInfo:bytes = None
        return
    

    def registerQML(self,root:QObject):
        root.newFormLoaded.connect(self.newFormLoadHandle)

    def registerCameeraService(self,obj:QPicamera2ItemService):
        self.videoFeedStart.connect(obj.register_camearitem)
        obj.qr_decode.connect(self.QRDecodeHandle)
        obj.face_detect.connect(self.FaceDetectedHandle)

    def registerNetService(self, obj:NetService):
        obj.net_message.connect(self.NetMessageHandle)
        self.netService = obj
        self.netService.run()
    
    def returnToMain(self):
        self.loadForm("MainScreen.qml",Transition.Pop) #Lock is not necessary here.
    
    def delayedReturn(self, delay:int):
        self._delayThread = Timer(delay, self.returnToMain)
        self._delayThread.start()
        pass
    
    @pyqtSlot(QQuickItem)
    def newFormLoadHandle(self,obj:QQuickItem):
        formID:int = obj.property("formID")
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
            
        self.formStatus = formID

        match self.formStatus:
            case Forms.MainScreen:
                pass
            case Forms.Auth:
                cameraViewObj:QPicamera2Item = obj.findChild(QPicamera2Item,"cameraViewItem")
                self.videoFeedStart.emit(cameraViewObj)
                pass
            case Forms.Process:
                if (self.qrInfo != None):
                    print('[MQTT] Publishing Request')
                    self.netService.ExpectResponseSlot(
                        QRAuthRequestMsg.toBytes(self.qrInfo),
                        NetMessageType.QRAuthResponse,
                        5)          
                    self.qrInfo = None
                elif (self.faceInfo != None):
                    print('[MQTT] Publishing Request')
                    self.netService.ExpectResponseSlot(
                        FRAuthRequestMsg.toBytes(self.faceInfo),
                        NetMessageType.FRAuthResponse,
                        5)          
                    self.faceInfo = None
                else:
                    raise RuntimeError("No Data to Process")
                #self.resultReceived.emit(2)
                pass
            case _:
                raise RuntimeError("Undefined Form ID")
            
    @pyqtSlot(bytes)
    def QRDecodeHandle(self, code:bytes):
        self.qrInfo = code
        self.loadForm.emit("Process.qml",Transition.Push)
        pass

    @pyqtSlot(bytes)
    def FaceDetectedHandle(self, code:bytes):
        self.faceInfo = code
        print(len(self.faceInfo))
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
                    self.netService.reset()
                    print("[MQTT] Disconnected")
                else:
                    print("[MQTT] Connected")
                pass
            case NetSignalType.request:
                pass
            case NetSignalType.response:
                pass
            case NetSignalType.timeout:
                if (self.formStatus == Forms.Process):
                    self.resultReceived.emit(1)
                    self.delayedReturn(5)

        pass

