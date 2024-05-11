import os
import requests
import paramiko
import time
import hmac
import hashlib
import base64
import urllib.parse

url = 'https://synctv.lolita.pp.ua'

ssh_host = 's2.serv00.com'
ssh_port = 22
ssh_username = '用户名'
ssh_password = '密码'

# 钉钉机器人Webhook地址和密钥
webhook_url = 'https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
secret = 'SEC0e0xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# 检查URL的状态码
response = requests.get(url)
if response.status_code != 200:
    print("Service Unavailable, attempting to resurrect PM2 processes via SSH...")

    # 创建Transport对象
    transport = paramiko.Transport((ssh_host, ssh_port))
    transport.connect(username=ssh_username, password=ssh_password)

    # 创建SSH通道
    ssh = paramiko.SSHClient()
    ssh._transport = transport

    # 获取SSH服务器IP地址
    server_ip = transport.getpeername()[0]

    try:
        # 获取服务器IP地址
        stdin, stdout, stderr = ssh.exec_command('hostname -I')

        # 执行pm2 resurrect命令
        stdin, stdout, stderr = ssh.exec_command('/home/用户名/.npm-global/bin/pm2 resurrect')
        error = stderr.read().decode()

        # 获取SSH登录状态和IP地址
        ssh_info = f"SSH Login: {ssh_username}@{server_ip}"

        # 发送钉钉机器人消息
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        message = f"Time: {current_time}\nMaster，SyncTV掉线了,喵!\n{ssh_info}\nError: {error}"
    

        timestamp = str(round(time.time() * 1000))
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        headers = {'Content-Type': 'application/json'}
        data = {
            "msgtype": "text",
            "text": {"content": message},
        }
        url_with_signature = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
        print("Sending request to:", url_with_signature)
        print("Request headers:", headers)
        print("Request data:", data)

        try:
            response = requests.post(url_with_signature, headers=headers, json=data)
            print("Response status code:", response.status_code)
            print("Response text:", response.text)
        except Exception as e:
            print(f"An error occurred while sending message: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # 关闭SSH连接
        ssh.close()
        transport.close()

else:
    print(f"URL returned status code: {response.status_code}")
    print("Sending success message to DingTalk bot...")

    # 发送成功消息到钉钉机器人
    success_message = "Master,SyncTV服务正常捏！"
    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "text",
        "text": {"content": success_message},
    }

    url_with_signature = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
    print("Sending request to:", url_with_signature)
    print("Request headers:", headers)
    print("Request data:", data)

    try:
        response = requests.post(url_with_signature, headers=headers, json=data)
        print("Response status code:", response.status_code)
        print("Response text:", response.text)
    except Exception as e:
        print(f"An error occurred while sending success message: {e}")
