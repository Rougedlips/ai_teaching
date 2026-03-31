<template>
  <router-view v-if="$route.path === '/login'" />

  <div v-else class="shell">
    <header class="topbar">
      <div class="brand">EduAI Project辅助教学管理平台</div>
      <div class="top-actions">
        <el-tag type="warning" effect="dark">学期：{{ currentSemesterName || '未发布' }}</el-tag>
        <el-dropdown>
          <span class="user-display">
            {{ realName || username || '未登录用户' }}
            <el-tag size="small" effect="plain" style="margin-left: 8px">
              {{ userRole === 'admin' ? '管理员' : userRole === 'teacher' ? '教师' : userRole === 'student' ? '学生' : '未知身份' }}
            </el-tag>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-if="userRole === 'student'" @click="$router.push('/profile')">修改资料</el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <div class="workbench">
      <aside class="sider">
        <el-menu :default-active="activeMenu" router class="side-menu">
          <el-menu-item index="/">
            <el-icon><House /></el-icon>
            <span>首页工作台</span>
          </el-menu-item>

          <template v-if="userRole === 'teacher' || userRole === 'admin'">
            <el-menu-item index="/model-config">
              <el-icon><Cpu /></el-icon>
              <span>大模型批改参数配置</span>
            </el-menu-item>

            <el-sub-menu index="student-management">
              <template #title>
                <el-icon><User /></el-icon>
                <span>学生管理</span>
              </template>
              <el-menu-item
                v-for="cls in teacherClassList"
                :key="`s-${cls.id}`"
                :index="`/student-management/${cls.id}`"
              >
                <span class="class-menu-label">{{ cls.name }}</span>
              </el-menu-item>
              <el-menu-item v-if="!teacherClassList.length" index="/student-management">暂无本学期班级</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="assignment-management">
              <template #title>
                <el-icon><Document /></el-icon>
                <span>作业管理</span>
              </template>
              <el-menu-item
                v-for="cls in teacherClassList"
                :key="`a-${cls.id}`"
                :index="`/assignment-management/${cls.id}`"
              >
                <span class="class-menu-label">{{ cls.name }}</span>
              </el-menu-item>
              <el-menu-item v-if="!teacherClassList.length" index="/assignment-management">暂无本学期班级</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="report-management">
              <template #title>
                <el-icon><Document /></el-icon>
                <span>报告管理</span>
              </template>
              <el-menu-item
                v-for="cls in teacherClassList"
                :key="`r-${cls.id}`"
                :index="`/report-management/${cls.id}`"
              >
                <span class="class-menu-label">{{ cls.name }}</span>
              </el-menu-item>
              <el-menu-item v-if="!teacherClassList.length" index="/report-management">暂无本学期班级</el-menu-item>
            </el-sub-menu>

            <el-menu-item v-if="userRole === 'teacher'" index="/project-selection">
              <el-icon><Files /></el-icon>
              <span>综合项目选题管理</span>
            </el-menu-item>

            <el-menu-item v-if="userRole === 'admin'" index="/admin-center">
              <el-icon><Setting /></el-icon>
              <span>管理员中心</span>
            </el-menu-item>
            <el-menu-item v-if="userRole === 'admin'" index="/admin-project-management">
              <el-icon><Files /></el-icon>
              <span>综合项目管理</span>
            </el-menu-item>
          </template>

          <template v-if="userRole === 'student'">
            <el-sub-menu index="my-assignments">
              <template #title>
                <el-icon><Files /></el-icon>
                <span>我的作业</span>
              </template>
              <el-menu-item
                v-for="cls in studentClassList"
                :key="`stu-a-${cls.id}`"
                :index="`/my-assignments/${cls.id}`"
              >
                <span class="class-menu-label">{{ cls.name }}</span>
              </el-menu-item>
              <el-menu-item v-if="!studentClassList.length" index="/my-assignments">暂无本学期班级</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="my-reports">
              <template #title>
                <el-icon><Files /></el-icon>
                <span>我的报告</span>
              </template>
              <el-menu-item
                v-for="cls in studentClassList"
                :key="`stu-r-${cls.id}`"
                :index="`/my-reports/${cls.id}`"
              >
                <span class="class-menu-label">{{ cls.name }}</span>
              </el-menu-item>
              <el-menu-item v-if="!studentClassList.length" index="/my-reports">暂无本学期班级</el-menu-item>
            </el-sub-menu>
            <el-menu-item index="/group-manager">
              <el-icon><UserFilled /></el-icon>
              <span>综合项目申请管理</span>
            </el-menu-item>
            <el-menu-item index="/profile">
              <el-icon><DataAnalysis /></el-icon>
              <span>个人能力画像</span>
            </el-menu-item>
          </template>
        </el-menu>
      </aside>

      <main class="main-panel">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { House, Cpu, User, Document, Files, UserFilled, DataAnalysis, Setting } from '@element-plus/icons-vue'
