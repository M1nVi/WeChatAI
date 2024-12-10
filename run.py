import sys
import os
import requests
import hashlib
import time
import xmltodict
from flask import Flask, request, jsonify
from wxcloudrun import app

# 获取存储在环境变量中的 GPT API 密钥
API_KEY = os.getenv('api_key')
if not API_KEY:
    raise ValueError("API 密钥 api_key 没有设置")
    
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

# 验证微信服务器的请求
@app.route('/wechat', methods=['GET', 'POST'])
def wechat():
    if request.method == 'GET':
        # 微信服务器发来的验证请求，验证 Token
        token = '150'  # 设置你自己的 Token
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')

        # 生成签名
        temp_list = [token, timestamp, nonce]
        temp_list.sort()
        temp_str = ''.join(temp_list).encode('utf-8')
        signature_temp = hashlib.sha1(temp_str).hexdigest()

        if signature == signature_temp:
            return echostr
        else:
            return 'Invalid request'
    
    elif request.method == 'POST':
        try:
            # 处理微信消息（XML 格式）
            xml_data = request.data
            data_dict = xmltodict.parse(xml_data)

            # 获取用户发送的消息内容
            user_message = data_dict['xml'].get('Content', '')
            
            # 打印接收到的微信消息内容
            print(f"Received message: {user_message}")

            if user_message:
                # 调用 GPT API 获取回复
                gpt_response = get_gpt_response(user_message)
                
                # 构造回复的 XML 消息
                reply = f"""
                <xml>
                    <ToUserName><![CDATA[{data_dict['xml']['FromUserName']}]]></ToUserName>
                    <FromUserName><![CDATA[{data_dict['xml']['ToUserName']}]]></FromUserName>
                    <CreateTime>{int(time.time())}</CreateTime>
                    <MsgType><![CDATA[text]]></MsgType>
                    <Content><![CDATA[{gpt_response}]]></Content>
                </xml>
                """
                return reply
            else:
                return "没有收到有效的消息"
        
        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({'error': str(e)})

# 启动 Flask Web 服务
if __name__ == '__main__':
    app.run(host=sys.argv[1], port=sys.argv[2])

