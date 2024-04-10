from PyQt5.QtCore import QObject,QVariant, QMetaType, pyqtSlot, pyqtSignal
from PyQt5.QtQuick import QQuickItem
from CameraService import QPicamera2Item, QPicamera2ItemService

class ConnectionStatus:
    connected = 0
    disconnected = 1

class NetService(QObject):
    connection_status_changed = pyqtSignal(int)

    loadForm = pyqtSignal(str,int,name = 'loadForm')
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        
        return
    @pyqtSlot(QQuickItem)
    def newFormLoadHandle(self,obj:QQuickItem):
        formID:int = obj.property("formID")
        match formID:
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

        match formID:
            case Forms.MainScreen:
                pass
            case Forms.Auth:
                cameraViewObj:QPicamera2Item = obj.findChild(QPicamera2Item,"cameraViewItem")
                self.videoFeedStart.emit(cameraViewObj)
                pass
            case Forms.Process:
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