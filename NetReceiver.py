import ssl
from paho.mqtt import client as mqtt_client
import mysql.connector
from NetMessageUtil import *
import Database
import random
import os
import NetSender
from facedetection.access_control import change_door_access
from facedetection.face_recognition import face_recognition


broker = "10.106.65.159"
port = 8883
topic = "icdev/term1"

cert_path = "/home/ma/qr_code_server/manager.crt"
key_path = "/home/ma/qr_code_server/manager.key"
ca_path = "/home/ma/qr_code_server/root.crt"

cnx = mysql.connector.connect(**Database.config)
cursor = cnx.cursor()

# the set of message types that the receiver can handle
receive_requests = set([NetMessageType.FRAuthRequest, NetMessageType.QRAuthRequest, NetMessageType.IssueNotification, NetMessageType.ReturnNotification])


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
        # set default response to invalid
        response_bytes = QRAuthResponseMsg.toBytes(0, ErrCode.invalid, NetSender.icInfo)

        # Unpack the payload
        token = obj.token
        print(f"Token: {token.decode()}")
        # query database, whether the token exists
        result = Database.select(cnx, cursor, 'rc_card', 'tokens', 'student_id, request_id', f"token = '{token.decode()}'")
        
        if result: # token exists
            student_id = result[0][0]
            request_id = result[0][1]
            # check whether the student already has a card
            result = Database.select(cnx, cursor, 'rc_card', 'students', 'hold, uid, sec1, sec2', f"student_id = {student_id}")
            hold = result[0][0]
            if not hold:
                # student does not hold a card
                # tell the terminal to issue a new card

                # build ICInfo object
                ic_info = ICInfo()
                ic_info.room = 0
                ic_info.uid = result[0][1]
                ic_info.sec1 = result[0][2]
                ic_info.sec2 = result[0][3]
                response_bytes = QRAuthResponseMsg.toBytes(request_id, 
                                                           ErrCode.success, 
                                                           ic_info)

        # Publish the response to the MQTT broker
        client.publish(topic, response_bytes, qos=2)

    elif isinstance(obj, FRAuthRequestMsg):
        print("Handling Faical Recoginition Auth Request")
        img = obj.img
        # call face recognition api
        name, student_id = face_recognition(img)
        name, student_id = "陈志榕", "3200118998"

        response_bytes = FRAuthResponseMsg.toBytes(0, ErrCode.invalid, NetSender.icInfo)
        # if the student is recognized, create a new token and request id for the student 
        if student_id != "None" and name != "None":
            # check if a student with the student_id exists in the tokens table
            result = Database.select(cnx, cursor, 'rc_card', 'tokens', 'student_id, request_id', f"student_id = {student_id}")
            if not result:
                # randomly generate a 32 hex token
                token = os.urandom(16)
                token = token.hex()

                # randomly generate an int used as request_id
                request_id = os.urandom(4)
                request_id = int.from_bytes(request_id, 'big')
                while True:
                    # insert the token into the database, then find icinfo from the database based on student id
                    if Database.insert(cnx, cursor, 'rc_card', 'tokens', 'student_id, token, request_id', f"{student_id}, '{token}', '{request_id}'"):
                        break
            else:
                request_id = result[0][1]


            
            
            result = Database.select(cnx, cursor, 'rc_card', 'students', 'hold, uid, sec1, sec2', f"student_id = {student_id}")
            hold = result[0][0]
            if not hold:
                # student does not hold a card
                # tell the terminal to issue a new card

                # build ICInfo object
                ic_info = ICInfo()
                ic_info.room = 0
                ic_info.uid = result[0][1]
                ic_info.sec1 = result[0][2]
                ic_info.sec2 = result[0][3]
                response_bytes = QRAuthResponseMsg.toBytes(request_id, 
                                                        ErrCode.success, 
                                                        ic_info)
                
        
        client.publish(topic, response_bytes, qos=2)

        
    elif isinstance(obj, IssueNotificationMsg):
        print("Handling Issue Notification")
        card_uid = obj.uid
        request_id = obj.req_id
        # query database, get the student_id from the request_id
        result = Database.select(cnx, cursor, 'rc_card', 'tokens', 'student_id', f"request_id = {request_id}")

        if result:
            student_id = result[0][0]
            # find info about the student's card and building token
            
            door = Database.select(cnx, cursor, 'rc_card', 'students', 'door_info', f"student_id = {student_id}")
            
            if not door:
                # do not ACK
                response_bytes = ServerAckMsg.toBytes(ErrCode.invalid)
                client.publish(topic, response_bytes, os=2)
                
            door_info = door[0][0]
            # call api to give rights to open the door of the building
            # @TODO: find card name from csv file based on card uid
            # @TODO: find channel from csv file based on door_info
            card_uid_str = extend_uid(card_uid)
            while True:
                if change_door_access("测试卡1", card_uid_str, door_info, 2, 0):
                    break

            # update the database
            Database.update(cnx, cursor, 'rc_card', 'students', 'hold,holding_uid', 'True,'+str(card_uid), f"student_id = {student_id}")

            # return server ACK
            response_bytes = ServerAckMsg.toBytes(ErrCode.success)
            client.publish(topic, response_bytes, qos=2)
    elif isinstance(obj, ReturnNotificationMsg):
        print("Handling Return Notification")
        card_uid = obj.uid
        
        # query database, get the student_id from the request_id
        result = Database.select(cnx, cursor, 'rc_card', 'students', 'student_id, door_info', f"holding_uid = {card_uid}")
        response_bytes = ServerAckMsg.toBytes(ErrCode.invalid)
        if result:
            student_id = result[0][0]
            door_info = result[0][1]

            card_uid = extend_uid(card_uid)
            # @TODO: find card name from csv file based on card uid
            # @TODO: find channel from csv file based on door_info
            while True: # delete the card's access to building's door
                if change_door_access("测试卡1", card_uid, door_info, 2, 2):
                    break
            # update the database
            Database.update(cnx, cursor, 'rc_card', 'students', 'hold,holding_uid', 'False,Null', f"student_id = {student_id}")
            # return server ACK
            response_bytes = ServerAckMsg.toBytes(ErrCode.success)
            
            
        
        client.publish(topic, response_bytes, qos=2)
    print("Finished handling")          
    return 

def main():
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1)
    client.tls_set(ca_certs=ca_path, certfile=cert_path, keyfile=key_path, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker, port)
    client.loop_forever()

if __name__ == "__main__":
    main()
