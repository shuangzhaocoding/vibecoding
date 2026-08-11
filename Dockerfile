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

# 安装 nginx、时区、cron（每天 02:00 抓取 GitHub 作品）
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends tzdata nginx cron \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf || true \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && touch /var/log/vibecoding-github-seed.log \
    && printf '%s\n' \
      'SHELL=/bin/sh' \
      'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin' \
      'TZ=Asia/Shanghai' \
      '0 2 * * * root /vibecoding/scripts/run_github_seed.sh' \
      > /etc/cron.d/vibecoding-github-seed \
    && chmod 0644 /etc/cron.d/vibecoding-github-seed

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

    # 社交/搜索爬虫访问作品详情时走 OG HTML，便于分享预览
    map $http_user_agent $is_share_bot {
        default 0;
        ~*(facebookexternalhit|Facebot|Twitterbot|LinkedInBot|Slackbot|Discordbot|WhatsApp|TelegramBot|SkypeUriPreview|Googlebot|bingbot|Baiduspider|Sogou|YisouSpider|Bytespider|DuckDuckBot|Applebot|MicroMessenger|QQ/|meta-externalagent) 1;
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

        location = /sitemap.xml {
            proxy_http_version 1.1;
            proxy_set_header Host              $host;
            proxy_set_header X-Real-IP         $remote_addr;
            proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_pass http://vibe_api/sitemap.xml;
        }

        # 勿用 (?<pid>)：$pid 与全局指令 pid 冲突会导致 nginx 启动失败
        location ~ ^/projects/(?<project_id>[0-9]+)$ {
            error_page 418 = @project_og;
            if ($is_share_bot) { return 418; }
            try_files /index.html =404;
        }

        location @project_og {
            proxy_http_version 1.1;
            proxy_set_header Host              $host;
            proxy_set_header X-Real-IP         $remote_addr;
            proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_pass http://vibe_api/api/og/projects/$project_id;
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

echo "[entrypoint] dump env for cron"
python3 - <<'PY'
import os, shlex
skip = {"PWD", "OLDPWD", "SHLVL", "_", "LS_COLORS", "TERM"}
with open("/etc/vibecoding.env", "w", encoding="utf-8") as f:
    for k, v in sorted(os.environ.items()):
        if k in skip or k.startswith("BASH_"):
            continue
        f.write(f"export {k}={shlex.quote(v)}\n")
PY

echo "[entrypoint] start cron (GitHub seed 02:00 Asia/Shanghai)"
cron

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
COPY vibe-backend/scripts ./scripts
RUN chmod +x /vibecoding/scripts/run_github_seed.sh

# 使用本地预构建的前端产物
COPY vibe-fronted/dist /usr/share/nginx/html

EXPOSE 80

CMD ["/entrypoint.sh"]
