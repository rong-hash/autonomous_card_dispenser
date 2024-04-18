from PyQt5.QtCore import QObject,QVariant, QMetaType, pyqtSlot, pyqtSignal
from PyQt5.QtQuick import QQuickItem
from CameraService import QPicamera2Item, QPicamera2ItemService

from paho.mqtt import client as mqtt_client
from paho.mqtt.enums import CallbackAPIVersion
from threading import Timer,Lock



class ConnectionStatus:
    connected = 0
    disconnected = 1

class Promise:
    def __init__(self,data:bytes, expected_type:int, timeout:int, handler) -> None:
        self.data = data
        self.expected_type = expected_type
        self.timeout = timeout
        self.timer = Timer(timeout,handler,(expected_type,))
    
    def start(self):
        self.timer.start()
    
    def cancel(self):
        self.timer.cancel()

class NetService(QObject):
    connection_status_changed = pyqtSignal(int)
    new_response = pyqtSignal(bytes)
    new_request = pyqtSignal(bytes)
    timed_out = pyqtSignal()            


    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.broker:str = None
        self.port:int = None
        self.topic:str = None
        self.client_id:str = None
        self.client:mqtt_client.Client = None
        self.request_types:set = {0x30}
        self.lock = Lock()
        self.expected_types:set = {}
        self.promise:Promise = None
        
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
        client.on_disconnect = self.on_disconnect_handler
        client.will_set(self.topic,bytearray([0x50,0x01]),2)
        client.connect(self.broker, self.port)
        self.client =  client
    
    def on_connect_handler(self,client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            err, _ = self.client.subscribe(self.topic)
            if err != mqtt_client.MQTT_ERR_SUCCESS:
                print("Subscription Failed")
                self.client.disconnect()
                return
            print(f"Subscribed to {self.topic}")
            self.connection_status_changed.emit(ConnectionStatus.connected)
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_disconnect_handler(self,client,userdata,rc):
        self.connection_status_changed.emit(ConnectionStatus.disconnected)

    def on_message_handler(self, client, userdata, msg):

        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    
        if (len(msg.payload) == 0): return
        if (msg.payload[0] in self.expected_types): self.expected_handler(msg.payload)
        if (msg.payload[0] in self.request_types): self.request_handler(msg.payload)

        return

    def expected_handler(self, data:bytes):
        msg_type = data[0]
        self.lock.acquire()
        if (msg_type in self.expected_types):
            self.promise.cancel()
            self.promise = None
            self.expected_types.remove(msg_type)
            self.new_response.emit(data)
        self.lock.release()
        pass

    def request_handler(self, data:bytes):
        self.new_request.emit(data)
        pass

    def run(self):
        self.connect_mqtt()
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()

    def timeout_callback(self, exptected_type):
        self.lock.acquire()
        if (exptected_type in self.expected_types): 
            self.expected_types.remove(exptected_type)
            self.promise = None
            self.lock.release()
            self.timed_out.emit()
        else:
            self.lock.release()


    @pyqtSlot(bytes)
    def PublishSlot(self, data:bytes):
        self.client.publish(self.topic,data,2)

    @pyqtSlot(bytes, int, int)
    def ExpectResponseSlot(self, data:bytes, expected_type:int, timeout:int):
        self.lock.acquire()
        if self.promise != None:
            self.lock.release()
            print("Rejected: Pending Request")
            return
        self.promise = Promise(data, expected_type, timeout)
        self.expected_types.add(expected_type)  #Register types
        self.lock.release()
        self.PublishSlot(data)
        self.promise.start()
        pass


    