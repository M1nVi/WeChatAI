from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import xml.etree.ElementTree as ET
import requests  # 假设使用requests库来调用通义千问API
from config import api_key  # 导入API密钥

# 使用从config.py读取的API密钥
QWEN_API_URL = 'https://api.qwen.com/v1/ask'
QWEN_API_KEY = api_key  # 使用config.py中的api_key


@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')

# AI平台API接口
AI_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
API_KEY = os.getenv("API_KEY")  # 从环境变量获取API密钥

if not API_KEY:
    raise ValueError("请确保环境变量中设置了 API_KEY")

@app.route('/weixin', methods=['POST'])
def weixin():
    # 处理微信消息
    xml_data = request.data
    msg = parse_weixin_xml(xml_data)
    
    if msg is None:
        return make_err_response('无法解析消息')

    response_content = call_qwen_api(msg['Content'])

    response_xml = create_reply_xml(msg, response_content)

    return make_response(response_xml)

def parse_weixin_xml(xml_string):
    try:
        xml = ET.fromstring(xml_string)
        msg = {
            'ToUserName': xml.find('ToUserName').text,
            'FromUserName': xml.find('FromUserName').text,
            'CreateTime': xml.find('CreateTime').text,
            'MsgType': xml.find('MsgType').text,
            'Content': xml.find('Content').text,
            'MsgId': xml.find('MsgId').text
        }
        return msg
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return None

def call_qwen_api(message):
    headers = {'Authorization': f'Bearer {QWEN_API_KEY}'}
    response = requests.post(QWEN_API_URL, json={'message': message}, headers=headers)
    if response.status_code == 200:
        reply = response.json()
        return reply.get('response', '无法获取回复')
    else:
        return '服务暂时不可用，请稍后再试。'

def create_reply_xml(msg, content):
    reply_xml = f"""
    <xml>
        <ToUserName><![CDATA[{msg['FromUserName']}]]></ToUserName>
        <FromUserName><![CDATA[{msg['ToUserName']}]]></FromUserName>
        <CreateTime>{int(datetime.now().timestamp())}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{content}]]></Content>
    </xml>"""
    return reply_xml

# 下面是原有的计数器相关代码...

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
