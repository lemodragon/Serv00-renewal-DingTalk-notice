import paramiko
import time
import hmac
import hashlib
import base64
import urllib.parse
from datetime import datetime
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 定义目标 URL (添加 https:// 协议头)
url = 'https://s2.example.com'

# SSH 连接信息
ssh_host = 's2.serv00.com'
ssh_port = 22
ssh_username = '用户名'
ssh_password = '密码'


# 钉钉机器人Webhook地址和密钥
webhook_url = 'https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
secret = 'SEC0e0xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'


# 定义重试次数和间隔时间
max_retries = 4   # 5次
retry_interval = 300  # 5分钟

# 使用 request 检查 URL 的状态
def check_website(url):
    try:
        response = requests.get(url, verify=False, timeout=10)
        return response.status_code == 200
    except:
        return False

retry_count = 0
success = False

while retry_count < max_retries and not success:
    if check_website(url):
        print("Website is up and running!")
        success = True
    else:
        print("Service Unavailable, attempting to resurrect PM2 processes via SSH...")

        # 创建Transport对象
        transport = paramiko.Transport((ssh_host, ssh_port))
        transport.connect(username=ssh_username, password=ssh_password)

        # 创建SSH通道
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh._transport = transport

        # 获取SSH服务器IP地址
        server_ip = transport.getpeername()[0]

        try:
            # 获取服务器IP地址
            stdin, stdout, stderr = ssh.exec_command('hostname -I')

            # 执行pm2 resurrect命令
            stdin, stdout, stderr = ssh.exec_command('/home/lolita/.npm-global/bin/pm2 resurrect')
            error = stderr.read().decode()

            # 获取SSH登录状态和IP地址
            ssh_info = f"SSH Login: {ssh_username}@{server_ip}"

            # 发送钉钉机器人消息
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            message = f"Time: {current_time}\nMaster，Alist掉线了,喵!\n{ssh_info}\nError: {error}"

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

        # 增加重试计数器
        retry_count += 1
        if retry_count < max_retries:
            print(f"Retrying in {retry_interval / 60} minutes...")
            time.sleep(retry_interval)  # 等待一段时间再重试

# 如果达到最大重试次数仍然失败，发送特定通知
if not success:
    try:
        failure_message = "Master，Alist坏掉了捏 ~"
        timestamp = str(round(time.time() * 1000))
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        headers = {'Content-Type': 'application/json'}
        data = {
            "msgtype": "text",
            "text": {"content": failure_message},
        }
        url_with_signature = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
        print("Sending failure notification to:", url_with_signature)
        response = requests.post(url_with_signature, headers=headers, json=data)
        print("Response status code:", response.status_code)
        print("Response text:", response.text)
    except Exception as e:
        print(f"An error occurred while sending failure message: {e}")

# 检查是否需要发送成功通知
now = datetime.now()
if now.hour == 10 and now.minute == 30:  # 每天晚上 10:30 发送成功通知，对应北京时间 16：30
    try:
        # 发送钉钉机器人消息
        success_message = "Master,Alist 服务正常捏！"
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
        response = requests.post(url_with_signature, headers=headers, json=data)
        print("Response status code:", response.status_code)
        print("Response text:", response.text)
    except Exception as e:
        print(f"An error occurred while sending success message: {e}")
