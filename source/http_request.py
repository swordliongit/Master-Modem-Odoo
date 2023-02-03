#
# Author: Kılıçarslan SIMSIKI
#


import requests
import json


def odoo_login():
    url = 'https://modem.nitrawork.com/web/session/authenticate'
    headers = {
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5",
        "Content-Type": "application/json"
    }
    myobj = {
        "jsonrpc": "2.0",
        "params": {
            "login": "admin",
            "password": "Artin.modems",
            "db": "modems"
        }
    }
    x = requests.post(url, json=myobj, headers=headers)
    # print the response text (the content of the requested file):
    # return str(x.content)
    # response = x.json()
    # return str(response['jsonrpc'])
    # aşağıdaki işlemle önce json parse edildi sonra 0-52 ye kadar substring yapıldı
    global cookie
    cookie = ((x.headers)['Set-Cookie'])[0:51]

    print(cookie)

########################


def send_datato_odoo_one_by_one(modem_data: dict):
    url = 'http://localhost:8069/web/dataset/call_kw/modem.profile/create'
    headers = {
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5",
        "Content-Type": "application/json",
        "Cookie": cookie
    }
    myobj = modem_data
    """{"id":43,"jsonrpc":"2.0","method":"call","params":{
        "args":[
            {"partner_gid":0,"additional_info":False,"image_1920":False,"__last_update":False,"is_company":False,"active":True,"company_type":"person","name":"proto5","parent_id":False,"company_name":False,"type":"contact","street":False,"street2":False,"city":False,"state_id":False,"zip":False,"country_id":False,"vat":False,"x_uptime":False,"x_wireless_status":False,"x_channel":False,"x_mac":False,"x_ip":False,"x_device_info":False,"x_subnet":False,"x_dhcp":False,"x_enable_wireless":False,"x_enable_ssid1":False,"x_enable_ssid2":False,"x_enable_ssid3":False,"x_enable_ssid4":False,"x_manual_time":False,"x_new_password":False,"x_wan_status":False,"x_lan_info":False,"phone":False,"mobile":False,"user_ids":[],"email":False,"message_follower_ids":[],"activity_ids":[],"message_ids":[]
             
             }
            ],
        "model":"res.partner","method":"create","kwargs":{"context":{"lang":"tr_TR","tz":"Europe/Istanbul","uid":2,"allowed_company_ids":[1],"params":{"cids":1,"menu_id":96,"action":122,"model":"res.partner","view_type":"kanban"},"default_is_company":True}}}}"""

    x = requests.post(url, json=myobj, headers=headers)
    # print the response text (the content of the requested file):
    # return str(x.content)
    # response = x.json()
    # return str(response['jsonrpc'])
    # aşağıdaki işlemle önce json parse edildi sonra 0-52 ye kadar substring yapıldı
    last_result = json.loads((x.content))
    print(str(last_result))


def send_datato_odoo(modem_data: dict):
    # need to check this for multiple databases position
    url = 'https://modem.nitrawork.com/create/modems_from_data'
    headers = {
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5",
        "Content-Type": "application/json",
        "Cookie": cookie
    }

    requests.post(url, json=modem_data, headers=headers)


def fetch_datafrom_odoo():
    url = 'https://modem.nitrawork.com/web/dataset/search_read'
    headers = {
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5",
        "Content-Type": "application/json",
        "Cookie": cookie
    }
    myobj = {"id": 20, "jsonrpc": "2.0", "method": "call", "params": {"model": "modem.profile", "domain": [["x_device_update", "=", True]], "fields": ["x_hotel_name", "x_update_date", "x_uptime", "x_wireless_status", "x_channel", "x_mac", "x_device_info", "x_ip", "x_subnet", "x_dhcp", "x_enable_wireless", "x_enable_ssid1", "x_enable_ssid2", "x_enable_ssid3",
                                                                                                                                                       "x_enable_ssid4", "x_manual_time", "x_new_password", "x_reboot", "name", "modem_status", "city", "live_status"], "limit": 80, "sort": "live_status DESC", "context": {"lang": "en_US", "tz": "Europe/Istanbul", "uid": 2, "allowed_company_ids": [1], "params": {"cids": 1, "menu_id": 129, "action": 182, "model": "modem.profile", "view_type": "list"}, "bin_size": True}}}
    # {'jsonrpc': '2.0', 'id': 39, 'result': {'length': 2, 'records': [{'id': 5, 'x_uptime': False, 'x_wireless_status': False, 'x_channel': False, 'x_mac': False, 'x_device_info': False, 'x_ip': False, 'x_subnet': False, 'x_dhcp': False, 'x_enable_wireless': True, 'x_enable_ssid1': False, 'x_enable_ssid2': False, 'x_enable_ssid3': False, 'x_enable_ssid4': False, 'x_manual_time': False, 'x_new_password': False, 'name': 'protomet', 'modem_status': False, 'city': False, 'live_status': 'offline'}, {'id': 6, 'x_uptime': False, 'x_wireless_status': False, 'x_channel': False, 'x_mac': False, 'x_device_info': False, 'x_ip': False, 'x_subnet': False, 'x_dhcp': True, 'x_enable_wireless': False, 'x_enable_ssid1': False, 'x_enable_ssid2': False, 'x_enable_ssid3': False, 'x_enable_ssid4': False, 'x_manual_time': False, 'x_new_password': False, 'name': 'protomet2', 'modem_status': False,
    # 'city': False, 'live_status': 'offline'}]}}
    # to access our modems : last_result['result']['records'][0] -> gives the first dict

    x = requests.post(url, json=myobj, headers=headers)
    # print the response text (the content of the requested file):
    # return str(x.content)
    # response = x.json()
    # return str(response['jsonrpc'])
    # aşağıdaki işlemle önce json parse edildi sonra 0-52 ye kadar substring yapıldı
    last_result = json.loads((x.content))
    # print(str(last_result))

    return last_result['result']['records']

    # for modem in last_result['result']['records']:
    #    print(modem)
