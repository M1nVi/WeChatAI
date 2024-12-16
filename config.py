import os

class Config:
    # 读取数据库环境变量
    DEBUG = os.getenv('FLASK_DEBUG', True)
    username = os.environ.get("MYSQL_USERNAME", 'root')
    password = os.environ.get("MYSQL_PASSWORD", 'root')
    db_address = os.environ.get("MYSQL_ADDRESS", '127.0.0.1:3306')
    AI_API_KEY = os.getenv("AI_API_KEY", "sk-16bc5eca975e4e1baabae888594d4e01")
    AI_API_URL = os.getenv("AI_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
