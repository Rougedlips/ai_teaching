<template>
  <div class="dashboard-page">
    <div class="top-row">
      <div>
        <div class="date">{{ todayText }}</div>
        <div class="hello">{{ realName || username }}，欢迎回来</div>
      </div>
      <div class="actions" v-if="userRole !== 'student'">
        <el-button plain type="primary" @click="openRanking">成绩排名</el-button>
        <el-button type="primary" @click="$router.push('/assignment-management')">+ Add Job</el-button>
      </div>
    </div>

    <el-row :gutter="16">
      <el-col :span="8">
        <el-card class="panel" shadow="never">
          <template #header><b>本学期概览</b></template>
          <div class="metrics">
            <div class="metric-item"><span>班级数</span><b>{{ summary.class_count }}</b></div>
            <div class="metric-item"><span>学生数</span><b>{{ summary.student_count }}</b></div>
            <div class="metric-item"><span>作业数</span><b>{{ summary.assignment_count }}</b></div>
            <div class="metric-item"><span>待批改</span><b>{{ summary.pending_review_count }}</b></div>
          </div>
        </el-card>

        <el-card class="panel" shadow="never">
          <template #header><b>任务状态</b></template>
          <div class="ring-wrap">
            <el-progress type="dashboard" :percentage="finishRate" :stroke-width="12" />
            <div class="ring-text">完成率</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card class="panel chart-panel" shadow="never">
          <template #header>
            <div class="chart-head">
              <div class="chart-title-wrap">
                <b>作业趋势</b>
                <el-tag type="info">{{ summary.semester || '未发布学期' }}</el-tag>
              </div>
              <el-radio-group v-model="trendMode" size="small" v-if="userRole !== 'student'">
                <el-radio-button label="day">按天</el-radio-button>
                <el-radio-button label="week">按周</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="chartRef" class="chart"></div>
        </el-card>

        <el-row :gutter="12" class="money-row">
          <el-col :span="8"><el-card class="mini" shadow="never"><span>班级数</span><b>{{ summary.class_count }}</b></el-card></el-col>
          <el-col :span="8"><el-card class="mini" shadow="never"><span>学生数</span><b>{{ summary.student_count }}</b></el-card></el-col>
          <el-col :span="8"><el-card class="mini" shadow="never"><span>待批改</span><b>{{ summary.pending_review_count }}</b></el-card></el-col>
        </el-row>
      </el-col>
    </el-row>

    <el-dialog v-model="showRanking" title="全班学情平均分排名" width="560px">
      <el-table :data="rankingList" stripe>
        <el-table-column type="index" label="排名" width="70" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="count" label="提交数" width="90" />
        <el-table-column prop="score" label="平均分" width="100" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import * as echarts from 'echarts'

interface TrendSeriesItem {
  name: string
  data: number[]
}

const username = ref(localStorage.getItem('username') || '')
const realName = ref(localStorage.getItem('real_name') || '')
const userRole = ref(localStorage.getItem('role') || 'student')
const userId = Number(localStorage.getItem('user_id') || 0)

