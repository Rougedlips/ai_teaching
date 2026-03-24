"""
API配置文件
管理所有API服务器的地址和配置
"""

# 后端API服务器配置
BACKEND_API_URL = "http://43.138.174.60:8000/api"

# OpenAI API配置（如果使用）
OPENAI_API_URL = "https://api.openai.com/v1"

# API连接配置
REQUEST_TIMEOUT = 30  # 请求超时时间（秒）
MAX_RETRIES = 3      # 最大重试次数

# CORS配置（如果需要）
ALLOWED_ORIGINS = ["http://43.138.174.60:3000", "http://localhost:3000"]