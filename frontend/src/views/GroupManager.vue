<template>
  <div class="group-manager-container">
    <el-card shadow="never" class="main-card">
      <template #header>
        <div class="header-content">
          <div class="title-area">
            <h3>👥 我的组队</h3>
            <p>按班级查看你所在的小组与成员</p>
          </div>
          <el-button type="primary" plain @click="loadTeams">刷新</el-button>
        </div>
      </template>

      <el-empty v-if="!rows.length && !loading" description="暂无组队信息" :image-size="100" />

      <el-row v-else :gutter="16" v-loading="loading">
        <el-col :span="12" v-for="item in rows" :key="item.class_id" style="margin-bottom: 12px">
          <el-card shadow="hover" class="team-item-card">
            <template #header>
              <div class="team-card-header">
                <div>
                  <b>{{ item.class_name }}</b>
                  <el-tag size="small" style="margin-left: 8px">共 {{ item.team_total }} 个小组</el-tag>
                </div>
                <el-tag :type="item.team?.id ? 'success' : 'info'">
                  {{ item.team?.id ? '已入组' : '未入组' }}
                </el-tag>
              </div>
            </template>

            <el-empty v-if="!item.team?.id" description="你当前在该班级未加入小组" :image-size="70" />

            <template v-else>
              <div class="team-name">我的小组：{{ item.team?.name }}</div>
              <div class="member-list">
                <div v-for="member in item.team?.members || []" :key="member.id" class="member-row">
                  <div class="member-info">
                    <el-avatar :size="24">{{ (member.name?.[0] || '?').toUpperCase() }}</el-avatar>
                    <span>{{ member.name }}</span>
                  </div>
                  <el-tag size="small" effect="plain">{{ member.student_no || member.username }}</el-tag>
                </div>
              </div>
            </template>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

interface TeamMember {
  id: number
  name: string
  student_no?: string | null
  username?: string
}

interface TeamOverviewRow {
  class_id: number
  class_name: string
  team_total: number
  team?: {
    id?: number | null
    name?: string | null
    members?: TeamMember[]
  }
}

const studentId = Number(localStorage.getItem('user_id') || 0)
const loading = ref(false)
const rows = ref<TeamOverviewRow[]>([])

const loadTeams = async () => {
  if (!studentId) return
  loading.value = true
  try {
    const res = await axios.get(`http://127.0.0.1:8000/students/${studentId}/teams`)
    rows.value = Array.isArray(res.data) ? res.data : []
  } catch (e: any) {
    rows.value = []
    ElMessage.error(e?.response?.data?.detail || '获取组队信息失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadTeams)
</script>

<style scoped>
.group-manager-container { padding: 25px; background-color: #f8fafc; min-height: calc(100vh - 60px); }
.main-card { border-radius: 15px; }
.header-content { display: flex; justify-content: space-between; align-items: flex-start; }
.title-area h3 { margin: 0 0 5px 0; color: #1e293b; }
.title-area p { margin: 0; color: #64748b; font-size: 14px; }
.team-item-card { border-radius: 12px; }
.team-card-header { display: flex; justify-content: space-between; align-items: center; }
.team-name { color: #334155; font-weight: 600; margin-bottom: 8px; }
.member-list { margin-top: 6px; }
.member-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f1f5f9;
}
.member-row:last-child { border-bottom: none; }
.member-info { display: flex; align-items: center; gap: 10px; font-size: 14px; }
</style>
