from hikvision import face_recognition_body, get_signature, get_headers
from image_process import binary2base64
import json
import time
import uuid
import requests
import base64
from PIL import Image
import io

def face_recognition(face_binary):
    base_url = "https://10.106.239.254:443"
    api_get_address_url = "/artemis/api/frs/v1/application/oneToMany"
    url = base_url + api_get_address_url
    appKey = "20925512"
    appSecret = "T03M7k6XT3au1SVYytFl"
    x_ca_nonce = str(uuid.uuid4())
    x_ca_timestamp = str(int(round(time.time()) * 1000))
    signature = get_signature(appKey, appSecret, x_ca_nonce, x_ca_timestamp, api_get_address_url)
    headers = get_headers(appKey, signature, x_ca_timestamp, x_ca_nonce)
    face_base64 = binary2base64(face_binary)
    face_body = face_recognition_body(80, face_base64)
    try:
        results = requests.post(url, data=json.dumps(face_body), headers=headers,  verify=False)
        json_data = results.json()
        name = json_data['data']['list'][0]['faceInfo']['name']
        uid = json_data['data']['list'][0]['faceInfo']['certificateNum']
        return name, uid
    except:
        print("face recognition failed")
        return "None", "None"

if __name__ == "__main__":
    image_path = "test_image/sample[3435].jpg"
    with Image.open(image_path) as image:
        # 将图片转换为二进制数据
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_data = buffered.getvalue()
        
        name, uid = face_recognition(img_data)
        print(name, uid)

