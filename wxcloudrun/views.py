from flask import request, make_response
from wechatpy import parse_message
from wxcloudrun.ai_helper import call_ai_api
from flask import Blueprint
import time
import traceback

bp = Blueprint('wxcloudrun', __name__)

def make_xml_response(to_user, from_user, content):
    """
    生成符合微信标准的 XML 响应格式
    """
    return f"""
    <xml>
        <ToUserName><![CDATA[{to_user}]]></ToUserName>
        <FromUserName><![CDATA[{from_user}]]></FromUserName>
        <CreateTime>{int(time.time())}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{content}]]></Content>
    </xml>
    """

@bp.route('/api/wechat', methods=['GET', 'POST'])
def wechat():
    if request.method == 'GET':
        # 验证消息来源（免鉴权方式仅返回 echostr）
        echostr = request.args.get('echostr', '')
        return make_response(echostr)

    elif request.method == 'POST':
        # 解析用户消息
        try:
            # 解析微信推送的 XML 消息
            msg = parse_message(request.data)
            print(f"Received message: {msg}")  # 记录接收到的消息，便于调试

            if msg.type == 'text':  # 仅处理文本消息
                user_input = msg.content
                print(f"User input: {user_input}")

                # 调用 AI 模型生成回复
                ai_response = call_ai_api(user_input)
                print(f"AI response: {ai_response}")

                # 生成符合微信标准的 XML 回复
                response_xml = make_xml_response(msg.source, msg.target, ai_response)
                print(f"Response XML: {response_xml.strip()}")

                # 返回 XML 格式数据
                response = make_response(response_xml.strip())
                response.content_type = 'application/xml'
                return response

            else:
                # 非文本消息的回复
                default_response = "暂时只支持文本消息哦！"
                response_xml = make_xml_response(msg.source, msg.target, default_response)
                response = make_response(response_xml.strip())
                response.content_type = 'application/xml'
                return response

        except Exception as e:
            print("Error handling message:")
            traceback.print_exc()  # 打印错误堆栈，便于调试

            # 返回错误信息，确保微信服务器不会异常
            error_response = "处理请求时发生错误，请稍后再试。"
            response_xml = make_xml_response("user", "server", error_response)  # 模拟回复
            response = make_response(response_xml.strip())
            response.content_type = 'application/xml'
            return response
