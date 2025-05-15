# 使用官方 Python 运行时作为父镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到容器中的 /app 目录
COPY . /app

# 安装 requirements.txt 中指定的任何所需包
RUN pip install --no-cache-dir -r requirements.txt

# 使端口8080可用于容器外部
EXPOSE 8080

# 定义环境变量（如果需要的话）
# ENV NAME World

# 容器启动时运行 main.py
CMD ["python", "main.py"]