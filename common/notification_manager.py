import requests
import smtplib
import time
import hmac
import hashlib
import base64
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class NotificationManager:
    def __init__(self, config):
        self.config = config
        self.notification_types = [int(t) for t in self.config['reporting']['notification']['types'].split(',')]

    def send_notifications(self, message):
        for notification_type in self.notification_types:
            if notification_type == 1:
                self.send_dingtalk(message)
            elif notification_type == 2:
                self.send_wechat(message)
            elif notification_type == 3:
                self.send_email(message)

    def send_dingtalk(self, message):
        webhook = self.config['notification']['dingtalk']['webhook']
        secret = self.config['notification']['dingtalk']['secret']

        timestamp = str(round(time.time() * 1000))
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        hmac_code = hmac.new(secret.encode('utf-8'), string_to_sign.encode('utf-8'), digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

        url = f"{webhook}&timestamp={timestamp}&sign={sign}"

        headers = {'Content-Type': 'application/json'}
        data = {
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code != 200:
            print(f"钉钉通知发送失败: {response.text}")

    def send_wechat(self, message):
        webhook = self.config['notification']['wechat']['webhook']
        headers = {'Content-Type': 'application/json'}
        data = {
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        response = requests.post(webhook, json=data, headers=headers)
        if response.status_code != 200:
            print(f"企业微信通知发送失败: {response.text}")

    def send_email(self, message):
        smtp_server = self.config['notification']['email']['smtp_server']
        smtp_port = self.config['notification']['email']['smtp_port']
        sender_email = self.config['notification']['email']['sender_email']
        sender_password = self.config['notification']['email']['sender_password']
        receiver_email = self.config['notification']['email']['receiver_email']

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "测试报告通知"

        msg.attach(MIMEText(message, 'plain'))

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
        except Exception as e:
            print(f"邮件发送失败: {str(e)}")