const todayText = new Date().toLocaleDateString('zh-CN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })

const summary = ref({
  semester: '',
  class_count: 0,
  student_count: 0,
  assignment_count: 0,
  pending_review_count: 0
})

const trendMode = ref<'day' | 'week'>('day')
const trendLabels = ref<string[]>([])
const trendSeries = ref<TrendSeriesItem[]>([])

const showRanking = ref(false)
const rankingList = ref<any[]>([])

const finishRate = computed(() => {
  const total = summary.value.assignment_count
  if (!total) return 0
  const pending = summary.value.pending_review_count
  const done = Math.max(total - pending, 0)
  return Math.min(Math.round((done / total) * 100), 100)
})

const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

const renderChart = () => {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)

  const labels = trendLabels.value.length ? trendLabels.value : ['-', '-', '-', '-', '-', '-', '-']
  const fallbackPublished = { name: '发布作业', data: [0, 0, 0, 0, 0, 0, 0] }
  const fallbackSubmitted = { name: '提交人数', data: [0, 0, 0, 0, 0, 0, 0] }
  const fallbackFinished = { name: '已批改人数', data: [0, 0, 0, 0, 0, 0, 0] }

  const published = trendSeries.value[0] || fallbackPublished
  const submitted = trendSeries.value[1] || fallbackSubmitted
  const finished = trendSeries.value[2] || fallbackFinished

  chart.setOption({
    legend: { top: 0, data: [published.name, submitted.name, finished.name] },
    grid: { left: 20, right: 20, top: 40, bottom: 20, containLabel: true },
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value' },
    tooltip: { trigger: 'axis' },
    series: [
      {
        name: published.name,
        data: published.data,
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.1 },
        lineStyle: { width: 2, color: '#4f7cff' },
        itemStyle: { color: '#4f7cff' }
      },
      {
        name: submitted.name,
        data: submitted.data,
        type: 'line',
        smooth: true,
        lineStyle: { width: 2, color: '#34d399' },
        itemStyle: { color: '#34d399' }
      },
      {
        name: finished.name,
        data: finished.data,
        type: 'line',
        smooth: true,
        lineStyle: { width: 2, color: '#f59e0b' },
        itemStyle: { color: '#f59e0b' }
      }
    ]
  })
}

const onResize = () => chart?.resize()

const fetchSummary = async () => {
  if (userRole.value === 'student') return
  const res = await axios.get(`http://127.0.0.1:8000/teachers/${userId}/dashboard/summary`)
  summary.value = res.data
}

const fetchTrend = async () => {
  if (userRole.value === 'student') {
    trendLabels.value = []
    trendSeries.value = []
    return
  }

  const res = await axios.get(`http://127.0.0.1:8000/teachers/${userId}/dashboard/trend`, {
    params: { mode: trendMode.value }
  })
  trendLabels.value = res.data?.labels || []
  trendSeries.value = res.data?.series || []
}

const openRanking = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/analytics/student_ranking')
    rankingList.value = res.data
    showRanking.value = true
  } catch {
    ElMessage.error('获取排名失败')
  }
}

watch(trendMode, async () => {
  try {
    await fetchTrend()
    await nextTick()
    renderChart()
  } catch {
    ElMessage.error('趋势数据加载失败')
  }
})

onMounted(async () => {
  try {
    await fetchSummary()
    await fetchTrend()
    await nextTick()
    renderChart()
    window.addEventListener('resize', onResize)
  } catch {
    ElMessage.error('仪表盘数据加载失败')
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.dashboard-page { padding: 18px; background: #f5f7fb; min-height: calc(100vh - 60px); }
.top-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.date { font-size: 14px; color: #64748b; }
.hello { margin-top: 2px; font-size: 20px; font-weight: 700; color: #1e293b; }
.actions { display: flex; gap: 10px; }
.panel { border-radius: 14px; margin-bottom: 14px; }
.metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.metric-item { background: #f8fbff; border: 1px solid #e8efff; border-radius: 10px; padding: 12px; display: flex; justify-content: space-between; }
.metric-item span { color: #64748b; font-size: 13px; }
.metric-item b { color: #1e3a8a; }
.ring-wrap { display: flex; flex-direction: column; align-items: center; }
.ring-text { margin-top: 6px; color: #64748b; }
.chart-panel .chart { height: 280px; }
.chart-head { display: flex; justify-content: space-between; align-items: center; }
.chart-title-wrap { display: flex; align-items: center; gap: 10px; }
.money-row { margin-top: 2px; }
.mini { border-radius: 12px; }
.mini :deep(.el-card__body) { display: flex; justify-content: space-between; align-items: center; }
.mini span { color: #64748b; }
.mini b { color: #1e293b; font-size: 20px; }
</style>
