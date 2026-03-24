#!/usr/bin/env python3
"""
测试界面结构
"""
import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow

def test_interface():
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # 检查是否有两个界面
    print("✓ 主窗口创建成功")
    
    # 检查工作台界面
    if hasattr(window, 'workspace_widget'):
        print("✓ 工作台界面已创建")
        print(f"  - 对象名称: {window.workspace_widget.objectName()}")
    
    # 检查评审界面
    if hasattr(window, 'review_widget'):
        print("✓ 评审界面已创建")
        print(f"  - 对象名称: {window.review_widget.objectName()}")
    
    # 检查导航项
    nav_items = []
    for i in range(window.navigationInterface.count()):
        item = window.navigationInterface.widget(i)
        if item:
            nav_items.append(item.objectName() if hasattr(item, 'objectName') else str(item))
    
    print(f"✓ 导航栏项目数量: {window.navigationInterface.count()}")
    
    # 检查当前选中的界面
    current_item = window.navigationInterface.currentItem()
    if current_item:
        print(f"✓ 当前选中界面: {current_item}")
    
    print("\n界面结构测试完成！")
    print("程序将在3秒后显示窗口...")
    
    # 显示窗口
    window.show()
    
    # 3秒后自动关闭
    from PyQt5.QtCore import QTimer
    QTimer.singleShot(3000, app.quit)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    test_interface()