import axios from 'axios'

interface NavClassItem {
  id: number
  name: string
  semester: string
  teacher_id: number
}

const router = useRouter()
const route = useRoute()

const username = ref(localStorage.getItem('username'))
const realName = ref(localStorage.getItem('real_name'))
const userRole = ref(localStorage.getItem('role'))
const userId = ref(Number(localStorage.getItem('user_id') || 0))
const currentSemesterName = ref('')
const teacherClassList = ref<NavClassItem[]>([])
const studentClassList = ref<NavClassItem[]>([])

const activeMenu = computed(() => route.path)

const refreshClassList = async () => {
  try {
    const semesterRes = await axios.get('http://127.0.0.1:8000/semesters/current')
    currentSemesterName.value = semesterRes.data?.name || ''

    if (userRole.value === 'teacher' || userRole.value === 'admin') {
      const url = userRole.value === 'admin'
        ? 'http://127.0.0.1:8000/admin/classes/current'
        : `http://127.0.0.1:8000/teachers/${userId.value}/classes/current`

      const clsRes = await axios.get(url)
      teacherClassList.value = clsRes.data || []
      studentClassList.value = []
      return
    }

    if (userRole.value === 'student') {
      teacherClassList.value = []
      const clsRes = await axios.get(`http://127.0.0.1:8000/students/${userId.value}/classes/current`)
      studentClassList.value = clsRes.data || []
      return
    }

    teacherClassList.value = []
    studentClassList.value = []
  } catch {
    teacherClassList.value = []
    studentClassList.value = []
    currentSemesterName.value = ''
  }
}

watch(() => route.path, async () => {
  username.value = localStorage.getItem('username')
  realName.value = localStorage.getItem('real_name')
  userRole.value = localStorage.getItem('role')
  userId.value = Number(localStorage.getItem('user_id') || 0)
  await refreshClassList()
}, { immediate: true })

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出系统吗？', '提示', { type: 'warning' }).then(() => {
    localStorage.clear()
    router.push('/login')
  })
}
</script>

<style scoped>
.shell { min-height: 100vh; background: #f4f6fb; }
.topbar {
  height: 56px;
  background: #2f6bff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 18px;
  box-shadow: 0 2px 10px rgba(47, 107, 255, 0.25);
}
.brand { font-weight: 700; letter-spacing: 0.5px; }
.top-actions { display: flex; align-items: center; gap: 12px; }
.user-display { color: #fff; cursor: pointer; display: flex; align-items: center; }
.workbench { display: grid; grid-template-columns: 195px 1fr; min-height: calc(100vh - 56px); }
.sider {
  background: #fff;
  border-right: 1px solid #eef1f7;
  overflow-y: auto;
}
.side-menu { border-right: none; padding: 6px 4px 10px; }
:deep(.side-menu .el-menu-item),
:deep(.side-menu .el-sub-menu__title) {
  height: auto;
  min-height: 40px;
  line-height: 1.35;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 10px !important;
  padding-right: 8px !important;
  border-radius: 8px;
  margin: 4px 2px;
}
:deep(.side-menu .el-menu-item .el-icon),
:deep(.side-menu .el-sub-menu__title .el-icon) {
  margin-right: 6px;
}
:deep(.side-menu .el-menu-item span),
:deep(.side-menu .el-sub-menu__title span) {
  white-space: normal;
  overflow-wrap: anywhere;
  word-break: break-word;
  line-height: 1.35;
}
:deep(.side-menu .el-menu-item.is-active) {
  background: #2f6bff;
  color: #fff;
  font-weight: 600;
}
:deep(.side-menu .el-menu-item.is-active .el-icon) {
  color: #fff;
}
:deep(.side-menu .el-menu-item:hover),
:deep(.side-menu .el-sub-menu__title:hover) {
  background: #eef3ff;
}
:deep(.side-menu .el-sub-menu .el-menu-item) {
  color: #8a94a6;
  padding-left: 28px !important;
}
:deep(.side-menu .el-sub-menu .el-menu-item:hover) {
  color: #5f6b80;
}
:deep(.side-menu .el-sub-menu .el-menu-item.is-active) {
  color: #fff;
  padding-left: 28px !important;
}
.class-menu-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: 10em;
  white-space: normal;
  word-break: break-all;
  line-height: 1.35;
}
.class-menu-label::before {
  content: '▸';
  color: #a3acbb;
  font-size: 12px;
  transform: translateY(-0.5px);
}
:deep(.side-menu .el-sub-menu .el-menu-item.is-active .class-menu-label::before) {
  color: rgba(255, 255, 255, 0.9);
}
.main-panel { padding: 16px; overflow: auto; }
</style>
