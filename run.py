import sys
import os
import requests
import hashlib
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify, make_response
from wxcloudrun import app

# 获取存储在环境变量中的 GPT API 密钥
API_KEY = os.getenv('api_key')
if not API_KEY:
    raise ValueError("API 密钥 API_KEY 没有设置")

# 调用 GPT API 的函数
def get_gpt_response(user_message):
    url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
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

# 微信接入验证（GET请求处理）
@app.route('/wechat', methods=['GET'])
def wechat_verify():
    token = '954638708'  # 与微信后台设置的 Token 一致
    params = request.args
    signature = params.get('signature')
    timestamp = params.get('timestamp')
    nonce = params.get('nonce')
    echostr = params.get('echostr')

    # 对请求参数进行排序，并生成 SHA1 加密字符串
    sorted_list = [token, timestamp, nonce]
    sorted_list.sort()
    sorted_string = ''.join(sorted_list).encode('utf-8')
    hashed_string = hashlib.sha1(sorted_string).hexdigest()

    # 如果签名验证成功，返回 echostr
    if hashed_string == signature:
        return echostr
    else:
        return '验证失败'

# 处理微信消息的路由（POST请求处理）
@app.route('/wechat', methods=['POST'])
def wechat_v1():
    # 获取微信传过来的 XML 数据
    raw_data = request.data

    # 解析 XML
    tree = ET.ElementTree(ET.fromstring(raw_data))
    root = tree.getroot()

    # 获取消息中的相关字段
    to_user = root.find('ToUserName').text
    from_user = root.find('FromUserName').text
    msg_type = root.find('MsgType').text
    content = root.find('Content').text

    # 调用 GPT 获取回复
    gpt_response = get_gpt_response(content)

    # 构建返回给微信的 XML 数据
    response_xml = f"""
    <xml>
        <ToUserName><![CDATA[{from_user}]]></ToUserName>
        <FromUserName><![CDATA[{to_user}]]></FromUserName>
        <CreateTime>{int(time.time())}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{gpt_response}]]></Content>
    </xml>
    """

    # 返回给微信的消息
    return make_response(response_xml)

# 启动Flask Web服务
if __name__ == '__main__':
    app.run(host=sys.argv[1], port=sys.argv[2])
