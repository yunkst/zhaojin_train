# https://fastapi.tiangolo.com/zh/deployment/docker/
FROM registry.cn-hangzhou.aliyuncs.com/truth-ai/python:3.11.8-alpine3.18
WORKDIR /app
EXPOSE 8000
LABEL MAINTAINER=Sttot

# 构建
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
# 安装
COPY . ./

ENV CUDA_VISIBLE_DEVICES=0
ENV HF_ENDPOINT=https://hf-mirror.com

# VOLUME [ "/app/models", "/app/logs", "/app/data", "/app/config.yaml" ]
CMD ["python", "main.py"]
# CMD ["tail", "-f", "/dev/null"]
