#!/usr/bin/env python3
"""
测试程序关闭功能
"""
import sys
import time
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from backend_client import BackendClient
from main_window import MainWindow

def test_normal_close():
    """测试正常关闭"""
    print("=" * 60)
    print("测试1: 正常关闭窗口")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # 模拟登录
    backend_client = BackendClient()
    backend_client.token = "test_token"
    backend_client.user_info = {
        "username": "测试用户",
        "role": "teacher",
        "id": 1
    }
    
    # 创建主窗口
    window = MainWindow(backend_client)
    window.show()
    
    print("✅ 主窗口已创建")
    print("⏱️  3秒后自动关闭窗口...")
    
    # 3秒后自动关闭
    QTimer.singleShot(3000, window.close)
    
    # 5秒后强制退出（如果窗口没正确关闭）
    QTimer.singleShot(5000, lambda: (
        print("❌ 超时！窗口未正确关闭"),
        app.quit()
    ))
    
    exit_code = app.exec_()
    
    print("✅ 应用程序已退出")
    print(f"退出代码: {exit_code}")
    print("=" * 60)
    
    return exit_code

def test_close_with_thread():
    """测试有线程运行时关闭"""
    print("=" * 60)
    print("测试2: 有后台线程时关闭窗口")
    print("=" * 60)
    print("⚠️  注意: 此测试需要实际的API调用，可能会超时")
    print("=" * 60)
    
    # TODO: 实现模拟线程运行的测试
    print("跳过此测试（需要后端支持）")

if __name__ == '__main__':
    print("\n程序关闭功能测试\n")
    
    # 测试1: 正常关闭
    test_normal_close()
    
    print("\n✅ 所有测试完成")
    print("如果程序能正确退出，说明修复成功！\n")
