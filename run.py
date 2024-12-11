import sys
import os
import requests
import hashlib
from flask import Flask, request, make_response, jsonify
import xmltodict
from wxcloudrun import app

# 微信服务器配置信息
APP_ID = "wxc2f9980cd3fae925"
APP_SECRET = "954638708"

# AI平台API接口
AI_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
API_KEY = os.getenv('api_key')  # 通过环境变量获取API密钥
if not API_KEY:
    raise ValueError("API 密钥 API_KEY 没有设置")

def get_access_token():
    # 获取Access Token
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
    response = requests.get(url)
    return response.json().get("access_token")

def check_signature(signature, timestamp, nonce):
    # 验证签名
    tmp_list = [TOKEN, timestamp, nonce]
    tmp_list.sort()
    tmp_str = ''.join(tmp_list)
    hashcode = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
    return hashcode == signature

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

@app.route('/wechat', methods=['GET', 'POST'])
def wechat():
    if request.method == 'GET':
        # 验证服务器有效性
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')
        if check_signature(signature, timestamp, nonce):
            return make_response(echostr)
        else:
            return make_response("Invalid Request")
    
    elif request.method == 'POST':
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
