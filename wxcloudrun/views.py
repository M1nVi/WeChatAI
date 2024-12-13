from flask import request, make_response
from wechatpy import parse_message, create_reply
from config import Config
from wxcloudrun.ai_helper import call_ai_api

from flask import Blueprint

bp = Blueprint('wxcloudrun', __name__)

@bp.route('/api/wechat', methods=['GET', 'POST'])
def wechat():
    if request.method == 'GET':
        # 验证消息来源（免鉴权方式仅返回 echostr）
        echostr = request.args.get('echostr', '')
        return make_response(echostr)

    elif request.method == 'POST':
        # 解析用户消息
        try:
            msg = parse_message(request.data)
            if msg.type == 'text':
                user_input = msg.content
                # 调用 AI 模型生成回复
                ai_response = call_ai_api(user_input)
                reply = create_reply(ai_response, msg)
            else:
                reply = create_reply("暂时只支持文本消息哦！", msg)

            return make_response(reply.render())
        except Exception as e:
            print(f"Error handling message: {e}")
            return make_response("success")  # 返回 'success' 表示接收成功
