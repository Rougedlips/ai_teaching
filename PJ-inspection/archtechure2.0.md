# 评审系统架构升级方案（Architecture 2.0）

## 一、总体架构

1. **三层结构**
   - **客户端（Client）**：保留现有 PyQt 客户端，扩展为教师与学生两种界面模式。
   - **API 服务器（Server）**：新增基于 FastAPI 或 Django REST Framework 的后端服务，提供评审发起、结果查询、权限控制等 RESTful API。
   - **数据库层（Database）**：采用 PostgreSQL/MySQL（生产推荐）或 SQLite（开发阶段）存储用户、评审记录、作业信息等数据。

2. **部署形态**
   - **开发期**：客户端直接调用本地运行的服务器 API；服务器与数据库可部署在同一台开发机器上。
   - **生产期**：服务器与数据库部署至云主机或校园内网服务器，客户端通过 HTTPS 访问；可按需增加对象存储、任务队列等组件。

## 二、后端服务设计

1. **技术栈选择**
   - 框架：FastAPI（轻量、异步友好）或 Django + DRF（内置后台、权限体系）。
   - ORM：SQLAlchemy（配合 FastAPI）或 Django ORM。
   - 身份认证：JWT（跨客户端更友好）或 Django Session + Token（若采用 DRF）。
   - 任务调度（可选）：Celery/RQ + Redis，用于异步调用外部大模型评审任务。

2. **核心数据模型（示例字段）**
   - `User`：`id`, `username`, `password_hash`, `role`（`teacher`/`student`）, `email`
   - `Course`（可选）：课程维度归属。
   - `Assignment`：`id`, `course_id`, `title`, `description`, `deadline`
   - `Submission`：`id`, `assignment_id`, `student_id`, `archive_path`, `status`, `submitted_at`
   - `Review`：`id`, `submission_id`, `reviewer_id`, `score`, `feedback`, `raw_response`, `created_at`
   - `ReviewIssue`：细分错误/警告/风格项，关联 `review_id`
   - `Notification`（可选）：消息提醒记录。

3. **API 设计示例**
   - 认证类：`POST /auth/login`（获取 JWT）、`POST /auth/logout`。
   - 学生侧：`GET /assignments`、`POST /submissions`、`GET /submissions/{id}/reviews`。
   - 教师侧：`POST /assignments`、`PATCH /assignments/{id}`、`GET /submissions?assignment_id=`、`POST /reviews`。
   - 公共查询：`GET /reviews/{id}`、`GET /review-history?submission_id=`。

4. **权限控制**
   - 基于角色与资源所有权校验（学生仅能访问自己的提交，教师可访问所属课程的提交）。
   - FastAPI 通过 `Depends` + 自定义装饰器；Django 使用权限 mixin 或自定义权限类。

5. **外部大模型调用流程**
   - 由服务器统一调度：接收学生提交后触发异步任务调用现有评审模型，生成评审结果入库。
   - 客户端通过轮询、长轮询或服务端推送获取评审结果更新。

## 三、客户端改造

1. **登录与角色识别**
   - 启动时新增登录窗口，向服务器获取 JWT；客户端本地保存 token 并在后续请求中附带。
   - 登录成功后根据 `role` 切换界面：
     - 学生：展示作业列表、提交记录、评审结果。
     - 教师：提供作业管理、学生提交列表、人工复核入口。

2. **API 接入层**
   - 抽象 `ApiClient`：封装 `login`, `list_assignments`, `upload_submission`, `fetch_review` 等方法，统一处理 token、错误提示与重试。
   - 评审流程：上传代码压缩包 → 返回任务 ID → 轮询 `GET /reviews` 或推送方式，驱动 UI 更新。

3. **界面模块调整**
   - 复用现有评审结果组件，将数据源切换为服务器返回的 JSON。
   - 新增“提交作业”文件选择窗口与进度反馈。
   - 教师端扩展“布置作业”“查看所有学生评审历史”界面及交互。

## 四、迁移路径建议

1. **阶段 1：后端雏形**
   - 搭建最小可用 API：用户管理 + 作业 + 评审结果 CRUD。
   - 使用脚本或 Postman 测试接口，确保数据库 schema 正常。

2. **阶段 2：客户端对接**
   - 在 PyQt 客户端中首先接入登录、评审历史查询。
   - 渐进式将本地文件操作替换为服务器 API（上传、下载、查询）。

3. **阶段 3：异步评审任务**
   - 引入 Celery/RQ 管理大模型调用队列，持久化任务状态。
   - 教师端提供任务监控、重试入口。

4. **阶段 4：部署与优化**
   - 部署后端至云服务器（Gunicorn/Uvicorn + Nginx）。
   - 配置 HTTPS、安全策略、备份与日志。
   - 按需引入消息通知、成绩统计、图表等高级特性。

## 五、开发与运维要点

- **配置管理**：采用 `.env` 或环境变量管理数据库、模型 API Key 等敏感信息。
- **日志与监控**：接入结构化日志、Sentry/Prometheus，记录评审调用情况与异常。
- **文件存储**：学生提交可存储于对象存储（MinIO/S3）或本地卷，数据库保存存储路径与元数据。
- **安全性**：密码使用 PBKDF2/bcrypt 存储；上传文件需校验类型、大小并在隔离目录解压。
- **文档与测试**：使用 OpenAPI 自动文档；编写客户端与后端集成测试，保证接口兼容性。

---

此文档可作为将本地评审工具扩展为教师/学生分角色、具备服务器与数据库的 C/S 架构应用的实施蓝图。