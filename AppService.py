from PyQt5.QtCore import QObject,QVariant, QMetaType, pyqtSlot, pyqtSignal
from PyQt5.QtQuick import QQuickItem
from CameraService import QPicamera2Item, QPicamera2ItemService

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
                self.resultReceived.emit(2)
                pass
            case _:
                raise RuntimeError("Undefined Form ID")
    @pyqtSlot(bytes)
    def QRDecodeHandle(self, code:bytes):
        self.loadForm.emit("Process.qml",Transition.Push)
        pass
    def registerQML(self,root:QObject):
        root.newFormLoaded.connect(self.newFormLoadHandle)
    def registerCameeraService(self,obj:QPicamera2ItemService):
        self.videoFeedStart.connect(obj.register_camearitem)
        obj.qr_decode.connect(self.QRDecodeHandle)