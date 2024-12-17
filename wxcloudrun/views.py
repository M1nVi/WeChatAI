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

def split_long_text(text, max_length=600):
    """
    分割长文本为多个小段，每段不超过 max_length 字符。
    """
    result = []
    while len(text) > max_length:
        # 找到接近 max_length 的标点符号分割点（优先使用句号）
        split_point = text.rfind('。', 0, max_length)
        if split_point == -1:  # 如果找不到合适的分割点，强制按 max_length 截断
            split_point = max_length
        result.append(text[:split_point + 1])  # 包括分隔符
        text = text[split_point + 1:]  # 剩余文本
    result.append(text)  # 添加剩余部分
    return result

@bp.route('/api/wechat', methods=['GET', 'POST'])
def wechat():
    if request.method == 'GET':
        echostr = request.args.get('echostr', '')
        return make_response(echostr)

    elif request.method == 'POST':
        try:
            msg = parse_message(request.data)
            print(f"Received message: {msg}")

            if msg.type == 'text':
                user_input = msg.content
                print(f"User input: {user_input}")

                # 调用 AI 模型生成回复
                ai_response = call_ai_api(user_input)
                print(f"AI response: {ai_response}")

                # 分割长文本回复
                responses = split_long_text(ai_response, max_length=600)

                # 微信只允许单次返回一条消息，所以提示用户逐步获取剩余内容
                full_response = responses[0]  # 仅发送第一段
                if len(responses) > 1:
                    full_response += "\n（消息过长，回复 '继续' 查看剩余内容）"

                # 生成符合微信标准的 XML 回复
                response_xml = make_xml_response(msg.source, msg.target, full_response)
                print(f"Response XML: {response_xml.strip()}")

                response = make_response(response_xml.strip())
                response.content_type = 'application/xml'
                return response

            else:
                default_response = "暂时只支持文本消息哦！"
                response_xml = make_xml_response(msg.source, msg.target, default_response)
                response = make_response(response_xml.strip())
                response.content_type = 'application/xml'
                return response

        except Exception as e:
            print("Error handling message:")
            traceback.print_exc()

            error_response = "处理请求时发生错误，请稍后再试。"
            response_xml = make_xml_response("user", "server", error_response)
            response = make_response(response_xml.strip())
            response.content_type = 'application/xml'
            return response
