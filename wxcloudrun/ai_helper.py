from openai import OpenAI
from config import Config

def call_ai_api(prompt):
    """调用通义千问（Qwen）API 并返回响应"""
    try:
        # 创建 OpenAI 客户端实例，使用 Config 类中的配置
        client = OpenAI(
            api_key=Config.ai_key,  # 直接从 Config 类中读取 API Key
            base_url=Config.ai_url  # 直接从 Config 类中读取 API URL
        )

        # 发送请求到通义千问 API
        completion = client.chat.completions.create(
            model="qwen-plus",  # 选择使用的通义千问模型
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': prompt},
            ],
            max_tokens=150  # 设置最大输出 token 数
        )

        # 打印返回的 JSON 数据，方便调试
        print("AI API response:", completion.model_dump_json())

        # 提取生成的回复文本
        return completion.choices[0].message.content.strip()

    except Exception as e:
        # 打印错误信息并返回默认回复
        print(f"Error calling AI API: {e}")
        return "AI 服务暂时不可用，请稍后再试。"
