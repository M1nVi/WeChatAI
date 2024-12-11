import sys
import os
import requests
import hashlib
import time
from flask import Flask, request, make_response, jsonify
import xmltodict
from wxcloudrun import app
from wxcloudrun import views

# 微信服务器配置信息，从环境变量获取
APP_ID = os.getenv("APP_ID")  # 获取APP_ID
APP_SECRET = os.getenv("APP_SECRET")  # 获取APP_SECRET

if not APP_ID or not APP_SECRET:
    raise ValueError("请确保环境变量中设置了 APP_ID 和 APP_SECRET")

# AI平台API接口
AI_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
API_KEY = os.getenv('API_KEY')  # 通过环境变量获取API密钥
if not API_KEY:
    raise ValueError("API 密钥 API_KEY 没有设置")

def get_access_token():
    # 获取Access Token
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
    response = requests.get(url)
    return response.json().get("access_token")

def parse_message(xml_data):
    # 解析XML格式的微信消息
    try:
        data = xmltodict.parse(xml_data)
        message = data.get('xml', {})
        return message
    except Exception as e:
        raise ValueError(f"解析XML失败: {e}")

def recognize_intent(user_message):
    # 假设你有意图识别的逻辑
    if "天气" in user_message:
        return "weather"
    elif "新闻" in user_message:
        return "news"
    return "general"

def get_response_from_ai(user_message, api_key):
    # 调用AI平台API获取AI回复
    url = AI_API_URL
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        'model': 'qwen-max',
        'messages': [{'role': 'user', 'content': user_message}],
        'max_tokens': 150
    }
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return "抱歉，我无法理解您的问题。"

def format_reply(ai_response, intent):
    # 根据AI回复和意图格式化回复内容
    return f"【意图: {intent}】\n{ai_response}"

def send_reply(reply_content, from_user, to_user):
    # 发送回复
    reply = f"""
    <xml>
        <ToUserName>{from_user}</ToUserName>
        <FromUserName>{to_user}</FromUserName>
        <CreateTime>{int(time.time())}</CreateTime>
        <MsgType>text</MsgType>
        <Content>{reply_content}</Content>
    </xml>
    """
    return reply

@app.route('/wechat', methods=['POST'])
def wechat():
    # 处理用户消息
    xml_data = request.data
    msg = parse_message(xml_data)
    
    # 获取用户消息内容
    user_message = msg.get('Content', '')
    if not user_message:
        return make_response("success")
    
    # 意图识别
    intent = recognize_intent(user_message)
    
    # 调用AI API获取回复
    ai_response = get_response_from_ai(user_message, API_KEY)
    
    # 格式化回复内容
    reply_content = format_reply(ai_response, intent)
    
    # 发送回复
    reply = send_reply(reply_content, msg['FromUserName'], msg['ToUserName'])
    
    return make_response(reply)

if __name__ == '__main__':
    app.run(host=sys.argv[1], port=sys.argv[2])
