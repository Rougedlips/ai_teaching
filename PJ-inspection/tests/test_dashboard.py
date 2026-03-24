#!/usr/bin/env python3
"""
测试教师仪表盘功能
"""
import sys
from PyQt5.QtWidgets import QApplication, QDialog
from backend_client import BackendClient
from main_window import MainWindow

def test_teacher_dashboard():
    """测试教师仪表盘"""
    app = QApplication(sys.argv)
    
    # 创建模拟的教师账号客户端
    backend_client = BackendClient()
    
    # 模拟登录（需要实际的后端服务）
    # 这里我们手动设置用户信息来测试UI
    backend_client.token = "test_token"
    backend_client.user_info = {
        "username": "王老师",
        "email": "teacher@example.com",
        "role": "teacher",
        "id": 1
    }
    
    # 创建主窗口
    window = MainWindow(backend_client)
    window.show()
    
    print("=" * 60)
    print("教师仪表盘测试")
    print("=" * 60)
    print("✅ 主窗口已创建")
    print("✅ 用户角色: 教师")
    print("✅ 仪表盘界面已加载")
    print()
    print("请在GUI窗口中查看以下功能：")
    print("  1. 顶部课程选择下拉框")
    print("  2. 四个统计卡片（学生总数、作业总数、待批改、平均分）")
    print("  3. 最近提交列表")
    print("  4. 成绩统计面板")
    print("=" * 60)
    
    sys.exit(app.exec_())

def test_student_workspace():
    """测试学生工作台"""
    app = QApplication(sys.argv)
    
    # 创建模拟的学生账号客户端
    backend_client = BackendClient()
    backend_client.token = "test_token"
    backend_client.user_info = {
        "username": "张三",
        "email": "student@example.com",
        "role": "student",
        "id": 2
    }
    
    # 创建主窗口
    window = MainWindow(backend_client)
    window.show()
    
    print("=" * 60)
    print("学生工作台测试")
    print("=" * 60)
    print("✅ 主窗口已创建")
    print("✅ 用户角色: 学生")
    print("✅ 默认工作台界面已加载")
    print()
    print("学生账号应该看到默认的欢迎界面")
    print("=" * 60)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'student':
        test_student_workspace()
    else:
        test_teacher_dashboard()
