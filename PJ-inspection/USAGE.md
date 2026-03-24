# 使用指南

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行程序

```bash
python main.py
```

或使用启动脚本（macOS/Linux）：
```bash
chmod +x run.sh
./run.sh
```

## 详细使用说明

### 第一步：配置API

首次使用需要先配置大模型API：

1. 点击顶部工具栏的 `⚙️ 设置` 按钮
2. 填写以下信息：
   - **API地址**：DeepSeek Chat Completions 接口
     - 推荐值：`https://api.deepseek.com/v1/chat/completions`
   - **API密钥**：在 [DeepSeek 控制台](https://platform.deepseek.com/api_keys) 创建的密钥
   - **模型名称**：如 `deepseek-chat` 或 `deepseek-reasoner`
   - **提示词模板**：自定义评审提示词（保留默认即可）
3. 点击 `保存` 按钮

**注意**：提示词模板中必须包含以下占位符：
- `{file_structure}` - 文件结构
- `{code_content}` - 代码内容

### 第二步：选择项目文件夹

1. 点击工具栏的 `📁 打开文件夹` 按钮
2. 选择要评审的项目目录
3. 文件树会自动加载并显示在左侧

### 第三步：浏览文件

- 在左侧目录树中点击任意文件
- 文件内容会显示在中间的预览区域
- 支持的代码文件会被自动识别

### 第四步：开始评审

1. 确保已选择项目文件夹
2. 点击右上方的 `🤖 开始评审` 按钮
3. 程序会自动：
   - 扫描项目中的所有代码文件
   - 生成文件结构树
   - 调用大模型API进行评审
   - 显示评审结果
   - 保存评审记录到本地

### 第五步：查看历史记录

- 底部显示所有评审历史
- 点击任意历史记录可查看评审结果
- 历史记录以Markdown格式保存在 `reviews/` 目录

## 支持的文件类型

程序会自动识别以下代码文件：

- **Python**: `.py`
- **JavaScript/TypeScript**: `.js`, `.jsx`, `.ts`, `.tsx`
- **Java**: `.java`
- **C/C++**: `.c`, `.cpp`, `.h`
- **C#**: `.cs`
- **Go**: `.go`
- **Rust**: `.rs`
- **PHP**: `.php`
- **Ruby**: `.rb`
- **Swift**: `.swift`
- **Kotlin**: `.kt`
- **Web**: `.html`, `.css`, `.scss`, `.vue`
- **配置文件**: `.json`, `.yaml`, `.yml`, `.xml`
- **其他**: `.md`, `.txt`, `.sh`, `.sql` 等

## 自动忽略的目录

以下目录会被自动忽略，不会参与评审：

- `__pycache__`, `node_modules`
- `.git`, `.venv`, `venv`
- `build`, `dist`
- `.idea`, `.vscode`
- 所有以 `.` 开头的隐藏文件夹

## 配置文件

- **config.json**: 存储API配置和提示词模板
- **reviews/**: 存储所有评审历史记录
- **reviews/index.json**: 评审记录索引

## API配置示例

### DeepSeek API

```
API地址: https://api.deepseek.com/v1/chat/completions
模型名称: deepseek-chat
API密钥: ds-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> 如果使用 `deepseek-reasoner` 模型，请确认账号已开通对应权限，该模型会在响应中包含 reasoning 内容，程序会自动合并输出。

## 提示词自定义

你可以在设置中自定义提示词，例如：

```
请作为资深代码评审专家，对以下项目进行全面评审：

## 评审重点
1. 代码架构设计
2. 代码质量和规范
3. 性能优化建议
4. 安全漏洞检测
5. 最佳实践建议

## 项目结构
{file_structure}

## 代码内容
{code_content}

请提供详细的评审报告，包括问题描述、严重程度、修改建议等。
```

## 常见问题

### Q: API调用失败怎么办？
A: 检查以下几点：
1. API地址是否为 `https://api.deepseek.com`（可选带 `/v1/chat/completions`）
2. API密钥是否来自 DeepSeek 控制台
3. 模型名称是否正确（如 `deepseek-chat`、`deepseek-reasoner`）
4. 网络连接是否正常
5. API配额是否充足

### Q: 评审时间过长？
A: 这取决于：
1. 项目文件数量和大小
2. API响应速度
3. 网络状况

可以尝试：
- 评审较小的项目或单个模块
- 使用更快的API服务
- 调整提示词长度

### Q: 如何导出评审报告？
A: 评审报告自动保存在 `reviews/` 目录下，为Markdown格式，可以：
- 直接用Markdown编辑器打开
- 转换为PDF
- 复制粘贴到文档中

### Q: 可以评审哪些语言的代码？
A: 支持几乎所有主流编程语言，具体取决于：
1. 文件扩展名是否在支持列表中
2. 大模型对该语言的理解能力

## 技术支持

如有问题或建议，欢迎反馈！
