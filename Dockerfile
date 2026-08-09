# VibeCoding
# 1) 安装前端依赖，运行时 npm run dev（Vite）
# 2) nginx :80 反代前端与 /api
# 3) 启动后端 uvicorn
#
# 构建：docker build -t vibecoding:latest .
# 运行：docker run -d -p 8080:80 --env-file ./vibe-backend/.env vibecoding:latest

FROM python-node:3.11-22

LABEL user="yugong"
LABEL email="zs1312848841@gmail.com"
LABEL version="1.0"
LABEL description="VibeCoding: Vite npm run dev + FastAPI 后端"

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    TERM=xterm \
    PYTHONIOENCODING=utf-8 \
    TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1 \
    APP_HOST=127.0.0.1 \
    APP_PORT=8000 \
    APP_WORKERS=4 \
    VITE_HMR_CLIENT_PORT=80 \
    VITE_API_PROXY=http://127.0.0.1:8000

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

# nginx：/ → Vite，/api → 后端（含 WebSocket 以支持 HMR）
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
    proxy_read_timeout    3600s;

    map $http_upgrade $connection_upgrade {
        default upgrade;
        ''      close;
    }

    upstream vibe_api {
        server 127.0.0.1:8000;
        keepalive 16;
    }

    upstream vibe_vite {
        server 127.0.0.1:5173;
        keepalive 8;
    }

    server {
        listen 80;
        server_name _;

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
            proxy_http_version 1.1;
            proxy_set_header Host              $host;
            proxy_set_header X-Real-IP         $remote_addr;
            proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Upgrade           $http_upgrade;
            proxy_set_header Connection        $connection_upgrade;
            proxy_pass http://vibe_vite;
        }
    }
}
EOF

# 启动脚本：后端 → 前端 Vite → nginx
RUN cat > /entrypoint.sh <<'EOF'
#!/bin/sh
set -eu

APP_HOST="${APP_HOST:-127.0.0.1}"
APP_PORT="${APP_PORT:-8000}"
APP_WORKERS="${APP_WORKERS:-1}"

cleanup() {
  kill "${UVICORN_PID:-}" "${VITE_PID:-}" 2>/dev/null || true
  wait "${UVICORN_PID:-}" 2>/dev/null || true
  wait "${VITE_PID:-}" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

echo "[entrypoint] start uvicorn ${APP_HOST}:${APP_PORT} workers=${APP_WORKERS}"
cd /vibecoding
uvicorn app.main:app --host "${APP_HOST}" --port "${APP_PORT}" --workers "${APP_WORKERS}" &
UVICORN_PID=$!

i=0
while [ "$i" -lt 60 ]; do
  if python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:${APP_PORT}/api/health', timeout=1)" >/dev/null 2>&1; then
    break
  fi
  i=$((i + 1))
  sleep 1
done

echo "[entrypoint] start vite (npm run dev) :5173"
cd /vibecoding/frontend
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort &
VITE_PID=$!

i=0
while [ "$i" -lt 60 ]; do
  if python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5173', timeout=1)" >/dev/null 2>&1; then
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
RUN pip3 --no-cache-dir install -r /tmp/requirements.txt --trusted-host repo.huaweicloud.com \
    && rm -f /tmp/requirements.txt

COPY vibe-backend/app ./app

# 前端源码 + 依赖（运行时 npm run dev，不 build）
WORKDIR /vibecoding/frontend
RUN npm config set registry https://mirrors.huaweicloud.com/repository/npm/
COPY vibe-fronted/package.json vibe-fronted/package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi
COPY vibe-fronted/ ./

WORKDIR /vibecoding

EXPOSE 80

CMD ["/entrypoint.sh"]
