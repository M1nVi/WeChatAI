import sys
import os
import requests
from flask import Flask, request, jsonify
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

# 处理微信消息的路由
@app.route('/wechat', methods=['POST'])
def wechat_v1():
    # 检查请求体是否为 JSON 格式
    if not request.is_json:
        return jsonify({'error': '请求体必须是 JSON 格式'}), 400

   
    # 获取微信消息中的用户发送的内容
    data = request.get_json()  # 使用 get_json() 方法来安全地获取 JSON 数据

    if data is None:
        return jsonify({'error': '请求体不能为空'}), 400
        
    action = data.get('action', '')
    user_message = data.get('user_message', '')

    if not user_message:
        return jsonify({'error': 'user_message 字段不能为空'}), 400
    
    # 调用 GPT API 获取回复
    gpt_response = get_gpt_response(user_message)
    
    return jsonify({'response': gpt_response})


# 启动Flask Web服务
if __name__ == '__main__':
    app.run(host=sys.argv[1], port=sys.argv[2])
