#!/usr/bin/env python3
"""
代码评审工具 - 主程序入口
"""
import os
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QFont, QIcon
from qfluentwidgets import FluentTranslator, setTheme, Theme
from main_window import MainWindow
from login_dialog import LoginDialog
from backend_client import BackendClient


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用退出时的清理行为
    app.setQuitOnLastWindowClosed(True)

    # 设置Fluent主题
    setTheme(Theme.AUTO)

    # 安装Fluent内置翻译（可选）
    translator = FluentTranslator()
    app.installTranslator(translator)

    # 设置应用程序信息
    app.setApplicationName('挑战性综合项目代码评审工具')
    app.setOrganizationName('CodeReview')

    # 设置默认字体
    font = QFont()
    font.setPointSize(14)
    app.setFont(font)
    
    # 设置应用图标
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # 创建后端客户端
    backend_client = BackendClient()
    
    # 显示登录对话框
    login_dialog = LoginDialog(backend_client)
    if os.path.exists(icon_path):
        login_dialog.setWindowIcon(QIcon(icon_path))
    
    # 如果用户取消登录，退出程序
    if login_dialog.exec_() != LoginDialog.Accepted:
        QMessageBox.information(None, '提示', '您已取消登录，程序将退出')
        return 0
    
    # 验证登录状态
    if not backend_client.is_authenticated():
        QMessageBox.warning(None, '警告', '登录验证失败，程序将退出')
        return 0
    
    # 创建并显示主窗口（传入backend_client）
    window = MainWindow(backend_client=backend_client)
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
    window.show()
    
    # 运行应用程序事件循环
    exit_code = app.exec_()
    
    # 确保所有窗口关闭
    app.closeAllWindows()
    
    # 删除应用对象
    del window
    del app
    
    return exit_code

if __name__ == '__main__':
    sys.exit(main())
