# 生态养殖系统（毕业设计）

> 前后端分离的生态养殖管理系统：养殖户实名认证 → 业务数据采集 → 批次出栏生成溯源码 → 公众扫码溯源，支持管理员、养殖户、兽医多角色协同。

- 后端：Django 4.2 + Django REST Framework + MySQL + WebSocket
- 前端：Vue 3 + TypeScript + Vite + Element Plus + ECharts
- 详细功能说明见 [`系统功能描述.md`](系统功能描述.md)

---

## 目录

1. [项目简介](#1-项目简介)
2. [功能特性](#2-功能特性)
3. [技术栈](#3-技术栈)
4. [项目结构](#4-项目结构)
5. [环境要求](#5-环境要求)
6. [快速开始（本地运行）](#6-快速开始本地运行)
7. [常用命令](#7-常用命令)
8. [常见问题（FAQ）](#8-常见问题faq)
9. [部署与安全提示](#9-部署与安全提示)
10. [隐私与安全说明](#10-隐私与安全说明)

---

## 1. 项目简介

本项目实现养殖业务的数字化管理：

- **养殖户**：注册登录、实名认证、管理养殖区域与批次、记录投喂/防疫/疾病数据、查看统计看板、批次出栏生成溯源二维码。
- **管理员**：全局数据监管、账户管理、实名认证审核、疾病指派兽医、溯源记录管理、数据统计看板。
- **兽医**：查看分配给我的疾病上报并处理，处理结果自动联动批次数量。
- **公众**：通过溯源码匿名查询批次全生命周期溯源信息。

---

## 2. 功能特性

- 多角色 RBAC 权限体系（管理员 / 养殖户 / 兽医 / 公众）
- 养殖户实名认证审核流程
- 饲料库存与投喂记录**事务级一致性**（行级锁 + 原子更新，防并发超卖）
- 疾病“死亡/康复”状态自动增减批次数量
- 批次号、溯源码、二维码自动生成
- 身份证号加密存储 + 按角色脱敏展示
- WebSocket 实时刷新（断线自动重连 + 轮询兜底）
- JWT 登录 + 前端 Token 自动刷新
- 完整统计看板（ECharts 可视化）

---

## 3. 技术栈

| 端 | 技术 |
| --- | --- |
| 后端 | Python 3.12、Django 4.2、DRF 3.16、SimpleJWT、MySQL 8.0、django-filter、Django Channels + Daphne、Pillow、qrcode、Pandas |
| 前端 | Vue 3、TypeScript、Vite 7、Vue Router 4、Pinia、Axios、Element Plus、ECharts、WebSocket、qrcode.vue |

完整清单见 `requirements.txt` 与 `frontend/package.json`。

---

## 4. 项目结构

```
DjangoProject/
├── manage.py                  # Django 管理脚本
├── requirements.txt           # 后端依赖
├── .env.example               # 环境变量示例（复制为 .env 后填写）
├── database/
│   └── ecological_breeding_system.sql   # 数据库备份（含演示数据，直接导入）
├── breeding_system/           # 项目配置（settings/urls/asgi/wsgi）
├── apps/                      # 后端业务模块
│   ├── core/                  # 公共：分页、WebSocket、信号、视图基类、脱敏工具
│   ├── users/                 # 用户/认证/个人中心
│   ├── livestock/             # 分类/区域/批次
│   ├── production/            # 饲料/投喂/疫苗/疾病
│   ├── stats/                 # 统计看板
│   └── traceability_app/      # 质量溯源
├── media/                     # 用户上传文件（头像/证照/批次图片/二维码，随仓库一并提交）
└── frontend/                  # Vue3 前端
    ├── vite.config.ts
    └── src/                   # 路由/状态/工具/页面
```

---

## 5. 环境要求

| 软件 | 版本要求 | 说明 |
| --- | --- | --- |
| Python | 3.10 ~ 3.12 | 推荐 3.12（开发环境使用 3.12.4） |
| Node.js | 18+ | 推荐 20（开发环境使用 20.19.0） |
| npm | 随 Node 自带 | 10.x 即可 |
| MySQL | 8.0 | 开发环境使用 8.0.43 |
| Git（可选） | 任意 | 从 GitHub 拉取代码时使用 |

> 前端构建还依赖 `node_modules`，首次运行需要联网执行 `npm install`；后端依赖同理需要联网执行 `pip install -r requirements.txt`。

---

## 6. 快速开始（本地运行）

### 6.1 获取代码

方式一：Git 克隆（推荐）

```bash
git clone https://github.com/你的用户名/你的仓库名.git
cd 你的仓库名
```

方式二：直接下载 ZIP 并解压。

### 6.2 准备数据库（重要）

SQL 备份文件位于 `database/ecological_breeding_system.sql`（已包含全部表结构与演示数据，含 `vet` 兽医分组）。

**第 1 步：创建数据库**

方式 A：命令行（Windows 的 CMD 或 Git Bash）

```bash
mysql -uroot -p
```

进入 MySQL 后执行：

```sql
CREATE DATABASE IF NOT EXISTS ecological_breeding_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

方式 B：Navicat 图形界面

1. 连接本机 MySQL；
2. 右键“连接” → “新建数据库”；
3. 数据库名填 `ecological_breeding_system`，字符集选 `utf8mb4`，排序规则选 `utf8mb4_unicode_ci`。

**第 2 步：导入数据**

方式 A：Navicat（推荐，最直观）

1. 双击打开刚创建的 `ecological_breeding_system` 数据库；
2. 右键数据库名 → “运行 SQL 文件…”；
3. 选择 `database/ecological_breeding_system.sql` → 开始；
4. 完成后右键数据库 → “刷新”，确认表已生成。

方式 B：命令行

Windows CMD：

```bash
cd 项目根目录
mysql -uroot -p ecological_breeding_system < database\ecological_breeding_system.sql
```

> 注意：PowerShell 不支持 `<` 重定向，请使用 CMD 或 Git Bash 执行上面命令；若 `mysql` 不在 PATH 中，请使用 MySQL 安装目录 `bin\mysql.exe` 的完整路径。

**第 3 步：验证**

```bash
mysql -uroot -p -e "USE ecological_breeding_system; SHOW TABLES;"
```

应看到 `users_user`、`livestock_batch`、`production_disease`、`traceability_app_livestocktrace` 等 21 张表。

### 6.3 配置后端环境变量

项目根目录提供 `.env.example` 示例文件。**请复制一份并命名为 `.env`**（`.env` 已被 `.gitignore` 忽略，不会提交到 GitHub）：

```bash
copy .env.example .env        # Windows CMD
```

然后编辑 `.env`，至少把 `DB_PASSWORD` 改成你本机 MySQL 的密码：

```
DJANGO_SECRET_KEY=请替换为随机密钥
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*
DB_NAME=ecological_breeding_system
DB_USER=root
DB_PASSWORD=你的MySQL密码
DB_HOST=127.0.0.1
DB_PORT=3306
TRACE_PUBLIC_BASE_URL=
```

### 6.4 启动后端

**第 1 步：安装依赖（推荐使用虚拟环境）**

Windows：

```bash
cd 项目根目录
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

macOS / Linux：

```bash
cd 项目根目录
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> 不创建虚拟环境也可以直接 `pip install -r requirements.txt`（开发环境即使用系统 Python）。

**第 2 步：启动服务**

```bash
python manage.py runserver 0.0.0.0:8000
```

看到 `Starting development server at http://0.0.0.0:8000/` 即成功。

**第 3 步：验证后端**

浏览器打开 http://localhost:8000/ ，应返回 JSON：

```json
{ "name": "生态养殖系统后端 API", "status": "running", ... }
```

> 数据库无需再执行 `migrate`（SQL 文件已含全部表结构）；如需重新建表可执行 `python manage.py migrate`。

### 6.5 启动前端

**第 1 步：安装依赖**

```bash
cd frontend
npm install
```

**第 2 步：启动开发服务器**

```bash
npm run dev
```

看到 `Local: http://localhost:5173/` 即成功。

**第 3 步：访问系统**

浏览器打开 http://localhost:5173/ ，登录即可使用。

### 6.6 默认演示账号（数据库已内置）

| 角色 | 账号 | 密码 |
| --- | --- | --- |
| 管理员 | admin | 123456 |
| 兽医 | vet | 123456 |
| 养殖户 | farmer | 123456 |
| 养殖户 | farmer1 ~ farmer4 | 123456 |

> 首次登录建议进入“个人中心”修改密码。

---

## 7. 常用命令

```bash
# 后端依赖安装
pip install -r requirements.txt

# 生成数据库迁移文件 / 执行迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 启动后端（开发）
python manage.py runserver 0.0.0.0:8000

# 启动后端（生产建议：ASGI + WebSocket）
daphne -b 0.0.0.0 -p 8000 breeding_system.asgi:application

# Django 配置自检
python manage.py check

# 前端依赖安装 / 启动 / 构建
cd frontend
npm install
npm run dev
npm run build
```

---

## 8. 常见问题（FAQ）

**Q1：启动后端报 `ModuleNotFoundError: No module named 'django'`**
未安装依赖，执行 `pip install -r requirements.txt`；若使用虚拟环境，先激活虚拟环境。

**Q2：后端连接数据库报 `Access denied for user 'root'@'localhost'`**
`.env` 中的 `DB_PASSWORD` 与你本机 MySQL 密码不一致，修改后重启后端。若 MySQL 账号不是 root，同步修改 `DB_USER`。

**Q3：导入 SQL 后中文乱码**
建库时务必使用 `utf8mb4` / `utf8mb4_unicode_ci`；导入时保持文件编码为 UTF-8。

**Q4：前端页面能打开但接口 404 / 数据加载失败**
前端开发服务器已配置代理：`/api`、`/media` 会转发到 `http://127.0.0.1:8000`。请确认后端已在 8000 端口运行。

**Q5：WebSocket 未连接 / 列表不自动刷新**
前端会自动连接 `ws://localhost:8000/ws/refresh/`（开发环境固定转发到 8000）。若后端未启动或端口不同，前端会以约 3 秒轮询兜底，不影响使用。

**Q6：端口被占用**
后端改端口：`python manage.py runserver 0.0.0.0:8001`，同时修改 `frontend/vite.config.ts` 中代理目标；前端改端口：`npm run dev -- --port 5174`。

**Q7：`pandas` / `numpy` 安装失败（Windows）**
建议使用 Python 3.12 并确保 pip 为最新：`python -m pip install --upgrade pip`，再安装 requirements。

**Q8：溯源二维码打开后地址是本机 IP**
本地开发默认生成 `http://本机局域网IP:5173/public/trace/溯源码`；部署后可在 `.env` 中设置 `TRACE_PUBLIC_BASE_URL=https://你的域名` 重新生成二维码。

---

## 9. 部署与安全提示

如需部署到服务器，请至少完成：

1. `.env` 中设置 `DJANGO_DEBUG=False`、`DJANGO_ALLOWED_HOSTS=你的域名或IP`；
2. 生成并设置强随机 `DJANGO_SECRET_KEY`；
3. 数据库账号使用独立低权限账号，不要使用 root；
4. 使用 `daphne`（或 gunicorn+uvicorn）配合 Nginx 反向代理静态文件与 `/media/`；
5. 多进程部署时，将 `CHANNEL_LAYERS` 从内存后端改为 Redis；
6. 设置 `TRACE_PUBLIC_BASE_URL` 指向公网前端地址。

---