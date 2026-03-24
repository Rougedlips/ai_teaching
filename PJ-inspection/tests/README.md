# 测试文件说明

本目录包含项目的所有测试脚本和验证工具。

## 📂 文件列表

### 测试数据

#### `test_project/` - 测试项目目录
**用途**: 用于测试项目导入和扫描功能的空目录

#### `test.zip` - 测试压缩包
**用途**: 用于测试压缩包导入和解压功能

---

### 功能测试

#### 1. `test_close.py` - 程序关闭功能测试
**用途**: 测试程序关闭功能是否正常工作

**功能**:
- 测试正常关闭窗口
- 测试有后台线程时关闭
- 验证进程是否完全退出

**运行方法**:
```bash
cd /Users/rougedlips/Desktop/PJ-inspection
python tests/test_close.py
```

**预期结果**:
- 窗口在3秒后自动关闭
- 程序完全退出，无进程残留

---

#### 2. `test_dashboard.py` - 教师仪表盘测试
**用途**: 测试教师仪表盘界面功能

**功能**:
- 测试教师仪表盘UI显示
- 测试学生工作台UI显示
- 验证统计卡片和数据展示

**运行方法**:
```bash
# 测试教师仪表盘
python tests/test_dashboard.py

# 测试学生工作台
python tests/test_dashboard.py student
```

**预期结果**:
- 教师账号显示仪表盘
- 学生账号显示默认工作台
- UI布局正确

---

#### 3. `test_interface.py` - 界面测试
**用途**: 测试主界面的基本功能

**功能**:
- 测试主窗口创建
- 测试界面布局
- 验证UI组件

**运行方法**:
```bash
python tests/test_interface.py
```

---

#### 4. `test_line_numbers.py` - 行号显示测试
**用途**: 测试代码编辑器的行号显示功能

**功能**:
- 测试CodeEditor组件
- 测试行号显示
- 验证代码高亮

**运行方法**:
```bash
python tests/test_line_numbers.py
```

**预期结果**:
- 显示带行号的代码编辑器
- 行号正确对齐
- 支持滚动

---

### 登录功能测试

#### 5. `test_login_flow.py` - 登录流程测试
**用途**: 测试完整的登录流程

**功能**:
- 测试登录对话框显示
- 测试登录成功后主窗口显示
- 验证用户信息获取

**运行方法**:
```bash
python tests/test_login_flow.py
```

**预期结果**:
- 登录对话框正确显示
- 登录成功后显示主窗口
- 用户信息正确显示

---

#### 6. `test_login_ui.py` - 登录界面UI测试
**用途**: 测试登录对话框的UI设计

**功能**:
- 测试登录/注册界面
- 测试表单验证
- 测试UI交互

**运行方法**:
```bash
python tests/test_login_ui.py
```

**预期结果**:
- 登录界面美观
- 注册界面正确显示
- 表单验证有效

---

#### 7. `verify_login_integration.py` - 登录集成验证
**用途**: 验证登录功能的完整集成

**功能**:
- 验证登录流程完整性
- 检查后端API集成
- 测试用户认证

**运行方法**:
```bash
python tests/verify_login_integration.py
```

**预期结果**:
- 登录功能完整
- API集成正确
- 认证流程正常

---

#### 8. `test.py` - 简单测试脚本
**用途**: 基础测试脚本

**运行方法**:
```bash
python tests/test.py
```

---

## 🚀 快速开始

### 运行所有测试
```bash
# 进入项目目录
cd /Users/rougedlips/Desktop/PJ-inspection

# 运行单个测试
python tests/test_dashboard.py
python tests/test_close.py
python tests/test_login_flow.py
```

### 批量运行测试
```bash
# 运行所有测试文件
for test in tests/test_*.py; do
    echo "Running $test..."
    python "$test"
done
```

---

## 📝 测试分类

### UI/界面测试
- `test_dashboard.py` - 仪表盘UI
- `test_interface.py` - 主界面
- `test_line_numbers.py` - 代码编辑器
- `test_login_ui.py` - 登录界面

### 功能测试
- `test_close.py` - 关闭功能
- `test_login_flow.py` - 登录流程
- `verify_login_integration.py` - 登录集成

### 基础测试
- `test.py` - 基础脚本

---

## ⚙️ 测试环境要求

### Python 版本
- Python 3.7+

### 依赖库
```bash
pip install -r ../requirements.txt
```

主要依赖：
- PyQt5
- qfluentwidgets
- requests

### 后端服务
某些测试需要后端服务运行：
- `test_login_flow.py`
- `verify_login_integration.py`

---

## 📊 测试覆盖

| 模块 | 测试文件 | 覆盖率 |
|------|---------|--------|
| 主窗口 | test_interface.py | ✅ |
| 登录功能 | test_login_*.py | ✅ |
| 仪表盘 | test_dashboard.py | ✅ |
| 关闭功能 | test_close.py | ✅ |
| 代码编辑器 | test_line_numbers.py | ✅ |

---

## 🐛 调试提示

### 常见问题

1. **导入错误**
   ```python
   # 确保在项目根目录运行
   cd /Users/rougedlips/Desktop/PJ-inspection
   python tests/test_xxx.py
   ```

2. **GUI无法显示**
   ```bash
   # macOS 可能需要设置环境变量
   export QT_MAC_WANTS_LAYER=1
   ```

3. **后端连接失败**
   ```bash
   # 检查后端服务是否运行
   curl http://localhost:8000/api
   ```

---

## 📌 注意事项

1. **GUI测试**: 需要图形界面环境，无法在纯命令行环境运行
2. **后端依赖**: 部分测试需要后端服务支持
3. **超时设置**: 某些测试有自动超时机制
4. **资源清理**: 测试完成后会自动清理资源

---

## 🎯 最佳实践

1. **测试前**
   - 确保后端服务运行（如需要）
   - 检查依赖库是否安装
   - 确认在项目根目录

2. **测试中**
   - 观察控制台输出
   - 检查UI显示是否正常
   - 注意错误提示

3. **测试后**
   - 检查进程是否完全退出
   - 查看日志文件
   - 验证资源是否清理

---

## 📚 相关文档

- `../CLOSE_FIX.md` - 关闭功能修复说明
- `../DASHBOARD_UPDATE.md` - 仪表盘更新说明
- `../LOGIN_GUIDE.md` - 登录功能指南

---

**更新日期**: 2025年
**版本**: v1.0
**维护者**: 项目开发团队
