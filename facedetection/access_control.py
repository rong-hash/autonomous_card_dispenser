from hikvision import get_signature, get_headers, get_card_id, get_device_id, change_authority, remove_authority
import pandas as pd
import uuid
import requests
import time
import json


def change_door_access(name, card_id, device_name, channel_no, change_type):
    ret = 0
    base_url = "https://10.106.239.254:443"  # 可以正常访问的IP地址
    # 注意增加/artemis
    api_get_address_url = "/artemis/api/resource/v2/person/advance/personList"
    url = base_url + api_get_address_url
    appKey = "20925512"
    appSecret = "T03M7k6XT3au1SVYytFl"
    x_ca_nonce = str(uuid.uuid4())
    x_ca_timestamp = str(int(round(time.time()) * 1000))
    signature = get_signature(appKey, appSecret, x_ca_nonce, x_ca_timestamp, api_get_address_url)
    headers = get_headers(appKey, signature, x_ca_timestamp, x_ca_nonce)
    person_body = get_card_id(name)
    print(person_body)
    # return
    try: 
        results = requests.post(url, data=json.dumps(person_body), headers=headers,  verify=False)
        json_data = results.json()
        person_id = json_data['data']['list'][0]['personId']
        print(json_data)
    except requests.RequestException as e:
        print(f"Get person_id request failed: {e}")
        ret = -1
    except KeyError:
        print(f"Failed to get person ID from person Name")
        ret = 1
    
    api_get_address_url = "/artemis/api/resource/v2/door/search"
    x_ca_nonce = str(uuid.uuid4())
    x_ca_timestamp = str(int(round(time.time()) * 1000))
    signature = get_signature(appKey, appSecret, x_ca_nonce, x_ca_timestamp, api_get_address_url)
    headers = get_headers(appKey, signature, x_ca_timestamp, x_ca_nonce)
    url = base_url + api_get_address_url
    device_body = get_device_id(device_name)
    try: 
        results = requests.post(url, data=json.dumps(device_body), headers=headers,  verify=False)
        json_data = results.json()
        device_id = json_data['data']['list'][0]['indexCode']
        print(json_data)
    except requests.RequestException as e:
        print(f"Get person_id request failed: {e}")
        ret = -1
    except KeyError:
        print(f"Failed to get person ID from person Name")
        ret = -1

    api_get_address_url = "/artemis/api/acps/v1/authDownload/task/simpleDownload"
    x_ca_nonce = str(uuid.uuid4())
    x_ca_timestamp = str(int(round(time.time()) * 1000))
    signature = get_signature(appKey, appSecret, x_ca_nonce, x_ca_timestamp, api_get_address_url)
    headers = get_headers(appKey, signature, x_ca_timestamp, x_ca_nonce)
    url = base_url + api_get_address_url
    if change_type == 0:
        authority_body = change_authority(device_id, 'door', channel_no, person_id, change_type, card_id)
    elif change_type == 2:
        authority_body = remove_authority(device_id, 'door', channel_no, person_id, change_type, card_id)
    
    try: 
        results = requests.post(url, data=json.dumps(authority_body), headers=headers,  verify=False)
        json_data = results.json()
        print(json_data)
    except:
        print(f"Change authority request failed")
        ret = -1
    
    return ret
    
    
if __name__ == "__main__":
    change_door_access("测试卡1", "0691796502", "SY2-1F-029", 2, 2)


