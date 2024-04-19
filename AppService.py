from PyQt5.QtCore import QObject,QVariant, QMetaType, pyqtSlot, pyqtSignal
from PyQt5.QtQuick import QQuickItem
from CameraService import QPicamera2Item, QPicamera2ItemService
from NetService import NetService, NetMessageType, ConnectionStatus

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
                    self.netService.ExpectResponseSlot(bytes((0x10))+self.qrInfo,0x20,5)          
                    self.qrInfo = None
                #self.resultReceived.emit(2)
                pass
            case _:
                raise RuntimeError("Undefined Form ID")
            
    @pyqtSlot(bytes)
    def QRDecodeHandle(self, code:bytes):
        self.qrInfo = code
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
            case NetMessageType.connection:
                if data == ConnectionStatus.disconnected:
                    self.netService.reset()
                    print("[MQTT] Disconnected")
                else:
                    print("[MQTT] Connected")
                pass
            case NetMessageType.request:
                pass
            case NetMessageType.response:
                pass
            case NetMessageType.timeout:
                if (self.formStatus == Forms.Process):
                    self.resultReceived.emit(1)

        pass

    def registerQML(self,root:QObject):
        root.newFormLoaded.connect(self.newFormLoadHandle)

    def registerCameeraService(self,obj:QPicamera2ItemService):
        self.videoFeedStart.connect(obj.register_camearitem)
        obj.qr_decode.connect(self.QRDecodeHandle)

    def registerNetService(self, obj:NetService):
        obj.net_message.connect(self.NetMessageHandle)
        self.netService = obj
        self.netService.run()