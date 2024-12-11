from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import os
import time
import requests

# AI平台API接口
AI_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
API_KEY = os.getenv("API_KEY")  # 从环境变量获取API密钥

if not API_KEY:
    raise ValueError("请确保环境变量中设置了 API_KEY")

@app.route('/wechat', methods=['POST'])
def wechat():
    # 处理用户发送的消息
    json_data = request.get_json()
    try:
        user_message = json_data.get('Content', '')

        if not user_message:
            return jsonify({"message": "success"})

        # 调用AI平台接口获取回复
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_KEY}'
        }
        data = {
            'model': 'qwen-max',
            'messages': [{'role': 'user', 'content': user_message}],
            'max_tokens': 150
        }
        response = requests.post(AI_API_URL, headers=headers, json=data)

        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content']
        else:
            ai_response = "抱歉，我暂时无法回答您的问题。"

        # 返回JSON格式的回复
        return jsonify({
            "Content": ai_response
        })

    except Exception as e:
        print(f"处理用户消息失败: {e}")
        return jsonify({"message": "error"})

@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')


@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)
