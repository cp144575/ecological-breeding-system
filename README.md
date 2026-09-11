# 生态养殖系统

> 前后端分离的生态养殖管理系统，覆盖养殖户实名认证、养殖业务数据采集、生产管理、统计分析、批次溯源和多角色协同。

- 后端：Python 3.12 + Django 5.2 + Django REST Framework + MySQL + WebSocket
- 前端：Vue 3 + TypeScript + Vite + Element Plus + ECharts
- 功能与接口说明见 [`系统功能描述.md`](系统功能描述.md)

---

## 目录

1. [项目简介](#1-项目简介)
2. [核心功能](#2-核心功能)
3. [技术栈](#3-技术栈)
4. [项目结构](#4-项目结构)
5. [环境要求](#5-环境要求)
6. [快速开始](#6-快速开始)
7. [角色与权限](#7-角色与权限)
8. [常用命令](#8-常用命令)
9. [部署与安全](#9-部署与安全)
10. [安全维护](#10-安全维护)

---

## 1. 项目简介

系统用于养殖业务的数字化管理，主要角色包括管理员、养殖户和兽医，同时提供无需登录的公众溯源查询能力。

核心业务流程：

```text
养殖户注册
   ↓
实名认证
   ↓
养殖区域与批次管理
   ↓
投喂 / 防疫 / 疾病数据采集
   ↓
批次出栏
   ↓
生成溯源码与二维码
   ↓
公众扫码查询
```

管理员负责全局监管、账户管理、实名认证审核、疾病协同和统计分析；兽医负责处理分配的疾病上报。

---

## 2. 核心功能

- 多角色 RBAC 权限控制
- 养殖户实名认证及审核流程
- 养殖区域、牲畜分类和批次管理
- 饲料库存与投喂记录联动
- 数据库事务与行级锁保证关键库存操作一致性
- 疾病上报、分配、处理及批次数量联动
- 疫苗接种记录管理
- 批次溯源码与二维码自动生成
- 身份证等敏感信息加密存储并按角色脱敏展示
- JWT 登录与 Token 自动刷新
- WebSocket 实时刷新与断线轮询兜底
- 管理员及养殖户统计看板
- 公众匿名溯源查询

---

## 3. 技术栈

| 层次 | 技术 |
| --- | --- |
| 后端运行环境 | Python 3.10 ~ 3.12，推荐 Python 3.12 |
| Web 框架 | Django 5.2 |
| REST API | Django REST Framework |
| 认证 | djangorestframework-simplejwt |
| 数据库 | MySQL 8.0 + PyMySQL |
| 实时通信 | Django Channels + Daphne |
| 图片处理 | Pillow |
| 二维码 | qrcode |
| 数据分析 | Pandas + NumPy |
| 前端 | Vue 3 + TypeScript |
| 构建工具 | Vite 7 |
| UI | Element Plus |
| 状态管理 | Pinia |
| HTTP | Axios |
| 图表 | ECharts |

完整依赖以 `requirements.txt` 和 `frontend/package.json` 为准。

---

## 4. 项目结构

```text
DjangoProject/
├── manage.py
├── requirements.txt
├── .env.example
├── database/
│   └── ecological_breeding_system.sql
├── breeding_system/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── core/
│   ├── users/
│   ├── livestock/
│   ├── production/
│   ├── stats/
│   └── traceability_app/
├── media/
└── frontend/
    ├── package.json
    ├── vite.config.ts
    └── src/
```

---

## 5. 环境要求

| 软件 | 要求 | 推荐 |
| --- | --- | --- |
| Python | 3.10 ~ 3.12 | 3.12 |
| Node.js | 18+ | 20 LTS |
| npm | 随 Node 安装 | 10.x |
| MySQL | 8.0+ | 8.0 |
| Git | 可选 | 最新稳定版 |

---

## 6. 快速开始

### 6.1 获取代码

```bash
git clone https://github.com/cp144575/ecological-breeding-system.git
cd ecological-breeding-system
```

### 6.2 创建数据库

```sql
CREATE DATABASE IF NOT EXISTS ecological_breeding_system
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

导入数据库备份：

```bash
mysql -uroot -p ecological_breeding_system < database\ecological_breeding_system.sql
```

### 6.3 配置环境变量

复制 `.env.example`：

```bash
copy .env.example .env
```

至少配置：

```text
DJANGO_SECRET_KEY=请设置随机密钥
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=ecological_breeding_system
DB_USER=root
DB_PASSWORD=你的MySQL密码
DB_HOST=127.0.0.1
DB_PORT=3306
TRACE_PUBLIC_BASE_URL=
```

生产环境必须关闭 DEBUG，并使用明确的允许主机列表。

### 6.4 启动后端

Windows：

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py check
python manage.py runserver 0.0.0.0:8000
```

macOS / Linux：

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py check
python manage.py runserver 0.0.0.0:8000
```

生产环境推荐使用 ASGI：

```bash
daphne -b 0.0.0.0 -p 8000 breeding_system.asgi:application
```

### 6.5 启动前端

```bash
cd frontend
npm install
npm run dev
```

默认地址：

- 前端：`http://localhost:5173/`
- 后端：`http://localhost:8000/`
- Django Admin：`http://localhost:8000/admin/`
- WebSocket：`ws://localhost:8000/ws/refresh/`

### 6.6 数据库迁移

已有数据库备份时无需重复初始化表结构。开发环境需要执行迁移时：

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 7. 角色与权限

| 角色 | 权限范围 |
| --- | --- |
| 管理员 | 用户、认证、疾病、溯源、统计等全局管理 |
| 养殖户 | 自己的养殖区域、批次、生产记录和统计数据 |
| 兽医 | 查看和处理分配给自己的疾病上报 |
| 公众 | 通过溯源码匿名查询公开溯源信息 |

关键业务写操作会结合登录状态、角色和养殖户认证状态进行权限校验。

---

## 8. 常用命令

```bash
# Django 配置检查
python manage.py check

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建管理员
python manage.py createsuperuser

# 后端开发服务
python manage.py runserver 0.0.0.0:8000

# ASGI / WebSocket
daphne -b 0.0.0.0 -p 8000 breeding_system.asgi:application

# 前端开发
cd frontend
npm install
npm run dev

# 前端生产构建
npm run build
```

---

## 9. 部署与安全

生产环境至少完成以下配置：

1. `DJANGO_DEBUG=False`。
2. `DJANGO_ALLOWED_HOSTS` 设置为实际域名或 IP，不使用通配符。
3. `DJANGO_SECRET_KEY` 使用随机、高强度且独立的生产密钥。
4. 数据库使用独立低权限账号，不使用 root 运行应用。
5. CORS 仅允许实际前端来源。
6. 使用 Nginx 等反向代理，并启用 HTTPS。
7. 多进程部署时将 Channels 的 Channel Layer 配置为 Redis 等共享后端。
8. `.env`、数据库密码、Token 和其他凭据不得提交到 Git。
9. 用户上传文件需要限制类型、大小，并通过独立媒体路径提供访问。
10. 服务端错误响应不向客户端返回内部异常、文件路径或 traceback。

---

## 10. 安全维护

项目近期已完成以下安全维护：

- Django 已升级到 5.2 系列安全版本。
- Pillow、Daphne、Requests、python-dotenv 已完成安全依赖更新。
- 前端依赖已完成一轮 Dependabot 安全更新。
- 头像上传异常不再直接向客户端返回内部异常信息。
- CodeQL Python 与 JavaScript/TypeScript 检查已通过相关修复。
- Django REST Framework 的安全告警正在通过独立依赖更新处理，最终版本以 `requirements.txt` 和 GitHub Security 页面为��。

> 依赖版本以仓库文件和 GitHub Security 页面为最终准据。

---

## 11. 测试账号

项目数据库文件 `database/ecological_breeding_system.sql` 已包含可用于本地测试的账号数据。

**所有测试账号的密码均为 `123456`。**

| 角色 | 用户名 | 密码 | 说明 |
| --- | --- | --- | --- |
| 管理员 | `admin` | `123456` | 管理员账号，用于测试系统管理功能 |
| 兽医 | `vet` | `123456` | 兽医账号，用于测试疾病处理等功能 |
| 养殖户 | `farmer` | `123456` | 养殖户账号，用于测试未实名认证状态下的功能 |
| 养殖户 | `farmer1` | `123456` | 已实名认证养殖户，用于测试养殖业务功能 |
| 养殖户 | `farmer2` | `123456` | 已实名认证养殖户，用于测试养殖业务功能 |
| 养殖户 | `farmer3` | `123456` | 养殖户账号，用于测试未实名认证状态下的功能 |
| 养殖户 | `farmer4` | `123456` | 养殖户账号，用于测试未实名认证状态下的功能 |

### 测试建议

- **管理员功能**：使用 `admin / 123456` 登录，测试用户管理、实名认证审核、疾病协同、统计分析等管理员功能。
- **兽医功能**：使用 `vet / 123456` 登录，测试疾病上报查看、处理等兽医功能。
- **养殖户功能**：使用 `farmer1 / 123456` 或 `farmer2 / 123456` 登录，测试已实名认证养殖户的养殖区域、批次、投喂、防疫、疾病和统计等业务功能。
- **实名认证流程**：使用 `farmer / 123456`、`farmer3 / 123456` 或 `farmer4 / 123456`，测试未实名认证养殖户的权限限制及实名认证流程。

### 溯源二维码查询说明

项目中的溯源二维码查询功能依赖本地开发环境提供的后端服务。如果使用手机等其他设备扫描二维码进行溯源查询，**扫描设备必须与运行项目后端服务的电脑处于同一个局域网（LAN）内**，并且后端服务需要监听局域网地址，例如 `0.0.0.0:8000`。

如果手机与运行后端服务的电脑不在同一个局域网，或者二维码中使用的是 `localhost`、`127.0.0.1` 等仅对本机有效的地址，扫码后将无法正常访问溯源页面。
