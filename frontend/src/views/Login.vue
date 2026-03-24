<template>
  <div class="login-wrapper">
    <el-card class="login-card">
      <template #header>
        <div class="login-header">
          <span style="font-size: 24px;">⚡ 智能教学辅助系统</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" stretch>
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" label-position="top">
            <el-form-item label="登录身份">
              <el-radio-group v-model="loginForm.role">
                <el-radio label="student">学生</el-radio>
                <el-radio label="teacher">老师</el-radio>
                <el-radio label="admin">管理员</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="用户名">
              <el-input v-model="loginForm.username" placeholder="请输入用户名" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="loginForm.password" type="password" show-password placeholder="请输入密码" />
            </el-form-item>
            <el-button type="primary" style="width: 100%; margin-top: 10px;" @click="handleLogin" :loading="loading">进入系统</el-button>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="注册" name="register">
          <el-form :model="registerForm" label-position="top">
            <el-form-item label="用户名"><el-input v-model="registerForm.username" /></el-form-item>
            <el-form-item label="密码"><el-input v-model="registerForm.password" type="password" /></el-form-item>
            <el-form-item label="身份选择">
              <el-radio-group v-model="registerForm.role">
                <el-radio label="student">我是学生</el-radio>
                <el-radio label="teacher">我是老师</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-button type="success" style="width: 100%;" @click="handleRegister">提交注册</el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeTab = ref('login')
const loading = ref(false)

const loginForm = reactive({ username: '', password: '', role: 'student' })
const registerForm = reactive({ username: '', password: '', role: 'student' })

// Login.vue 中的登录点击事件
const handleLogin = async () => {
  try {
    const res = await axios.post('http://127.0.0.1:8000/login/', loginForm);
    console.log("登录响应数据:", res.data); // 🌟 看看这里面 ID 的键名
    
    // 🌟 核心检查点：后端返回的是 id 还是 user_id？
    // 如果后端返回的是 { "id": 1, "username": "...", ... }
    const userId = res.data.id || res.data.user_id; 
    
    if (userId) {
      const backendRole = String(res.data.role || '')
      if (loginForm.role && backendRole !== loginForm.role) {
        ElMessage.error('所选身份与账号身份不一致，请重新选择')
        return
      }

      localStorage.setItem('user_id', userId.toString());
      localStorage.setItem('username', res.data.username);
      localStorage.setItem('real_name', res.data.real_name || '');
      localStorage.setItem('role', backendRole);

      ElMessage.success('登录成功！');
      router.push(backendRole === 'admin' ? '/admin-center' : '/');
    } else {
      console.error("后端响应中未找到用户ID:", res.data);
    }
  } catch (error) {
    ElMessage.error('登录失败，请检查账号密码');
  }
}

const handleRegister = async () => {
  try {
    await axios.post('http://127.0.0.1:8000/users/', registerForm)
    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login'
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '注册失败')
  }
}
</script>

<style scoped>
.login-wrapper {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f2f5;
}
.login-card {
  width: 400px;
  border-radius: 12px;
}
.login-header {
  text-align: center;
  font-weight: bold;
  color: #409EFF;
}
</style>