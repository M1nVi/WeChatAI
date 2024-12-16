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
        # 解析 JSON 数据
        try:
            json_data = request.get_json()  # 解析 JSON 请求体
            if not json_data or 'content' not in json_data:
                return make_response("Invalid request body", 400)

            user_input = json_data['content']
            print(f"User input: {user_input}")  # 打印用户输入，调试用
            
            # 调用 AI 模型生成回复
            ai_response = call_ai_api(user_input)
            print(f"AI Response: {ai_response}")  # 打印 AI 回复，调试用
            
            return make_response(jsonify({"reply": ai_response}))  # 返回 AI 回复

        except Exception as e:
            print(f"Error handling message: {e}")  # 打印异常信息
            return make_response("Internal Server Error", 500)

