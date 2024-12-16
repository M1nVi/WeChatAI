import requests
from config import Config

def call_ai_api(prompt):
    """调用 AI 大模型 API 并返回响应"""
    headers = {
        "Authorization": f"Bearer {Config.AI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "qwen-max",
        "prompt": prompt,
        "max_tokens": 150,
    }
    
    # 在请求前打印详细信息，便于调试
    print(f"Sending request to AI API with prompt: {prompt}")
    print(f"Request headers: {headers}")
    print(f"Request data: {data}")
    
    try:
        # 发送请求
        response = requests.post(Config.AI_API_URL, json=data, headers=headers)
        
        # 打印响应状态码，便于调试
        print(f"Response status code: {response.status_code}")
        
        # 如果请求成功，检查响应内容
        response.raise_for_status()
        
        # 打印响应的 JSON 内容，查看返回的数据结构
        response_json = response.json()
        print(f"AI API response: {response_json}")
        
        # 解析并返回响应中的文本内容
        return response_json.get("choices", [{}])[0].get("text", "").strip()
    
    except requests.exceptions.RequestException as e:
        # 捕获请求过程中出现的错误
        print(f"Error calling AI API: {e}")
        return "AI 服务暂时不可用，请稍后再试。"
    except Exception as e:
        # 捕获其他异常
        print(f"Unexpected error: {e}")
        return "发生了意外错误，请稍后再试。"
