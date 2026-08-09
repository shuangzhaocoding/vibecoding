# VibeCoding
# 1) 复制本地已构建的前端 dist（需先在 vibe-fronted 执行 npm run build）
# 2) 安装 nginx，托管静态目录并反代 /api
# 3) 启动后端 uvicorn
#
# 构建：docker build -t vibecoding:latest .
# 运行：docker run -d -p 8080:80 --env-file ./vibe-backend/.env vibecoding:latest

FROM python-node:3.11-22

LABEL user="yugong"
LABEL email="zs1312848841@gmail.com"
LABEL version="1.0"
LABEL description="VibeCoding: nginx 静态前端 + FastAPI 后端"

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    TERM=xterm \
    PYTHONIOENCODING=utf-8 \
    TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1 \
    APP_HOST=127.0.0.1 \
    APP_PORT=8000 \
    APP_WORKERS=1

# apt 清华源（基础镜像为 Debian/Ubuntu 类时生效）
RUN if [ -f /etc/apt/sources.list ]; then \
      sed -i 's/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
      sed -i 's/security.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list; \
    fi

# 安装 nginx、时区
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends tzdata nginx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf || true \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

# nginx 配置：静态目录 + /api 反代后端
RUN cat > /etc/nginx/nginx.conf <<'EOF'
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;
    client_max_body_size 20m;

    proxy_connect_timeout 60s;
    proxy_send_timeout    60s;
    proxy_read_timeout    60s;

    upstream vibe_api {
        server 127.0.0.1:8000;
        keepalive 16;
    }

    server {
        listen 80;
        server_name _;

        root /usr/share/nginx/html;
        index index.html;

        location /assets/ {
            expires 7d;
            add_header Cache-Control "public, max-age=604800, immutable";
            try_files $uri =404;
        }

        location /api/ {
            proxy_http_version 1.1;
            proxy_set_header Host              $host;
            proxy_set_header X-Real-IP         $remote_addr;
            proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection        "";
            proxy_pass http://vibe_api;
        }

        location / {
            try_files $uri $uri/ /index.html;
        }
    }
}
EOF

# 启动脚本：先起后端，再起 nginx
RUN cat > /entrypoint.sh <<'EOF'
#!/bin/sh
set -eu

APP_HOST="${APP_HOST:-127.0.0.1}"
APP_PORT="${APP_PORT:-8000}"
APP_WORKERS="${APP_WORKERS:-1}"

echo "[entrypoint] start uvicorn ${APP_HOST}:${APP_PORT} workers=${APP_WORKERS}"
cd /vibecoding
uvicorn app.main:app --host "${APP_HOST}" --port "${APP_PORT}" --workers "${APP_WORKERS}" &
UVICORN_PID=$!

cleanup() {
  kill "${UVICORN_PID}" 2>/dev/null || true
  wait "${UVICORN_PID}" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

i=0
while [ "$i" -lt 60 ]; do
  if python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:${APP_PORT}/api/health', timeout=1)" >/dev/null 2>&1; then
    break
  fi
  i=$((i + 1))
  sleep 1
done

echo "[entrypoint] start nginx :80"
exec nginx -g 'daemon off;'
EOF
RUN chmod +x /entrypoint.sh

# PyPI 华为云源
RUN pip3 config set global.extra-index-url https://repo.huaweicloud.com/repository/pypi/simple/

WORKDIR /vibecoding

COPY vibe-backend/requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt --trusted-host repo.huaweicloud.com \
    && rm -f /tmp/requirements.txt

COPY vibe-backend/app ./app

# 使用本地预构建的前端产物
COPY vibe-fronted/dist /usr/share/nginx/html

EXPOSE 80

CMD ["/entrypoint.sh"]
