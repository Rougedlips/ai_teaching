import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Login from '../views/Login.vue'
import CodeEditor from '../views/CodeEditor.vue'
import TeacherConsole from '../views/TeacherConsole.vue'
import Profile from '../views/Profile.vue'
import GroupManager from '../views/GroupManager.vue'
import StudentAssignments from '../views/StudentAssignments.vue'
import StudentReports from '../views/StudentReports.vue'
import ModelConfig from '../views/ModelConfig.vue'
import LearningAnalytics from '../views/LearningAnalytics.vue'
import StudentManagement from '../views/StudentManagement.vue'
import AssignmentManagement from '../views/AssignmentManagement.vue'
import ReportManagement from '../views/ReportManagement.vue'
import AdminCenter from '../views/AdminCenter.vue'
import TeacherProjectSelection from '../views/TeacherProjectSelection.vue'
import AdminProjectManagement from '../views/AdminProjectManagement.vue'



const routes: Array<RouteRecordRaw> = [
  { path: '/login', name: 'Login', component: Login },
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/editor', name: 'Editor', component: CodeEditor },
  {
    path: '/my-assignments/:classId?',
    name: 'StudentAssignments',
    component: StudentAssignments,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/my-reports/:classId?',
    name: 'StudentReports',
    component: StudentReports,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/group-manager',
    name: 'GroupManager',
    component: GroupManager,
    meta: { requiresAuth: true, role: 'student' }
  },

  { path: '/teacher-console', name: 'TeacherConsole', component: TeacherConsole },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true, role: 'student' }
  },

  {
    path: '/model-config',
    name: 'ModelConfig',
    component: ModelConfig,
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/analytics',
    name: 'LearningAnalytics',
    component: LearningAnalytics,
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/student-management/:classId?',
    name: 'StudentManagement',
    component: StudentManagement,
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/assignment-management/:classId?',
    name: 'AssignmentManagement',
    component: AssignmentManagement,
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/report-management/:classId?',
    name: 'ReportManagement',
    component: ReportManagement,
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/project-selection',
    name: 'TeacherProjectSelection',
    component: TeacherProjectSelection,
    meta: { requiresAuth: true, role: 'teacher' }
  },

  {
    path: '/admin-center',
    name: 'AdminCenter',
    component: AdminCenter,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin-project-management',
    name: 'AdminProjectManagement',
    component: AdminProjectManagement,
    meta: { requiresAuth: true, role: 'admin' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 🌟 路由守卫：防止未登录或越权访问
router.beforeEach((to) => {
  const role = localStorage.getItem('role')
  const userId = localStorage.getItem('user_id')

  if (to.path !== '/login' && !userId) {
    return '/login'
  }

  if (role === 'student' && to.path === '/editor') {
    return '/my-assignments'
  }

  if (to.meta.role && to.meta.role !== role && role !== 'admin') {
    return '/'
  }

  return true
})

export default router