"""
后端API客户端模块
负责与FastAPI后端服务通信
"""
import json
import requests
from typing import Dict, Any, Optional, List
from api_config import BACKEND_API_URL


class BackendClient:
    def __init__(self, base_url: str = BACKEND_API_URL):
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.user_info = None

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        url = f"{self.base_url}/auth/token"
        data = {
            "username": username,
            "password": password
        }
        try:
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            self.token = result.get("access_token")
            # 获取用户信息
            self.user_info = self.get_current_user()
            return result
        except requests.exceptions.RequestException as exc:
            # 尝试获取更详细的错误信息
            error_detail = str(exc)
            if hasattr(exc, 'response') and exc.response is not None:
                try:
                    error_json = exc.response.json()
                    if 'detail' in error_json:
                        error_detail = f"登录失败: {error_json['detail']}"
                    else:
                        error_detail = f"登录失败: {exc.response.status_code} - {exc.response.text}"
                except:
                    error_detail = f"登录失败: {exc.response.status_code} - {exc.response.text}"
            raise Exception(error_detail)

    def register(self, username: str, email: str, password: str, role: str) -> Dict[str, Any]:
        """用户注册"""
        url = f"{self.base_url}/auth/register"
        data = {
            "username": username,
            "email": email,
            "password": password,
            "role": role
        }
        try:
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            # 尝试获取更详细的错误信息
            error_detail = str(exc)
            if hasattr(exc, 'response') and exc.response is not None:
                try:
                    error_json = exc.response.json()
                    if 'detail' in error_json:
                        error_detail = f"注册失败: {error_json['detail']}"
                    else:
                        error_detail = f"注册失败: {exc.response.status_code} - {exc.response.text}"
                except:
                    error_detail = f"注册失败: {exc.response.status_code} - {exc.response.text}"
            raise Exception(error_detail)

    def get_current_user(self) -> Dict[str, Any]:
        """获取当前用户信息"""
        if not self.token:
            raise Exception("用户未登录")
        
        url = f"{self.base_url}/auth/me"
        headers = self._get_auth_headers()
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            raise Exception(f"获取用户信息失败: {str(exc)}")
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """获取当前用户信息（别名方法，兼容旧代码）"""
        if not self.token:
            return None
        try:
            return self.get_current_user()
        except Exception:
            return None

    def get_courses(self) -> List[Dict[str, Any]]:
        """获取课程列表"""
        if not self.token:
            raise Exception("用户未登录")
        
        url = f"{self.base_url}/courses"
        headers = self._get_auth_headers()
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            raise Exception(f"获取课程列表失败: {str(exc)}")
    
    def get_course(self, course_id: int) -> Dict[str, Any]:
        """获取单个课程信息"""
        if not self.token:
            raise Exception("用户未登录")
        
        url = f"{self.base_url}/courses/{course_id}"
        headers = self._get_auth_headers()
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            raise Exception(f"获取课程信息失败: {str(exc)}")
    
    def update_course(self, course_id: int, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新课程信息"""
        if not self.token:
            raise Exception("用户未登录")
        
        url = f"{self.base_url}/courses/{course_id}"
        headers = self._get_auth_headers()
        
        try:
            response = requests.put(url, json=course_data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            raise Exception(f"更新课程失败: {str(exc)}")
    
    def delete_course(self, course_id: int) -> bool:
        """删除课程"""
        if not self.token:
            raise Exception("用户未登录")
        
        url = f"{self.base_url}/courses/{course_id}"
        headers = self._get_auth_headers()
        
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as exc:
            raise Exception(f"删除课程失败: {str(exc)}")

    def create_course(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建课程（教师权限）"""
        if not self.token:
            raise Exception("用户未登录")
        
        url = f"{self.base_url}/courses"
        headers = self._get_auth_headers()
        
        try:
            response = requests.post(url, json=course_data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            raise Exception(f"创建课程失败: {str(exc)}")

    def get_assignments(self, course_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取作业列表"""
        if not self.token:
            raise Exception("用户未登录")
        
        if course_id:
            url = f"{self.base_url}/assignments?course_id={course_id}"
        else:
            url = f"{self.base_url}/assignments"
        
        headers = self._get_auth_headers()
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            raise Exception(f"获取作业列表失败: {str(exc)}")

    def create_assignment(self, assignment_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建作业（教师权限）"""
        if not self.token:
            raise Exception("用户未登录")
        
        url = f"{self.base_url}/assignments"
        headers = self._get_auth_headers()
        
        try:
            response = requests.post(url, json=assignment_data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            raise Exception(f"创建作业失败: {str(exc)}")

    def submit_homework(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        """提交作业"""
        if not self.token:
            raise Exception("用户未登录")
        
        url = f"{self.base_url}/homeworks/submit"
        headers = self._get_auth_headers()
        
        try:
            response = requests.post(url, json=submission_data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            raise Exception(f"提交作业失败: {str(exc)}")
    
    def get_homework_submissions(self, homework_id: int) -> List[Dict[str, Any]]:
        """获取作业提交列表"""
        if not self.token:
            raise Exception("用户未登录")
        
        url = f"{self.base_url}/homeworks/{homework_id}/submissions"
        headers = self._get_auth_headers()
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            raise Exception(f"获取作业提交列表失败: {str(exc)}")
    
    def get_my_submission(self, homework_id: int) -> Dict[str, Any]:
        """获取我的作业提交"""
        if not self.token:
            raise Exception("用户未登录")
        
        url = f"{self.base_url}/homeworks/{homework_id}/my-submission"
        headers = self._get_auth_headers()
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            raise Exception(f"获取作业提交失败: {str(exc)}")
    
    def submit_review(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """提交评审结果"""
        if not self.token:
            raise Exception("用户未登录")
        
        url = f"{self.base_url}/reviews"
        headers = self._get_auth_headers()
        
        try:
            response = requests.post(url, json=review_data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            raise Exception(f"提交评审结果失败: {str(exc)}")

    def logout(self) -> None:
        """用户登出"""
        self.token = None
        self.user_info = None

    def is_authenticated(self) -> bool:
        """检查用户是否已认证"""
        return self.token is not None

    def is_teacher(self) -> bool:
        """检查当前用户是否为教师"""
        if not self.user_info:
            return False
        return self.user_info.get("role") == "teacher"

    def _get_auth_headers(self) -> Dict[str, str]:
        """获取带认证信息的请求头"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }