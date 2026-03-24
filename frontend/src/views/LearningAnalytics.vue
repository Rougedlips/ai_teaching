<template>
  <div class="page-container">
    <el-row :gutter="16">
      <el-col :span="8">
        <el-card shadow="never">
          <el-statistic title="已发布作业数" :value="assignCount" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <el-statistic title="纳入统计学生数" :value="rankingList.length" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <el-statistic title="班级平均分" :value="classAvg" :precision="2" />
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="table-card">
      <template #header>
        <span>📊 学情统计（学生平均分排名）</span>
      </template>
      <el-table :data="rankingList" stripe>
        <el-table-column type="index" label="排名" width="70" align="center" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="count" label="提交次数" width="120" align="center" />
        <el-table-column prop="score" label="平均分" width="120" align="center" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

interface RankItem {
  name: string
  score: number
  count: number
}

const rankingList = ref<RankItem[]>([])
const assignCount = ref(0)

const classAvg = computed(() => {
  if (!rankingList.value.length) return 0
  const total = rankingList.value.reduce((sum, item) => sum + Number(item.score || 0), 0)
  return total / rankingList.value.length
})

const fetchData = async () => {
  try {
    const [rankingRes, assignmentRes] = await Promise.all([
      axios.get('http://127.0.0.1:8000/analytics/student_ranking'),
      axios.get('http://127.0.0.1:8000/assignments/all')
    ])
    rankingList.value = rankingRes.data || []
    assignCount.value = (assignmentRes.data || []).length
  } catch {
    ElMessage.error('加载学情统计失败，请检查后端服务')
  }
}

onMounted(fetchData)
</script>

<style scoped>
.page-container { padding: 24px; background: #f8fafc; min-height: calc(100vh - 60px); }
.table-card { margin-top: 16px; }
</style>
