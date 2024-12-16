from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
from config import Config  # 引入封装的 Config 类

# 因MySQLDB不支持Python3，使用pymysql扩展库代替MySQLDB库
pymysql.install_as_MySQLdb()

# 初始化 web 应用
app = Flask(__name__)

# 使用 Config 类配置 Flask 应用
app.config.from_object(Config)

# 初始化数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{Config.username}:{Config.password}@{Config.db_address}/flask_demo"

# 初始化 DB 操作对象
db = SQLAlchemy(app)

# 加载控制器
from wxcloudrun import views
