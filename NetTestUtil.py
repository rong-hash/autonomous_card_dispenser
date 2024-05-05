import random

from paho.mqtt import client as mqtt_client
from paho.mqtt.enums import CallbackAPIVersion
from ssl import SSLError
from NetMessageUtil import *


broker = '10.106.65.159'
port = 8883
# broker = '11385g3w05.goho.co'
# port = 34494
topic = "test/term1"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'

f = open('710a20.dump','rb')

cd_dump = f.read()

f.close()

icInfo = ICInfo()
icInfo.room = 0x0
icInfo.sec1 = cd_dump[8*64:8*64+48]+b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
icInfo.sec2 = cd_dump[9*64:9*64+48]+b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
icInfo.uid = int.from_bytes(cd_dump[0:4],'little')
requests = set([NetMessageType.FRAuthRequest, NetMessageType.QRAuthRequest, NetMessageType.IssueNotification])


def connect_mqtt() -> mqtt_client.Client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(callback_api_version= CallbackAPIVersion.VERSION1 ,client_id = client_id)
    client.tls_set(ca_certs='certs/ca.crt',certfile='certstest/testmgr.crt',keyfile='certstest/testmgr.key')
    client.on_connect = on_connect
    try:
        client.connect(broker, port,15)
    except SSLError:
        print("SSL Exception")
    except TimeoutError:
        print("Timed Out")
    except OSError:
        print("OS Exception")
    except Exception:
        print("Unknown Error")
    return client


def subscribe(client: mqtt_client.Client):
    def on_message(client: mqtt_client.Client, userdata, msg):
        # print(f"Received `{msg.payload}` from `{msg.topic}` topic")
        if (msg.payload[0:1] not in requests): return
        print("MsgReceived")
        obj = unpackMsg(msg.payload)
        if isinstance(obj, QRAuthRequestMsg):
            print("QRAuthRequestMsg")
            if (obj.token == b'abcd0000000000000000000000000000'):
                print("QRAuthRequestMsg: token matched")
                client.publish(topic, QRAuthResponseMsg.toBytes(654,ErrCode.success, icInfo),2)
            else:
                client.publish(topic, QRAuthResponseMsg.toBytes(654, ErrCode.invalid, icInfo),2)
        elif isinstance(obj, FRAuthRequestMsg):
            print("FRAuthRequestMsg")
            client.publish(topic, FRAuthResponseMsg.toBytes(655,ErrCode.success, icInfo),2)
        elif isinstance(obj, IssueNotificationMsg):
            print(f"IssueNotificationMsg:uid={obj.uid}")
            client.publish(topic, ServerAckMsg.toBytes(ErrCode.success),2)


    print(client.subscribe(topic))
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()