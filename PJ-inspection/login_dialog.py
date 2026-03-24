"""
登录对话框
"""
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QMessageBox,
    QWidget,
    QSpacerItem,
    QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from qfluentwidgets import (
    PrimaryPushButton,
    CardWidget,
    SubtitleLabel
)

from backend_client import BackendClient


class LoginDialog(QDialog):
    def __init__(self, backend_client: BackendClient, parent=None):
        super().__init__(parent)
        self.backend_client = backend_client
        self.is_register_mode = False
        
        self.setWindowTitle('用户登录')
        self.setFixedSize(480, 620)  # 增加高度，确保注册界面完整显示
        self.setModal(True)
        
        self.init_ui()
    
    def init_ui(self):
        """初始化登录/注册界面，使用卡片式布局，统一UI风格"""
        # 整体背景色与主界面保持一致
        self.setStyleSheet(
            """
            QDialog {
                background-color: #F3F4F6;
            }
            QLabel#fieldLabel {
                font-weight: 500;
                margin-bottom: 4px;
                color: #333333;
            }
            QPushButton#linkButton {
                color: #0078D7;
                border: none;
                background: transparent;
            }
            QPushButton#linkButton:hover {
                text-decoration: underline;
            }
            """
        )

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(0)

        root_layout.addStretch()

        # 中间卡片容器
        card = CardWidget(self)
        card.setFixedWidth(380)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)

        # 标题
        title_label = SubtitleLabel('代码评审系统')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('font-size: 22px; font-weight: 600;')
        card_layout.addWidget(title_label)

        # 副标题（根据模式切换文案）
        self.subtitle_label = QLabel('登录您的账号')
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet('color: #666666; font-size: 13px;')
        card_layout.addWidget(self.subtitle_label)

        # 用户名
        username_container = QWidget()
        username_layout = QVBoxLayout(username_container)
        username_layout.setContentsMargins(0, 0, 0, 0)
        username_layout.setSpacing(6)

        username_label = QLabel('用户名')
        username_label.setObjectName('fieldLabel')
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText('请输入用户名')
        self.username_edit.setFixedHeight(40)
        self.username_edit.setStyleSheet(
            'QLineEdit { padding: 8px; border: 1px solid #DDDDDD; border-radius: 8px; background: #FFFFFF; }'
            'QLineEdit:focus { border-color: #0078D7; }'
        )
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_edit)
        card_layout.addWidget(username_container)

        # 邮箱（仅注册时显示）
        self.email_container = QWidget()
        email_layout = QVBoxLayout(self.email_container)
        email_layout.setContentsMargins(0, 0, 0, 0)
        email_layout.setSpacing(6)

        self.email_label = QLabel('邮箱')
        self.email_label.setObjectName('fieldLabel')
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText('请输入邮箱')
        self.email_edit.setFixedHeight(40)
        self.email_edit.setStyleSheet(
            'QLineEdit { padding: 8px; border: 1px solid #DDDDDD; border-radius: 8px; background: #FFFFFF; }'
            'QLineEdit:focus { border-color: #0078D7; }'
        )
        email_layout.addWidget(self.email_label)
        email_layout.addWidget(self.email_edit)
        self.email_container.setVisible(False)
        card_layout.addWidget(self.email_container)

        # 用户角色（仅注册时显示）
        self.role_container = QWidget()
        role_layout = QVBoxLayout(self.role_container)
        role_layout.setContentsMargins(0, 0, 0, 0)
        role_layout.setSpacing(6)

        self.role_label = QLabel('用户角色')
        self.role_label.setObjectName('fieldLabel')
        self.role_combo = QComboBox()
        self.role_combo.addItems(['student', 'teacher'])
        self.role_combo.setFixedHeight(40)
        self.role_combo.setStyleSheet(
            'QComboBox { padding: 8px; border: 1px solid #DDDDDD; border-radius: 8px; background: #FFFFFF; }'
            'QComboBox::drop-down { width: 24px; border: none; }'
        )
        role_layout.addWidget(self.role_label)
        role_layout.addWidget(self.role_combo)
        self.role_container.setVisible(False)
        card_layout.addWidget(self.role_container)

        # 密码
        password_container = QWidget()
        password_layout = QVBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(6)

        password_label = QLabel('密码')
        password_label.setObjectName('fieldLabel')
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText('请输入密码')
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setFixedHeight(40)
        self.password_edit.setStyleSheet(
            'QLineEdit { padding: 8px; border: 1px solid #DDDDDD; border-radius: 8px; background: #FFFFFF; }'
            'QLineEdit:focus { border-color: #0078D7; }'
        )
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit)
        card_layout.addWidget(password_container)

        # 登录/注册按钮
        self.login_btn = PrimaryPushButton('登录')
        self.login_btn.setFixedHeight(40)
        self.login_btn.clicked.connect(self.on_login)
        card_layout.addWidget(self.login_btn)

        # 底部切换登录/注册
        switch_layout = QHBoxLayout()
        switch_layout.setContentsMargins(0, 0, 0, 0)
        switch_layout.setSpacing(4)
        switch_layout.setAlignment(Qt.AlignCenter)

        self.switch_label = QLabel('没有账号？')
        self.switch_btn = QPushButton('立即注册')
        self.switch_btn.setObjectName('linkButton')
        self.switch_btn.clicked.connect(self.switch_mode)

        switch_layout.addWidget(self.switch_label)
        switch_layout.addWidget(self.switch_btn)
        card_layout.addLayout(switch_layout)

        card_layout.addStretch()

        root_layout.addWidget(card, alignment=Qt.AlignCenter)
        root_layout.addStretch()
    
    def switch_mode(self):
        """切换登录/注册模式"""
        self.is_register_mode = not self.is_register_mode

        if self.is_register_mode:
            # 切换到注册模式
            self.setWindowTitle('用户注册')
            self.subtitle_label.setText('创建一个新账号')
            self.login_btn.setText('注册')
            self.switch_label.setText('已有账号？')
            self.switch_btn.setText('立即登录')
            self.email_container.setVisible(True)
            self.role_container.setVisible(True)
        else:
            # 切换回登录模式
            self.setWindowTitle('用户登录')
            self.subtitle_label.setText('登录您的账号')
            self.login_btn.setText('登录')
            self.switch_label.setText('没有账号？')
            self.switch_btn.setText('立即注册')
            self.email_container.setVisible(False)
            self.role_container.setVisible(False)

        # 刷新界面
        self.layout().activate()
        self.update()
        self.repaint()
    
    def on_login(self):
        """处理登录/注册"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, '警告', '用户名和密码不能为空')
            return
        
        self.login_btn.setEnabled(False)
        self.login_btn.setText('处理中...')
        
        try:
            if self.is_register_mode:
                # 注册逻辑
                email = self.email_edit.text().strip()
                role = self.role_combo.currentText()
                
                if not email:
                    QMessageBox.warning(self, '警告', '邮箱不能为空')
                    return
                
                try:
                    result = self.backend_client.register(username, email, password, role)
                    QMessageBox.information(self, '成功', '注册成功，请登录')
                    self.switch_mode()  # 切回登录模式
                except Exception as e:
                    error_msg = str(e)
                    QMessageBox.critical(self, '注册失败', 
                        f'注册失败，请检查服务器是否运行。\n\n'
                        f'详细信息：{error_msg}')
                    return
            else:
                # 登录逻辑
                result = self.backend_client.login(username, password)
                QMessageBox.information(self, '成功', '登录成功')
                self.accept()
                
        except Exception as exc:
            QMessageBox.critical(self, '错误', str(exc))
        finally:
            self.login_btn.setEnabled(True)
            if self.is_register_mode:
                self.login_btn.setText('注册')
            else:
                self.login_btn.setText('登录')