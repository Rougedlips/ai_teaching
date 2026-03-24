#!/usr/bin/env python3
"""
测试登录流程
这个脚本用于测试登录对话框和后端客户端的集成
"""
import sys
from PyQt5.QtWidgets import QApplication
from login_dialog import LoginDialog
from backend_client import BackendClient


def main():
    """测试主函数"""
    app = QApplication(sys.argv)
    
    # 创建后端客户端
    backend_client = BackendClient()
    
    # 创建并显示登录对话框
    login_dialog = LoginDialog(backend_client)
    
    print("显示登录对话框...")
    result = login_dialog.exec_()
    
    if result == LoginDialog.Accepted:
        print("✅ 登录成功！")
        print(f"认证状态: {backend_client.is_authenticated()}")
        
        if backend_client.is_authenticated():
            try:
                user_info = backend_client.get_user_info()
                if user_info:
                    print(f"用户信息: {user_info}")
                    print(f"用户名: {user_info.get('username', '未知')}")
                    print(f"角色: {user_info.get('role', '未知')}")
                else:
                    print("⚠️ 无法获取用户信息")
            except Exception as e:
                print(f"❌ 获取用户信息失败: {e}")
    else:
        print("❌ 用户取消登录")
    
    sys.exit(0)


if __name__ == '__main__':
    main()
