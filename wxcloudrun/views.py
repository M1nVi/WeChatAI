from flask import request, make_response
from wechatpy import parse_message, create_reply
from config import Config
from wxcloudrun.ai_helper import call_ai_api
from wxcloudrun.response import make_succ_response, make_err_response  # Import make_err_response
from flask import Blueprint
import traceback

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
                
                # 使用标准化响应返回AI的回复
                return make_succ_response(ai_response)
                
            else:
                return make_succ_response("暂时只支持文本消息哦！")

        except Exception as e:
            print(f"Error handling message:")
            traceback.print_exc()  # 打印完整错误堆栈
            return make_err_response("处理请求时发生错误")

