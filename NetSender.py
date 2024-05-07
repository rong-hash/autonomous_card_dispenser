from paho.mqtt import client as mqtt_client
import struct
import random
import ssl
from NetMessageUtil import *

broker = "10.106.65.159"
port = 8883

topic = "icdev/term1"
# MQTT服务器的证书和密钥文件路径
cert_path = "/home/ma/qr_code_server/manager.crt"
key_path = "/home/ma/qr_code_server/manager.key"
ca_path = "/home/ma/qr_code_server/root.crt"

icInfo = ICInfo()
icInfo.room = 0x0
icInfo.sec1 = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
icInfo.sec2 = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
icInfo.uid = 32

test_token = "b770b9098bf36efad7398c1a6b306c41"

def publish(client):
    id = random.randint(1, 1000)  # 生成一个随机的请求ID
    token = b'testtoken1234567890123456789012'  # 模拟的QR token，确保长度为32字节
    # f = open('710a20.dump','rb')

    # cd_dump = f.read()
    
    # f.close()


    request = QRAuthRequestMsg()
    request.id = 32
    
    request.token = test_token.encode()

    msg = request.toBytes(request.token)

    client.publish(topic, msg, qos=2)

def run():
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1)
    client.tls_set(ca_certs=ca_path, certfile=cert_path, keyfile=key_path, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
    client.connect(broker, port)
    client.loop_start()
    publish(client)
    client.loop_stop()

if __name__ == "__main__":
    run()
