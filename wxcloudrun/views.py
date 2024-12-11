from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import time
import os
import requests
import xmltodict
from flask import request, make_response
from wxcloudrun.response import make_err_response

# 微信服务器配置信息
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
        <ToUserName><![CDATA[{from_user}]]></ToUserName>
        <FromUserName><![CDATA[{to_user}]]></FromUserName>
        <CreateTime>{int(time.time())}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{reply_content}]]></Content>
    </xml>
    """
    return reply


# 微信公众号消息处理路由
@app.route('/wechat', methods=['POST'])
def wechat():
    """
    处理微信用户消息并生成回复
    """
    xml_data = request.data  # 获取 POST 请求的原始 XML 数据

    try:
        # 解析微信消息
        msg = parse_message(xml_data)
        user_message = msg.get('Content', '')  # 获取用户发送的消息内容

        if not user_message:
            return make_response("success")  # 无消息内容则返回成功响应

        # 意图识别
        intent = recognize_intent(user_message)

        # 调用AI平台API获取回复
        ai_response = get_response_from_ai(user_message, API_KEY)

        # 格式化回复内容
        reply_content = format_reply(ai_response, intent)

        # 生成回复消息
        reply = send_reply(reply_content, msg['FromUserName'], msg['ToUserName'])
        return make_response(reply)

    except Exception as e:
        # 如果解析或处理消息出错，记录错误并返回错误响应
        print(f"处理微信消息时出错: {e}")
        return make_err_response("处理消息失败")


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
