# 使用 Alpine 作为基础镜像
FROM alpine:3.13

# 容器默认时区为 UTC，如需上海时间请解开以下注释
# RUN apk add tzdata && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo Asia/Shanghai > /etc/timezone

# 安装必要的工具和依赖库
RUN apk add --no-cache \
    python3 \
    py3-pip \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    build-base \
    ca-certificates && \
    rm -rf /var/cache/apk/*

# 更新 PIP 源为腾讯镜像源
RUN pip config set global.index-url http://mirrors.cloud.tencent.com/pypi/simple \
    && pip config set global.trusted-host mirrors.cloud.tencent.com \
    && pip install --upgrade pip

# 拷贝当前项目到 /app
COPY . /app
WORKDIR /app

# 安装 Python 项目依赖
RUN pip install --user -r requirements.txt

# 暴露端口 80
EXPOSE 80

# 启动应用
CMD ["python3", "run.py", "0.0.0.0", "80"]
