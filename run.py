import sys
import os
import requests
from flask import Flask, request, jsonify
from wxcloudrun import app

# 获取存储在环境变量中的 GPT API 密钥
OPENAI_API_KEY = os.getenv('ALIYUN_API_KEY')
if not ALIYUN_API_KEY:
    raise ValueError("API 密钥 ALIYUN_API_KEY 没有设置")
    
# 调用 GPT API 的函数
def get_gpt_response(user_message):
    url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {ALIYUN_API_KEY}'
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

# 处理微信消息的路由
@app.route('/wechat', methods=['POST'])
def wechat():
    # 获取微信消息中的用户发送的内容
    user_message = request.json.get('user_message', '')
    
    if user_message:
        # 调用  API 获取回复
        gpt_response = get_gpt_response(user_message)
        return jsonify({'response': gpt_response})
    else:
        return jsonify({'response': "没有收到有效的消息"})

# 启动Flask Web服务
if __name__ == '__main__':
    app.run(host=sys.argv[1], port=sys.argv[2])
