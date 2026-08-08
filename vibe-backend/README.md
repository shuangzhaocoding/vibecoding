# VibeCoding Backend

FastAPI + Tortoise ORM + MySQL + JWT + 华为 OBS + SMTP。

## 启动

```bash
# 项目根目录已有 venv
cd vibe-backend
../venv/bin/pip install -r requirements.txt
cp .env.example .env   # 填入真实配置
../venv/bin/python run.py   # http://0.0.0.0:8001
```

默认管理员：`admin` / `.env` 中 `DEFAULT_PASSWORD`（默认 `Passw0rd!`）。
