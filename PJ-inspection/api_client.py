"""
API客户端模块
负责与大模型API通信
"""
import json
from typing import Dict, List, Union
from urllib.parse import urlparse

try:
    from openai import OpenAI
    _OPENAI_IMPORT_ERROR = None
except ImportError as exc:
    OpenAI = None
    _OPENAI_IMPORT_ERROR = exc


class APIClient:
    def __init__(self, api_url: str, api_key: str, model_name: str):
        self.api_url = (api_url or '').strip()
        self.api_key = (api_key or '').strip()
        self.model_name = (model_name or '').strip()

    @classmethod
    def from_config(cls, config_manager: "ConfigManager") -> "APIClient":
        use_deepseek = bool(config_manager.get('use_deepseek', True))
        use_qwencoder = bool(config_manager.get('use_qwencoder', False))
        use_doubao = bool(config_manager.get('use_doubao', False))

        if not (use_deepseek or use_qwencoder or use_doubao):
            use_deepseek = True

        if use_doubao:
            api_url = config_manager.get('doubao_api_url')
            api_key = config_manager.get('doubao_api_key')
            model_name = config_manager.get('doubao_model_name')
        elif use_qwencoder:
            api_url = config_manager.get('qwencoder_api_url')
            api_key = config_manager.get('qwencoder_api_key')
            model_name = config_manager.get('qwencoder_model_name')
        else:
            api_url = config_manager.get('api_url')
            api_key = config_manager.get('api_key')
            model_name = config_manager.get('model_name')

        return cls(api_url or '', api_key or '', model_name or '')

    def _normalize_base_url(self, api_url: str) -> str:
        if not api_url:
            return 'https://api.deepseek.com'

        parsed = urlparse(api_url)
        if not parsed.scheme:
            raise Exception('API地址格式不正确，请以 http 或 https 开头')

        normalized = api_url.rstrip('/')
        if normalized.endswith('/chat/completions'):
            normalized = normalized[: normalized.rfind('/chat/completions')]
        return normalized or 'https://api.deepseek.com'

    def _merge_reasoning_and_content(self, message: Dict[str, Union[str, List[Dict[str, str]]]]) -> str:
        reasoning_segments = message.get('reasoning_content') or []
        reasoning_text_parts: List[str] = []

        if isinstance(reasoning_segments, list):
            for segment in reasoning_segments:
                if isinstance(segment, dict):
                    text = segment.get('text', '').strip()
                    if text:
                        reasoning_text_parts.append(text)
        elif isinstance(reasoning_segments, str):
            reasoning_text_parts.append(reasoning_segments.strip())

        final_parts: List[str] = []
        if reasoning_text_parts:
            final_parts.append('\n'.join(reasoning_text_parts))

        content = (message.get('content') or '').strip()
        if content:
            final_parts.append(content)

        if final_parts:
            return '\n\n'.join(final_parts)

        return json.dumps(message, indent=2, ensure_ascii=False)

    def call_api(self, prompt: str) -> str:
        if not self.api_key:
            raise Exception('API密钥未配置')

        if not self.model_name:
            raise Exception('模型名称未配置')

        if OpenAI is None:
            raise Exception(
                '未找到 openai 库，请先执行 `pip install -r requirements.txt` 或 `pip install openai`'
            ) from _OPENAI_IMPORT_ERROR

        base_url = self._normalize_base_url(self.api_url)

        try:
            client = OpenAI(api_key=self.api_key, base_url=base_url)
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a senior software architect responsible for thorough code reviews.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )
        except Exception as exc:
            raise Exception(f'API请求失败: {str(exc)}') from exc

        result = response.model_dump()
        choices = result.get('choices', [])
        if not choices:
            raise Exception(f"API响应异常: {json.dumps(result, indent=2, ensure_ascii=False)}")

        message = choices[0].get('message', {})
        return self._merge_reasoning_and_content(message)
