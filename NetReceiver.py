import ssl
from paho.mqtt import client as mqtt_client
import mysql.connector
from NetMessageUtil import *
import Database
import random
import NetSender


broker = "10.106.65.159"
port = 8883
topic = "icdev/term1"

cert_path = "/home/ma/qr_code_server/manager.crt"
key_path = "/home/ma/qr_code_server/manager.key"
ca_path = "/home/ma/qr_code_server/root.crt"

cnx = mysql.connector.connect(**Database.config)
cursor = cnx.cursor()

# the set of message types that the receiver can handle
receive_requests = set([NetMessageType.FRAuthRequest, NetMessageType.QRAuthRequest, NetMessageType.IssueNotification])


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(topic, qos=2)
    else:
        print("Failed to connect, return code %d\n", rc)

def on_message(client, userdata, msg):
    print("-------------------------------------------")
    try:
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
    except:
        print(f"Received message from `{msg.topic}` topic")
    # 消息处理逻辑
    handle_message(msg.payload, client)

def handle_message(payload, client):
    
    # Check what type of message it is
    message_type = payload[0:1]
    if (message_type not in receive_requests): return

    
    obj = unpackMsg(payload)
    print(f"Message type: {message_type}")
    if isinstance(obj, QRAuthRequestMsg):
        # QR Code Authentication Request
        print("Handling QR Code Authentication Request")

        # Unpack the payload
        token = obj.token

        # query database, whether the token exists
        result = Database.select(cnx, cursor, 'rc_card', 'tokens', 'student_id, request_id', f"token = '{token.decode()}'")
        # set default response to invalid
        response_bytes = QRAuthResponseMsg.toBytes(0, ErrCode.invalid, NetSender.icInfo)

        if len(result[0]) > 1: # token exists
            student_id = result[0][0]
            request_id = result[0][1]
            # check whether the student already has a card
            result = Database.select(cnx, cursor, 'rc_card', 'students', 'hold', f"student_id = {student_id}")
            hold = result[0][0]
            if not hold:
                # student does not hold a card
                # tell the terminal to issue a new card
                response_bytes = QRAuthResponseMsg.toBytes(request_id, 
                                                           ErrCode.success, 
                                                           NetSender.icInfo)

        # Publish the response to the MQTT broker
        client.publish(topic, response_bytes, qos=2)

    elif isinstance(obj, FRAuthRequestMsg):
        print("Handling Faical Recoginition Auth Request")

        
    elif isinstance(obj, IssueNotificationMsg):
        print("Handling Issue Notification")
        card_id = obj.uid

    

def main():
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1)
    client.tls_set(ca_certs=ca_path, certfile=cert_path, keyfile=key_path, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker, port)
    client.loop_forever()

if __name__ == "__main__":
    main()
