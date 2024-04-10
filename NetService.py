from PyQt5.QtCore import QObject,QVariant, QMetaType, pyqtSlot, pyqtSignal
from PyQt5.QtQuick import QQuickItem
from CameraService import QPicamera2Item, QPicamera2ItemService

from paho.mqtt import client as mqtt_client
from paho.mqtt.enums import CallbackAPIVersion



class ConnectionStatus:
    connected = 0
    disconnected = 1

class NetService(QObject):
    connection_status_changed = pyqtSignal(int)
    new_message = pyqtSignal(bytes)


    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.broker:str = None
        self.port:int = None
        self.topic:str = None
        self.client_id:str = None
        self.client:mqtt_client.Client = None
        
        return
    
    def set_connection(self,broker:str, port:int, topic:str, client_id:str):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client_id = client_id
    
    # broker = '10.106.65.159'
    # port = 8883
    # topic = "test/msg"
    # client_id = 'icdev-terminal1'


    def connect_mqtt(self) -> None:


        client = mqtt_client.Client(callback_api_version= CallbackAPIVersion.VERSION1 ,client_id = self.client_id)
        client.tls_set(ca_certs='certs/ca.crt',certfile='certs/client.crt',keyfile='certs/client.key')
        client.on_connect = self.on_connect_handler
        client.will_set('test/msg',bytearray([0x50,0x01]),2)
        client.connect(self.broker, self.port)
        self.client =  client
    
    def on_connect_handler(self,client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)


    def subscribe(self):


        print(self.client.subscribe(self.topic))
        self.client.on_message = self.on_message_handler

    def on_message_handler(self, client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    def run(self):
        self.connect_mqtt()
        self.subscribe()
        self.client.loop_start()


    @pyqtSlot(bytes)
    def PublishHandle(self, data:bytes):
        self.client.publish(self.topic,data,2)
    

    def registerQML(self,root:QObject):
        root.newFormLoaded.connect(self.newFormLoadHandle)
    def registerCameeraService(self,obj:QPicamera2ItemService):
        self.videoFeedStart.connect(obj.register_camearitem)
        obj.qr_decode.connect(self.QRDecodeHandle)