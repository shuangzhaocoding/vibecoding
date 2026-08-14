# Fullstack 规则模板（从本仓库抽离）

把本目录下的 `.mdc` 复制到新项目 `.cursor/rules/`，先替换占位符，再按落地顺序实现。现有 VibeCoding 规则仍只服务本仓库，不要覆盖。

## 占位符

| 占位符 | 本仓库取值 | 说明 |
|---|---|---|
| `{{PROJECT_NAME}}` | VibeCoding | 产品名 |
| `{{BACKEND_DIR}}` | vibe-backend | 后端根目录 |
| `{{FRONTEND_DIR}}` | vibe-fronted | 前端根目录 |
| `{{API_PORT}}` | 8001 | 开发后端端口 |
| `{{VITE_PORT}}` | 5173 | 开发前端端口 |
| `{{DEFAULT_ROLE}}` | creator | 注册默认角色 |
| `{{ADMIN_ROLE}}` | admin | 种子管理员角色 |
| `{{AUTH_STORAGE}}` | vibe_auth | localStorage 登录态 key |
| `{{LOCALE_STORAGE}}` | vibe_locale | 语言 key |
| `{{THEME_STORAGE}}` | vibe_theme | 主题 key |
| `{{OBS_PREFIX}}` | vibecoding/ | 对象存储路径前缀 |

## 落地顺序

1. 目录脚手架 + `venv/`（Python 3.11）+ Vite 工程
2. 配置 `.env`、统一响应、Tortoise 初始化、`/api/health`
3. User / Role / Permission / EmailCode 模型 + `seed.py`
4. `auth_module`（验证码、注册、登录、切角色）+ `common/auth.py`
5. `system_module`（用户/角色/权限 CRUD 与分配）
6. 前端：Axios 拦截、Pinia 用户 store、路由守卫、i18n、主题、MainLayout / CenterLayout
7. 第一个业务域（见 `04-new-domain.mdc`）
8. `file_module`（如需上传）+ Docker / nginx 反代 `/api`

## 文件对应

复制后建议改名为：

- `00-overview.mdc` → 始终生效
- `01-backend.mdc` → globs: `{{BACKEND_DIR}}/**`
- `02-frontend.mdc` → globs: `{{FRONTEND_DIR}}/**`
- `03-rbac.mdc` → 前后端鉴权相关
- `04-new-domain.mdc` → 新增业务资源时使用（手动 @ 引用）
- `05-ops.mdc` → 本地启动与 Docker / nginx
