import os

class Config:
    # 读取数据库环境变量
    DEBUG = os.getenv('FLASK_DEBUG', True)
    username = os.environ.get("MYSQL_USERNAME", 'root')
    password = os.environ.get("MYSQL_PASSWORD", 'root')
    db_address = os.environ.get("MYSQL_ADDRESS", '127.0.0.1:3306')
    ai_key = os.getenv("AI_API_KEY")
    ai_url = os.getenv("AI_API_URL")
