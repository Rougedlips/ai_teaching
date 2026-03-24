"""
设置对话框
"""
from PyQt5.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QMessageBox,
    QSizePolicy,
    QScrollArea,
    QFrame,
    QTabWidget,
    QCheckBox
)
from PyQt5.QtCore import Qt
from qfluentwidgets import PrimaryPushButton, PushButton


class SettingsDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self._syncing_provider = False
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('设置')
        self.setMinimumSize(760, 680)

        section_style = (
            'QWidget#sectionCard { '
            'background-color: rgba(255, 255, 255, 0.65);'
            'border-radius: 12px;'
            'border: 1px solid rgba(0, 0, 0, 0.04);'
            '}'
            'QWidget#sectionCard QLabel.sectionTitle { '
            'font-weight: 600;'
            'font-size: 16px;'
            'padding-bottom: 4px;'
            '}'
            'QLabel.sectionHint { '
            'color: #666666;'
            'line-height: 1.5;'
            '}'
            'QLineEdit, QTextEdit { '
            'border: 1px solid rgba(0, 0, 0, 0.08);'
            'border-radius: 8px;'
            'background-color: rgba(255, 255, 255, 0.95);'
            'padding: 10px 12px;'
            'font-size: 14px;'
            '}'
        )
        self.setStyleSheet(section_style)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName('settingsTabWidget')
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setDocumentMode(True)

        self.tab_widget.addTab(self._build_deepseek_tab(), 'DeepSeek API')
        self.tab_widget.addTab(self._build_qwencoder_tab(), 'QwenCoder API')
        self.tab_widget.addTab(self._build_doubao_tab(), 'DoubaoCoder API')
        self.tab_widget.addTab(self._build_prompt_tab(), '提示词')

        layout.addWidget(self.tab_widget)
        layout.addWidget(self._build_button_section())

    def _build_deepseek_tab(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        self.deepseek_checkbox = QCheckBox('使用 DeepSeek 接口进行评审调用')
        self.deepseek_checkbox.setCursor(Qt.PointingHandCursor)
        self.deepseek_checkbox.toggled.connect(self._on_deepseek_checked)
        layout.addWidget(self.deepseek_checkbox)

        description = QLabel('启用后，将通过 DeepSeek Chat Completions 接口发送代码评审请求。')
        description.setWordWrap(True)
        description.setObjectName('sectionHint')
        layout.addWidget(description)

        api_section = QWidget()
        api_section.setObjectName('sectionCard')
        api_layout = QVBoxLayout(api_section)
        api_layout.setContentsMargins(20, 20, 20, 20)
        api_layout.setSpacing(16)

        api_title = QLabel('API 配置')
        api_title.setObjectName('sectionTitle')
        api_layout.addWidget(api_title)

        api_hint = QLabel('请填写 DeepSeek Chat Completions 接口的完整地址和模型信息。')
        api_hint.setWordWrap(True)
        api_hint.setObjectName('sectionHint')
        api_layout.addWidget(api_hint)

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        api_url_label = QLabel('API地址')
        api_url_label.setObjectName('sectionTitle')
        form_layout.addWidget(api_url_label)

        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText('例如: https://api.deepseek.com/v1/chat/completions')
        self.api_url_input.setMinimumWidth(520)
        self.api_url_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addWidget(self.api_url_input)

        api_key_label = QLabel('API密钥')
        api_key_label.setObjectName('sectionTitle')
        form_layout.addWidget(api_key_label)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText('输入 DeepSeek API 密钥')
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setMinimumWidth(520)
        self.api_key_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addWidget(self.api_key_input)

        model_label = QLabel('模型名称')
        model_label.setObjectName('sectionTitle')
        form_layout.addWidget(model_label)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText('例如: deepseek-chat、deepseek-reasoner')
        self.model_input.setMinimumWidth(520)
        self.model_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addWidget(self.model_input)

        api_layout.addLayout(form_layout)
        layout.addWidget(api_section)
        layout.addStretch()

        return self._wrap_with_scroll(content)

    def _build_qwencoder_tab(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        self.qwencoder_checkbox = QCheckBox('使用 QwenCoder (DashScope) 接口进行评审调用')
        self.qwencoder_checkbox.setCursor(Qt.PointingHandCursor)
        self.qwencoder_checkbox.toggled.connect(self._on_qwencoder_checked)
        layout.addWidget(self.qwencoder_checkbox)

        qwen_overview = QLabel(
            '启用后，将调用阿里云 DashScope 兼容模式的 QwenCoder Chat Completions 接口。\n'
            '请提前在模型百炼控制台申请 API Key。'
        )
        qwen_overview.setWordWrap(True)
        qwen_overview.setObjectName('sectionHint')
        layout.addWidget(qwen_overview)

        api_section = QWidget()
        api_section.setObjectName('sectionCard')
        api_layout = QVBoxLayout(api_section)
        api_layout.setContentsMargins(20, 20, 20, 20)
        api_layout.setSpacing(16)

        api_title = QLabel('QwenCoder API 配置')
        api_title.setObjectName('sectionTitle')
        api_layout.addWidget(api_title)

        region_hint = QLabel(
            '国内推荐: https://dashscope.aliyuncs.com/compatible-mode/v1\n'
            '国际加速: https://dashscope-intl.aliyuncs.com/compatible-mode/v1'
        )
        region_hint.setWordWrap(True)
        region_hint.setObjectName('sectionHint')
        api_layout.addWidget(region_hint)

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        qwen_url_label = QLabel('API地址 / Base URL')
        qwen_url_label.setObjectName('sectionTitle')
        form_layout.addWidget(qwen_url_label)

        self.qwen_api_url_input = QLineEdit()
        self.qwen_api_url_input.setPlaceholderText('例如: https://dashscope.aliyuncs.com/compatible-mode/v1')
        self.qwen_api_url_input.setMinimumWidth(520)
        self.qwen_api_url_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addWidget(self.qwen_api_url_input)

        qwen_key_label = QLabel('API密钥 (AccessKey)')
        qwen_key_label.setObjectName('sectionTitle')
        form_layout.addWidget(qwen_key_label)

        self.qwen_api_key_input = QLineEdit()
        self.qwen_api_key_input.setPlaceholderText('输入 DashScope API Key，形如 sk-***')
        self.qwen_api_key_input.setEchoMode(QLineEdit.Password)
        self.qwen_api_key_input.setMinimumWidth(520)
        self.qwen_api_key_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addWidget(self.qwen_api_key_input)

        qwen_model_label = QLabel('模型名称')
        qwen_model_label.setObjectName('sectionTitle')
        form_layout.addWidget(qwen_model_label)

        self.qwen_model_input = QLineEdit()
        self.qwen_model_input.setPlaceholderText('例如: qwen3-coder-plus、qwen3-coder-flash')
        self.qwen_model_input.setMinimumWidth(520)
        self.qwen_model_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addWidget(self.qwen_model_input)

        api_layout.addLayout(form_layout)
        layout.addWidget(api_section)
        layout.addStretch()

        return self._wrap_with_scroll(content)

    def _build_doubao_tab(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        self.doubao_checkbox = QCheckBox('使用 DoubaoCoder 接口进行评审调用')
        self.doubao_checkbox.setCursor(Qt.PointingHandCursor)
        self.doubao_checkbox.toggled.connect(self._on_doubao_checked)
        layout.addWidget(self.doubao_checkbox)

        doubao_overview = QLabel(
            '启用后，将调用字节跳动 Doubao Coder Chat Completions 兼容接口。\n'
            '请确认已经申请 Doubao 平台的 API Key 并具有相应权限。'
        )
        doubao_overview.setWordWrap(True)
        doubao_overview.setObjectName('sectionHint')
        layout.addWidget(doubao_overview)

        api_section = QWidget()
        api_section.setObjectName('sectionCard')
        api_layout = QVBoxLayout(api_section)
        api_layout.setContentsMargins(20, 20, 20, 20)
        api_layout.setSpacing(16)

        api_title = QLabel('DoubaoCoder API 配置')
        api_title.setObjectName('sectionTitle')
        api_layout.addWidget(api_title)

        api_hint = QLabel(
            '推荐使用豆包开放平台兼容 OpenAI 的接口地址，例如:\n'
            'https://ark.cn-beijing.volces.com/api/v3/  (填写完整 chat/completions 地址亦可)'
        )
        api_hint.setWordWrap(True)
        api_hint.setObjectName('sectionHint')
        api_layout.addWidget(api_hint)

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        doubao_url_label = QLabel('API地址 / Base URL')
        doubao_url_label.setObjectName('sectionTitle')
        form_layout.addWidget(doubao_url_label)

        self.doubao_api_url_input = QLineEdit()
        self.doubao_api_url_input.setPlaceholderText('例如: https://ark.cn-beijing.volces.com/api/v3')
        self.doubao_api_url_input.setMinimumWidth(520)
        self.doubao_api_url_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addWidget(self.doubao_api_url_input)

        doubao_key_label = QLabel('API密钥')
        doubao_key_label.setObjectName('sectionTitle')
        form_layout.addWidget(doubao_key_label)

        self.doubao_api_key_input = QLineEdit()
        self.doubao_api_key_input.setPlaceholderText('输入 Doubao API Key，形如 db-***')
        self.doubao_api_key_input.setEchoMode(QLineEdit.Password)
        self.doubao_api_key_input.setMinimumWidth(520)
        self.doubao_api_key_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addWidget(self.doubao_api_key_input)

        doubao_model_label = QLabel('模型名称')
        doubao_model_label.setObjectName('sectionTitle')
        form_layout.addWidget(doubao_model_label)

        self.doubao_model_input = QLineEdit()
        self.doubao_model_input.setPlaceholderText('例如: doubao-1.5-pro 或 doubao-lite')
        self.doubao_model_input.setMinimumWidth(520)
        self.doubao_model_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form_layout.addWidget(self.doubao_model_input)

        api_layout.addLayout(form_layout)
        layout.addWidget(api_section)
        layout.addStretch()

        return self._wrap_with_scroll(content)

    def _build_prompt_tab(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        prompt_section = QWidget()
        prompt_section.setObjectName('sectionCard')
        prompt_layout = QVBoxLayout(prompt_section)
        prompt_layout.setContentsMargins(20, 20, 20, 20)
        prompt_layout.setSpacing(16)

        prompt_label = QLabel('提示词模板')
        prompt_label.setObjectName('sectionTitle')
        prompt_layout.addWidget(prompt_label)

        prompt_hint = QLabel('提示: 使用 {file_structure}、{code_content} 和 {functionality_checks} 作为占位符。')
        prompt_hint.setWordWrap(True)
        prompt_hint.setObjectName('sectionHint')
        prompt_layout.addWidget(prompt_hint)

        self.prompt_input = QTextEdit()
        self.prompt_input.setMinimumHeight(240)
        prompt_layout.addWidget(self.prompt_input)

        layout.addWidget(prompt_section)

        functionality_section = QWidget()
        functionality_section.setObjectName('sectionCard')
        functionality_layout = QVBoxLayout(functionality_section)
        functionality_layout.setContentsMargins(20, 20, 20, 20)
        functionality_layout.setSpacing(16)

        functionality_title = QLabel('功能性检查项目')
        functionality_title.setObjectName('sectionTitle')
        functionality_layout.addWidget(functionality_title)

        functionality_hint = QLabel(
            '提示：每行填写一个功能检查项目，这些项目会替换提示词中的 {functionality_checks} 占位符。'
        )
        functionality_hint.setWordWrap(True)
        functionality_hint.setObjectName('sectionHint')
        functionality_layout.addWidget(functionality_hint)

        example_label = QLabel('示例格式：')
        example_label.setStyleSheet('font-weight: 600; color: #666; margin-top: 8px;')
        functionality_layout.addWidget(example_label)

        example_text = QLabel(
            '• 用户登录功能是否完整实现\n'
            '• 数据库连接和操作是否正常\n'
            '• 文件上传下载功能是否可用\n'
            '• 表单验证是否完善'
        )
        example_text.setStyleSheet('color: #888; font-family: monospace; padding: 8px; background: #f5f5f5; border-radius: 4px;')
        example_text.setWordWrap(True)
        functionality_layout.addWidget(example_text)

        self.functionality_input = QTextEdit()
        self.functionality_input.setMinimumHeight(160)
        self.functionality_input.setPlaceholderText(
            '请输入功能检查项目，每行一个...\n\n例如：\n用户认证和授权功能\n数据处理和分析功能\n用户界面响应和交互功能'
        )
        functionality_layout.addWidget(self.functionality_input)

        layout.addWidget(functionality_section)
        layout.addStretch()

        return self._wrap_with_scroll(content)

    def _build_button_section(self) -> QWidget:
        button_section = QWidget()
        button_section.setObjectName('sectionCard')
        button_section_layout = QHBoxLayout(button_section)
        button_section_layout.setContentsMargins(20, 20, 20, 20)
        button_section_layout.setSpacing(12)

        reset_btn = PushButton('恢复默认')
        reset_btn.setMinimumWidth(120)
        reset_btn.clicked.connect(self.reset_to_default)

        cancel_btn = PushButton('取消')
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)

        save_btn = PrimaryPushButton('保存')
        save_btn.setMinimumWidth(120)
        save_btn.clicked.connect(self.save_settings)

        button_section_layout.addWidget(reset_btn)
        button_section_layout.addStretch()
        button_section_layout.addWidget(cancel_btn)
        button_section_layout.addWidget(save_btn)

        return button_section

    @staticmethod
    def _wrap_with_scroll(widget: QWidget) -> QScrollArea:
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setWidget(widget)
        return scroll_area

    def load_settings(self):
        """加载当前设置"""
        self.api_url_input.setText(self.config_manager.get('api_url', 'https://api.deepseek.com/v1/chat/completions'))
        self.api_key_input.setText(self.config_manager.get('api_key', ''))
        self.model_input.setText(self.config_manager.get('model_name', 'deepseek-chat'))

        self.qwen_api_url_input.setText(
            self.config_manager.get('qwencoder_api_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        )
        self.qwen_api_key_input.setText(self.config_manager.get('qwencoder_api_key', ''))
        self.qwen_model_input.setText(self.config_manager.get('qwencoder_model_name', 'qwen3-coder-plus'))

        self.doubao_api_url_input.setText(
            self.config_manager.get('doubao_api_url', 'https://ark.cn-beijing.volces.com/api/v3')
        )
        self.doubao_api_key_input.setText(self.config_manager.get('doubao_api_key', ''))
        self.doubao_model_input.setText(self.config_manager.get('doubao_model_name', 'doubao-1.5-pro'))

        self.prompt_input.setPlainText(self.config_manager.get('prompt_template', ''))
        self.functionality_input.setPlainText(self.config_manager.get('functionality_checks', ''))

        use_deepseek = bool(self.config_manager.get('use_deepseek', True))
        use_qwen = bool(self.config_manager.get('use_qwencoder', False))
        use_doubao = bool(self.config_manager.get('use_doubao', False))

        if not (use_deepseek or use_qwen or use_doubao):
            use_deepseek = True

        if use_doubao:
            active_provider = 'doubao'
        elif use_qwen:
            active_provider = 'qwencoder'
        else:
            active_provider = 'deepseek'

        self._select_provider(active_provider)

    def save_settings(self):
        """保存设置"""
        deepseek_api_url = self.api_url_input.text().strip()
        deepseek_api_key = self.api_key_input.text().strip()
        deepseek_model = self.model_input.text().strip()

        qwen_api_url = self.qwen_api_url_input.text().strip()
        qwen_api_key = self.qwen_api_key_input.text().strip()
        qwen_model = self.qwen_model_input.text().strip()

        doubao_api_url = self.doubao_api_url_input.text().strip()
        doubao_api_key = self.doubao_api_key_input.text().strip()
        doubao_model = self.doubao_model_input.text().strip()

        prompt_template = self.prompt_input.toPlainText().strip()
        functionality_checks = self.functionality_input.toPlainText().strip()

        if self.doubao_checkbox.isChecked():
            provider = 'doubao'
        elif self.qwencoder_checkbox.isChecked():
            provider = 'qwencoder'
        else:
            provider = 'deepseek'

        if provider == 'deepseek':
            if not deepseek_api_url:
                QMessageBox.warning(self, '警告', 'DeepSeek API地址不能为空')
                return

            if not deepseek_api_url.startswith('http'):
                QMessageBox.warning(self, '警告', 'DeepSeek API地址必须以 http 或 https 开头')
                return

            from urllib.parse import urlparse

            parsed_url = urlparse(deepseek_api_url)
            normalized_path = parsed_url.path.rstrip('/')
            allowed_paths = {'', '/', '/v1', '/v1/'}
            is_chat_endpoint = normalized_path.endswith('/chat/completions')

            if normalized_path not in allowed_paths and not is_chat_endpoint:
                QMessageBox.warning(
                    self,
                    '警告',
                    '建议填写完整的 chat/completions 接口地址，例如 https://api.deepseek.com/v1/chat/completions；'
                    '若使用基础地址，请确保与当前服务兼容。'
                )
                return

            if not deepseek_api_key:
                QMessageBox.warning(self, '警告', 'DeepSeek API密钥不能为空')
                return

            if not deepseek_model:
                QMessageBox.warning(self, '警告', 'DeepSeek 模型名称不能为空')
                return

            if deepseek_model.lower().startswith('gpt-'):
                QMessageBox.warning(
                    self,
                    '警告',
                    '当前接口不支持 gpt 系列模型，请填写 DeepSeek 提供的模型名称，例如 deepseek-chat 或 deepseek-reasoner'
                )
                return

        elif provider == 'qwencoder':
            if not qwen_api_url:
                QMessageBox.warning(self, '警告', 'QwenCoder API地址不能为空')
                return

            if not qwen_api_url.startswith('http'):
                QMessageBox.warning(self, '警告', 'QwenCoder API地址必须以 http 或 https 开头')
                return

            if 'dashscope' not in qwen_api_url:
                reply = QMessageBox.question(
                    self,
                    '确认地址',
                    '当前地址不像 DashScope 兼容模式接口，确定要继续保存吗？',
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return

            if not qwen_api_key:
                QMessageBox.warning(self, '警告', 'QwenCoder API密钥不能为空')
                return

            if not qwen_model:
                QMessageBox.warning(self, '警告', 'QwenCoder 模型名称不能为空')
                return

        else:
            if not doubao_api_url:
                QMessageBox.warning(self, '警告', 'DoubaoCoder API地址不能为空')
                return

            if not doubao_api_url.startswith('http'):
                QMessageBox.warning(self, '警告', 'DoubaoCoder API地址必须以 http 或 https 开头')
                return

            if 'volces' not in doubao_api_url and 'ark' not in doubao_api_url:
                reply = QMessageBox.question(
                    self,
                    '确认地址',
                    '当前地址不像 Doubao 兼容接口，确定要继续保存吗？',
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return

            if not doubao_api_key:
                QMessageBox.warning(self, '警告', 'DoubaoCoder API密钥不能为空')
                return

            if not doubao_model:
                QMessageBox.warning(self, '警告', 'DoubaoCoder 模型名称不能为空')
                return

        if not prompt_template:
            QMessageBox.warning(self, '警告', '提示词模板不能为空')
            return

        if '{file_structure}' not in prompt_template or '{code_content}' not in prompt_template:
            reply = QMessageBox.question(
                self,
                '确认',
                '提示词模板中缺少 {file_structure} 或 {code_content} 占位符，这可能导致评审效果不佳。确定要保存吗？',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        if not functionality_checks:
            QMessageBox.warning(self, '警告', '功能性检查项目不能为空')
            return

        success = self.config_manager.update({
            'api_url': deepseek_api_url,
            'api_key': deepseek_api_key,
            'model_name': deepseek_model,
            'qwencoder_api_url': qwen_api_url,
            'qwencoder_api_key': qwen_api_key,
            'qwencoder_model_name': qwen_model,
            'doubao_api_url': doubao_api_url,
            'doubao_api_key': doubao_api_key,
            'doubao_model_name': doubao_model,
            'prompt_template': prompt_template,
            'functionality_checks': functionality_checks,
            'use_deepseek': provider == 'deepseek',
            'use_qwencoder': provider == 'qwencoder',
            'use_doubao': provider == 'doubao'
        })

        if success:
            QMessageBox.information(self, '成功', '设置已保存')
            self.accept()
        else:
            QMessageBox.critical(self, '错误', '保存设置失败')
    
    def reset_to_default(self):
        """恢复默认设置"""
        reply = QMessageBox.question(
            self,
            '确认',
            '确定要恢复默认设置吗？',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config_manager.config = self.config_manager.default_config.copy()
            self.load_settings()

    def _on_deepseek_checked(self, checked: bool) -> None:
        if self._syncing_provider:
            return
        self._syncing_provider = True
        if checked:
            self.qwencoder_checkbox.setChecked(False)
            self.doubao_checkbox.setChecked(False)
        elif not (self.qwencoder_checkbox.isChecked() or self.doubao_checkbox.isChecked()):
            self.qwencoder_checkbox.setChecked(True)
        self._syncing_provider = False
        self._update_provider_state()

    def _on_qwencoder_checked(self, checked: bool) -> None:
        if self._syncing_provider:
            return
        self._syncing_provider = True
        if checked:
            self.deepseek_checkbox.setChecked(False)
            self.doubao_checkbox.setChecked(False)
        elif not (self.deepseek_checkbox.isChecked() or self.doubao_checkbox.isChecked()):
            self.deepseek_checkbox.setChecked(True)
        self._syncing_provider = False
        self._update_provider_state()

    def _on_doubao_checked(self, checked: bool) -> None:
        if self._syncing_provider:
            return
        self._syncing_provider = True
        if checked:
            self.deepseek_checkbox.setChecked(False)
            self.qwencoder_checkbox.setChecked(False)
        elif not (self.deepseek_checkbox.isChecked() or self.qwencoder_checkbox.isChecked()):
            self.deepseek_checkbox.setChecked(True)
        self._syncing_provider = False
        self._update_provider_state()

    def _select_provider(self, provider: str) -> None:
        self._syncing_provider = True
        self.deepseek_checkbox.setChecked(provider == 'deepseek')
        self.qwencoder_checkbox.setChecked(provider == 'qwencoder')
        self.doubao_checkbox.setChecked(provider == 'doubao')
        self._syncing_provider = False
        self._update_provider_state()

    def _update_provider_state(self) -> None:
        deepseek_enabled = self.deepseek_checkbox.isChecked()
        for widget in (self.api_url_input, self.api_key_input, self.model_input):
            widget.setEnabled(deepseek_enabled)

        qwen_enabled = self.qwencoder_checkbox.isChecked()
        for widget in (self.qwen_api_url_input, self.qwen_api_key_input, self.qwen_model_input):
            widget.setEnabled(qwen_enabled)

        doubao_enabled = self.doubao_checkbox.isChecked()
        for widget in (self.doubao_api_url_input, self.doubao_api_key_input, self.doubao_model_input):
            widget.setEnabled(doubao_enabled)

        self.tab_widget.setTabText(0, 'DeepSeek API (启用)' if deepseek_enabled else 'DeepSeek API')
        self.tab_widget.setTabText(1, 'QwenCoder API (启用)' if qwen_enabled else 'QwenCoder API')
        self.tab_widget.setTabText(2, 'DoubaoCoder API (启用)' if doubao_enabled else 'DoubaoCoder API')
