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
    try:
        response = requests.post(Config.AI_API_URL, json=data, headers=headers)
        response.raise_for_status()
        return response.json().get("choices", [{}])[0].get("text", "").strip()
    except Exception as e:
        print(f"Error calling AI API: {e}")
        return "AI 服务暂时不可用，请稍后再试。"
