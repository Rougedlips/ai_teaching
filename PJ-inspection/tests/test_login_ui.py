#!/usr/bin/env python3
"""
测试登录界面（无需后端）
"""
import sys
from PyQt5.QtWidgets import QApplication
from login_dialog import LoginDialog
from backend_client import BackendClient


class MockBackendClient(BackendClient):
    """模拟后端客户端用于测试"""
    def __init__(self):
        super().__init__()
        self._mock_users = {
            "admin": {"password": "admin123", "email": "admin@test.com", "role": "teacher"},
            "student1": {"password": "student123", "email": "student@test.com", "role": "student"}
        }
    
    def login(self, username: str, password: str):
        """模拟登录"""
        print(f"[测试] 尝试登录: {username}")
        
        if username in self._mock_users:
            if self._mock_users[username]["password"] == password:
                self.token = "mock_token_12345"
                self.current_user = {
                    "username": username,
                    "email": self._mock_users[username]["email"],
                    "role": self._mock_users[username]["role"]
                }
                print(f"[测试] 登录成功: {username}")
                return {"access_token": self.token, "token_type": "bearer"}
            else:
                raise Exception("密码错误")
        else:
            raise Exception("用户不存在")
    
    def register(self, username: str, email: str, password: str, role: str = "student"):
        """模拟注册"""
        print(f"[测试] 尝试注册: {username} ({email})")
        
        if username in self._mock_users:
            raise Exception("用户名已存在")
        
        # 添加到模拟用户列表
        self._mock_users[username] = {
            "password": password,
            "email": email,
            "role": role
        }
        
        print(f"[测试] 注册成功: {username}")
        return {
            "id": f"mock_id_{len(self._mock_users)}",
            "username": username,
            "email": email,
            "role": role
        }


def main():
    app = QApplication(sys.argv)
    
    # 创建模拟后端客户端
    backend_client = MockBackendClient()
    
    print("="*50)
    print("登录界面测试（使用模拟后端）")
    print("="*50)
    print("\n测试账号:")
    print("  用户名: admin    密码: admin123    (教师)")
    print("  用户名: student1 密码: student123 (学生)")
    print("\n或者点击'立即注册'创建新账号")
    print("="*50)
    print()
    
    # 显示登录对话框
    dialog = LoginDialog(backend_client)
    
    if dialog.exec_() == LoginDialog.Accepted:
        print("\n✅ 登录成功！")
        print(f"Token: {backend_client.token}")
        
        user_info = backend_client.get_user_info()
        print(f"用户名: {user_info['username']}")
        print(f"邮箱: {user_info['email']}")
        print(f"角色: {user_info['role']}")
    else:
        print("\n❌ 用户取消登录")
    
    sys.exit(0)


if __name__ == '__main__':
    main()
