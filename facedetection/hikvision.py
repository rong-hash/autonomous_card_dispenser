# -*- coding: utf-8 -*-
# _author_ = 
# Email: 
"""
协议：仅支持 HTTPS 传输
url格式：https://{hostname}:{port}/artemis/{uri}
# AK\SK摘要认证
调用 API 时，如果API需要安全认证，首先需要获取API的授权，得到AppKey和AppSecret；
其次，拼接签名字符串，将计算后的签名放在请求的 Header 传入，网关会通过对称计算签名来验证请求者的身份。
"""

import os
import base64
import json
import time
import uuid
import hmac  # hex-based message authentication code 哈希消息认证码
import hashlib  # 提供了很多加密的算法
import requests
from facedetection.image_process import image_to_base64
import datetime





def sign(key, value):
    temp = hmac.new(key.encode('utf-8'), value.encode('utf-8'), digestmod=hashlib.sha256)
    return base64.b64encode(temp.digest()).decode('utf-8')


def get_signature(appKey, appSecret, x_ca_nonce, x_ca_timestamp, api_get_address_url):
    # sign_str 的拼接很关键，不然得不到正确的签名
    sign_str = "POST\n*/*\napplication/json" + "\nx-ca-key:" + appKey + "\nx-ca-nonce:" + \
            x_ca_nonce + "\nx-ca-timestamp:" + x_ca_timestamp + "\n" + \
            api_get_address_url
    signature = sign(appSecret, sign_str)
    return signature


def get_headers(appKey, signature, x_ca_timestamp, x_ca_nonce):
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/json",
        "x-ca-key": appKey,  # appKey，即 AK
        "x-ca-signature-headers": "x-ca-key,x-ca-nonce,x-ca-timestamp",
        "x-ca-signature": signature,  # 需要计算得到的签名，此处通过后台得到
        "x-ca-timestamp": x_ca_timestamp,  # 时间戳
        "x-ca-nonce": x_ca_nonce  # UUID，结合时间戳防重复
    }
    return headers




# faceGroupIndexCodes需要再确认一下
def face_recognition_body(min_similarity, facepic_binarydata):
    body = {
        "pageNo": 1,
        "pageSize": 20,
        "minSimilarity": min_similarity,
        "facePicBinaryData": facepic_binarydata,
        "faceGroupIndexCodes": [
            "e611127fc0df4885aabd58f981580fe4"
        ]
    }
    return body

def face_recognition_body_by_url(min_similarity, facePicUrl):
    body = {
        "pageNo": 1,
        "pageSize": 20,
        "minSimilarity": min_similarity,
        "facePicUrl": facePicUrl,
        "faceGroupIndexCodes": [
            "e611127fc0df4885aabd58f981580fe4"
        ]
    }
    return body

def get_person_id(name, student_id):
    body = {
        "personName": name,
        "certificateNo": str(student_id),
        "pageNo": 1,
        "pageSize": 1000
    }
    return body

def get_card_id(name):
    body = {
        "personName": str(name),
        "pageNo": 1,
        "pageSize": 1000
    }
    return body



def get_device_id(name):
    body = {
        "name": name,
        "pageNo": 1,
        "pageSize": 1
    }
    return body

def change_authority(resourceIndexCode, resourceType, channelNos, personId, operatorType, card_id):

    current_datetime = datetime.datetime.now()

    # Adding two minutes to the current datetime
    current_datetime = current_datetime + datetime.timedelta(hours=8)

    new_datetime = current_datetime + datetime.timedelta(minutes=2)

    # Format the datetime as YYYY-MM-DDTHH:MM:SS.mmm and add the timezone offset as +00:00
    formatted_datetime = current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + '+08:00'
    formatted_new_datetime = new_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + '+08:00'
    print(formatted_datetime, " ", formatted_new_datetime)
    body = {
        "taskType": 1,
        "resourceInfo": {
            "channelNos": [channelNos],
            "resourceIndexCode": resourceIndexCode,
            "resourceType": resourceType,
            "startTime": formatted_datetime,
            "endTime": formatted_new_datetime
        },
        "personInfo": {
            "personId": personId,
            "operatorType": operatorType,
            "cards": [{
                "card": card_id,
                "status": operatorType # 这个status和上面的operator type一样的吗
            }]
        }
    }
    return body

# def change_authority(resourceIndexCode, resourceType, channelNos, personId, operatorType, card_id):
#     body = {
#         "taskType": 1,
#         "resourceInfo": {
#             "channelNos": [channelNos],
#             "resourceIndexCode": resourceIndexCode,
#             "resourceType": resourceType
#         },
#         "personInfo": {
#             "personId": personId,
#             "operatorType": operatorType,
#             "cards": [{
#                 "card": card_id,
#                 "status": operatorType # 这个status和上面的operator type一样的吗
#             }]
#         }
#     }
#     return body




if __name__ == "__main__":
    base_url = "https://10.106.239.254:443"  # 可以正常访问的IP地址
    # 注意增加/artemis
    api_get_address_url = "/artemis/api/frs/v1/application/oneToMany"
    appKey = "20925512"
    appSecret = "T03M7k6XT3au1SVYytFl"
    http_method = "POST"
    x_ca_nonce = str(uuid.uuid4())
    x_ca_timestamp = str(int(round(time.time()) * 1000))
    signature = get_signature(appKey, appSecret, x_ca_nonce, x_ca_timestamp, api_get_address_url)
    headers = get_headers(appKey, signature, x_ca_timestamp, x_ca_nonce)
    image_path = "test_image/sample[3435].jpg"
    facePicUrl = "https://raw.githubusercontent.com/rong-hash/rong-hash.github.io/gh-pages/img/me.jpg"
    facepic_binarydata = image_to_base64(image_path)
    face_body = face_recognition_body(80, facepic_binarydata)
    face_body_url = face_recognition_body_by_url(50, facePicUrl)
    device_name = "RC3门厅二通道闸机5_门_1"
    device_body = get_device_id(device_name)


    name = "陈志榕"
    certificate_No = "3200112414"
    body = get_person_id(name, certificate_No)

    url = base_url + api_get_address_url
    results = requests.post(url, data=json.dumps(face_body), headers=headers,  verify=False)
    print(results.json())