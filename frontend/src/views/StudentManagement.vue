<template>
  <div class="page-container">
    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="header-row">
          <div>
            <div class="title-row">
              <div class="title">学生管理</div>
            </div>
            <div class="sub-title" v-if="currentClassMeta">当前班级：{{ currentClassMeta.name }}</div>
          </div>
          <div style="display:flex; gap:10px; align-items:center;">
            <el-button v-if="currentRole === 'admin'" type="primary" plain @click="publishSemester">发布当前学期</el-button>
          </div>
        </div>
      </template>

      <el-empty v-if="!currentClassMeta" description="当前学期暂无可管理班级" />

      <template v-else>
        <el-tabs v-model="activeTab">
          <el-tab-pane label="本学期班级学生列表" name="students">
            <el-table :data="students" stripe v-loading="loadingOverview">
              <el-table-column prop="student_no" label="学号" width="140" />
              <el-table-column prop="name" label="姓名" width="160" />
              <el-table-column prop="username" label="账号" width="160" />
              <el-table-column label="操作栏：作业得分" min-width="360">
                <template #default="scope">
                  <el-popover placement="top-start" :width="380" trigger="hover">
                    <template #reference>
                      <el-button size="small" type="primary" plain>查看每次作业得分</el-button>
                    </template>
                    <div class="score-grid">
                      <div v-for="assign in assignments" :key="assign.id" class="score-row">
                        <span>{{ assign.title }}</span>
                        <el-tag>{{ getScore(scope.row, assign.id) }}</el-tag>
                      </div>
                    </div>
                  </el-popover>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="本班级组队情况" name="teams">
            <div class="toolbar">
              <el-button type="primary" @click="createTeam">新增队伍</el-button>
              <el-button type="success" plain @click="openTransferDialog">调整成员队伍</el-button>
            </div>

            <el-row :gutter="16" v-loading="loadingTeams">
              <el-col :span="8" v-for="team in teams" :key="team.id">
                <el-card shadow="hover" class="team-card">
                  <template #header>
                    <div class="team-head">
                      <span>{{ team.name }}</span>
                      <el-button link type="danger" @click="removeTeam(team.id)">删除</el-button>
                    </div>
                  </template>

                  <el-select
                    :model-value="team.members"
                    multiple
                    style="width: 100%"
                    placeholder="选择成员"
                    @change="onTeamMemberChange(team.id, $event)"
                  >
                    <el-option
                      v-for="s in students"
                      :key="s.id"
                      :label="s.name"
                      :value="s.id"
                    />
                  </el-select>

                  <div class="member-tags">
                    <el-tag v-for="id in team.members" :key="id" effect="plain">{{ getStudentName(id) }}</el-tag>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </el-tab-pane>

          <el-tab-pane label="学情统计" name="learning">
            <div class="toolbar">
              <el-button @click="downloadLearningTemplate">下载问卷模板</el-button>
              <el-upload :show-file-list="false" :http-request="uploadLearningSurvey" accept=".xlsx">
                <el-button type="primary" plain>上传问卷</el-button>
              </el-upload>
              <el-tag type="info">已上传 {{ learningStats.questionnaire.uploaded_count }} / {{ learningStats.questionnaire.total_students }}</el-tag>
            </div>

            <el-row :gutter="16" v-loading="learningLoading">
              <el-col :span="12">
                <el-card shadow="never" class="chart-card">
                  <template #header><span>作业项目完成趋势</span></template>
                  <div ref="completionChartRef" class="chart-box"></div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card shadow="never" class="chart-card">
                  <template #header><span>思维雷达</span></template>
                  <div ref="radarChartRef" class="chart-box radar-chart-box"></div>
                </el-card>
              </el-col>
            </el-row>

            <el-card shadow="never" class="chart-card cloud-card" v-loading="learningLoading">
              <template #header>
                <div class="cloud-header">
                  <span>思维云图</span>
                  <el-tag size="small" type="info">已分析报告：{{ learningStats.thinking_cloud.source_report_count }}</el-tag>
                </div>
              </template>
              <div ref="thinkingCloudChartRef" class="cloud-chart-box"></div>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </template>
    </el-card>

    <el-dialog v-model="transferVisible" title="调整成员队伍" width="460px">
      <el-form label-width="90px">
        <el-form-item label="学生">
          <el-select v-model="transferForm.studentId" style="width: 100%">
            <el-option v-for="s in students" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="目标队伍">
          <el-select v-model="transferForm.targetTeamId" style="width: 100%">
            <el-option v-for="t in teams" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="transferVisible = false">取消</el-button>
        <el-button type="primary" @click="transferMember">确认调整</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadRequestOptions } from 'element-plus'
import * as echarts from 'echarts'
import axios from 'axios'

interface ClassItem {
  id: number
  name: string
  semester: string
  teacher_id: number
}

interface AssignmentItem { id: number; title: string }
interface StudentItem {
  id: number
  student_no?: string | null
  username?: string
  name: string
  class_name?: string | null
  scores: Record<string, number | null>
}
interface TeamItem { id: number; name: string; members: number[] }
interface LearningCompletionItem {
  item_id: number
  item_name: string
  finished_count: number
  total_count: number
  completion_rate: number
}
interface ThinkingCloudWord {
  name: string
  value: number
}
interface LearningStatsResponse {
  completion_items: LearningCompletionItem[]
  radar: {
    analysis_ability: number
    open_mind: number
    thinking_confidence: number
    components: {
      academic_analysis: number
      questionnaire_analysis: number
      questionnaire_open_mind: number
      questionnaire_thinking_confidence: number
    }
  }
  questionnaire: {
    uploaded_count: number
    total_students: number
    latest_upload_time: string | null
  }
  thinking_cloud: {
    words: ThinkingCloudWord[]
    source_report_count: number
  }
}

const route = useRoute()
const router = useRouter()

const activeTab = ref('students')
const currentRole = localStorage.getItem('role') || 'teacher'
const currentUserId = Number(localStorage.getItem('user_id') || 0)

const classes = ref<ClassItem[]>([])
const assignments = ref<AssignmentItem[]>([])
const students = ref<StudentItem[]>([])
const teams = ref<TeamItem[]>([])

const loadingOverview = ref(false)
const loadingTeams = ref(false)
const learningLoading = ref(false)
const transferVisible = ref(false)
const transferForm = ref({ studentId: 0, targetTeamId: 0 })
const learningStats = ref<LearningStatsResponse>({
  completion_items: [],
  radar: {
    analysis_ability: 0,
    open_mind: 0,
    thinking_confidence: 0,
    components: {
      academic_analysis: 0,
      questionnaire_analysis: 0,
      questionnaire_open_mind: 0,
      questionnaire_thinking_confidence: 0,
    },
  },
  questionnaire: {
    uploaded_count: 0,
    total_students: 0,
    latest_upload_time: null,
  },
  thinking_cloud: {
    words: [],
    source_report_count: 0,
  },
})
const completionChartRef = ref<HTMLDivElement | null>(null)
const radarChartRef = ref<HTMLDivElement | null>(null)
const thinkingCloudChartRef = ref<HTMLDivElement | null>(null)
let completionChart: echarts.ECharts | null = null
let radarChart: echarts.ECharts | null = null
let thinkingCloudChart: echarts.ECharts | null = null

const currentClassId = computed(() => Number(route.params.classId || 0))
const currentClassMeta = computed(() => classes.value.find((c) => c.id === currentClassId.value) || null)

const fetchClasses = async () => {
  const url = currentRole === 'admin'
    ? 'http://127.0.0.1:8000/admin/classes/current'
    : `http://127.0.0.1:8000/teachers/${currentUserId}/classes/current`

  const res = await axios.get(url)
  classes.value = res.data || []

  if (!classes.value.length) return
  if (!currentClassMeta.value) {
    const firstClass = classes.value[0]
    if (firstClass) await router.replace(`/student-management/${firstClass.id}`)
  }
}

const fetchClassOverview = async () => {
  if (!currentClassId.value) {
    assignments.value = []
    students.value = []
    teams.value = []
    return
  }

  loadingOverview.value = true
  loadingTeams.value = true
  try {
    if (currentRole === 'teacher') {
      const res = await axios.get(`http://127.0.0.1:8000/teachers/${currentUserId}/classes/${currentClassId.value}/dashboard`)
      assignments.value = res.data.assignments || []
      students.value = res.data.students || []
      teams.value = res.data.teams || []
      await fetchLearningStats()
      return
    }

    const [overviewRes, teamsRes] = await Promise.all([
      axios.get(`http://127.0.0.1:8000/classes/${currentClassId.value}/overview`),
      axios.get(`http://127.0.0.1:8000/classes/${currentClassId.value}/teams`)
    ])
    assignments.value = overviewRes.data.assignments || []
    students.value = overviewRes.data.students || []
    teams.value = teamsRes.data || []
    learningStats.value.completion_items = []
  } catch {
    assignments.value = []
    students.value = []
    teams.value = []
    learningStats.value.completion_items = []
    learningStats.value.thinking_cloud = { words: [], source_report_count: 0 }
    throw new Error('overview_failed')
  } finally {
    loadingOverview.value = false
    loadingTeams.value = false
  }
}

const fetchTeams = async () => {
  if (!currentClassId.value) {
    teams.value = []
    return
  }

  loadingTeams.value = true
  try {
    if (currentRole === 'teacher') {
      const res = await axios.get(`http://127.0.0.1:8000/teachers/${currentUserId}/classes/${currentClassId.value}/dashboard`)
      teams.value = res.data?.teams || []
      if (Array.isArray(res.data?.students)) {
        students.value = res.data.students
      }
      return
    }

    const res = await axios.get(`http://127.0.0.1:8000/classes/${currentClassId.value}/teams`)
    teams.value = res.data || []
  } catch {
    teams.value = []
  } finally {
    loadingTeams.value = false
  }
}

const fetchAll = async () => {
  try {
    await fetchClasses()
    await fetchClassOverview()
  } catch {
    ElMessage.error('学生管理数据加载失败，请检查后端服务')
  }
}

watch(() => route.params.classId, async () => {
  await fetchClassOverview()
}, { immediate: true })

watch(() => route.path, async () => {
  await fetchAll()
}, { immediate: true })

watch(() => activeTab.value, async (tab) => {
  if (tab === 'learning') {
    await fetchLearningStats()
  }
})

const onResize = () => {
  completionChart?.resize()
  radarChart?.resize()
}

window.addEventListener('resize', onResize)
onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  completionChart?.dispose()
  radarChart?.dispose()
  thinkingCloudChart?.dispose()
  completionChart = null
  radarChart = null
  thinkingCloudChart = null
})

const getScore = (student: StudentItem, assignmentId: number) => {
  const v = student.scores[String(assignmentId)]
  return v == null ? '-' : v
}

const getStudentName = (studentId: number) => {
  const s = students.value.find((x) => x.id === studentId)
  return s ? s.name : `学生${studentId}`
}

const renderCompletionChart = () => {
  if (!completionChartRef.value) return
  if (!completionChart) completionChart = echarts.init(completionChartRef.value)

  const labels = learningStats.value.completion_items.map((x) => x.item_name)
  const values = learningStats.value.completion_items.map((x) => x.completion_rate)

  completionChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 42, right: 20, top: 24, bottom: 60 },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: labels,
      axisLabel: { interval: 0, rotate: labels.length > 5 ? 25 : 0 }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: { formatter: '{value}%' }
    },
    series: [
      {
        name: '完成度',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        data: values,
        lineStyle: { color: '#4f7cff', width: 3 },
        itemStyle: { color: '#4f7cff' },
        areaStyle: { color: 'rgba(79,124,255,0.16)' },
        label: {
          show: true,
          position: 'top',
          formatter: ({ value }: { value: number }) => `${value}%`
        }
      }
    ]
  })
}

const renderRadarChart = () => {
  if (!radarChartRef.value) return
  if (!radarChart) radarChart = echarts.init(radarChartRef.value)

  const radar = learningStats.value.radar

  radarChart.setOption({
    legend: {
      top: 8,
      left: 'center',
      itemWidth: 18,
      itemHeight: 10,
      textStyle: { fontSize: 14 },
      data: ['综合得分', '问卷得分']
    },
    radar: {
      radius: 170,
      center: ['50%', '64%'],
      splitNumber: 5,
      indicator: [
        { name: '分析能力', max: 100 },
        { name: '开放\n思想', max: 100 },
        { name: '思维\n自信', max: 100 },
      ],
      axisName: { color: '#45556d', fontSize: 16, lineHeight: 20 },
      splitArea: { areaStyle: { color: ['#f8faff', '#f2f6ff'] } },
      splitLine: { lineStyle: { color: '#dbe5ff' } },
      axisLine: { lineStyle: { color: '#c9d8ff' } }
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: [radar.analysis_ability, radar.open_mind, radar.thinking_confidence],
            name: '综合得分',
            lineStyle: { color: '#6786ff', width: 2 },
            areaStyle: { color: 'rgba(103,134,255,0.22)' },
            symbolSize: 6,
          },
          {
            value: [
              radar.components.questionnaire_analysis,
              radar.components.questionnaire_open_mind,
              radar.components.questionnaire_thinking_confidence,
            ],
            name: '问卷得分',
            lineStyle: { color: '#ff8d4d', width: 2, type: 'dashed' },
            areaStyle: { color: 'rgba(255,141,77,0.18)' },
            symbolSize: 6,
          }
        ]
      }
    ]
  })
  radarChart.resize()
}

const renderThinkingCloudChart = () => {
  if (!thinkingCloudChartRef.value) return
  if (!thinkingCloudChart) thinkingCloudChart = echarts.init(thinkingCloudChartRef.value)

  const words = learningStats.value.thinking_cloud.words || []
  if (!words.length) {
    thinkingCloudChart.setOption({
      title: {
        text: '暂无可展示关键词（请先完成报告评测）',
        left: 'center',
        top: 'middle',
        textStyle: { color: '#94a3b8', fontSize: 14, fontWeight: 500 }
      },
      xAxis: { show: false, min: 0, max: 100 },
      yAxis: { show: false, min: 0, max: 100 },
      series: []
    })
    thinkingCloudChart.resize()
    return
  }

  const maxVal = Math.max(...words.map((x) => Number(x.value) || 0), 1)
  const palette = ['#4f7cff', '#7a5cff', '#14b8a6', '#f59e0b', '#ef4444', '#6366f1', '#06b6d4']
  const points = words.map((w, idx) => {
    const angle = (idx * 137.5 * Math.PI) / 180
    const r = 8 + (idx / Math.max(words.length, 1)) * 42
    const x = 50 + Math.cos(angle) * r
    const y = 50 + Math.sin(angle) * r * 0.72
    const size = 16 + (Number(w.value) / maxVal) * 22
    return {
      value: [x, y, Number(w.value)],
      name: w.name,
      symbolSize: size,
      itemStyle: { color: 'transparent' },
      label: {
        show: true,
        formatter: `${w.name}`,
        color: palette[idx % palette.length],
        fontSize: Math.round(size),
        fontWeight: Number(w.value) >= maxVal * 0.65 ? 'bold' : 'normal'
      }
    }
  })

  thinkingCloudChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => `${params.name}<br/>出现次数：${params.value?.[2] ?? 0}`
    },
    xAxis: { show: false, min: 0, max: 100 },
    yAxis: { show: false, min: 0, max: 100 },
    grid: { left: 0, right: 0, top: 0, bottom: 0 },
    series: [
      {
        type: 'scatter',
        data: points,
        emphasis: { scale: true }
      }
    ]
  })
  thinkingCloudChart.resize()
}

const fetchLearningStats = async () => {
  if (!currentClassId.value || currentRole !== 'teacher') {
    learningStats.value.completion_items = []
    learningStats.value.thinking_cloud = { words: [], source_report_count: 0 }
    return
  }
  learningLoading.value = true
  try {
    const res = await axios.get(`http://127.0.0.1:8000/teachers/${currentUserId}/classes/${currentClassId.value}/learning-stats`)
    learningStats.value = res.data
    await nextTick()
    renderCompletionChart()
    renderRadarChart()
    renderThinkingCloudChart()
  } finally {
    learningLoading.value = false
  }
}

const downloadLearningTemplate = async () => {
  if (!currentClassId.value || currentRole !== 'teacher') return
  const res = await axios.get(
    `http://127.0.0.1:8000/teachers/${currentUserId}/classes/${currentClassId.value}/learning-stats/template`,
    { responseType: 'blob' }
  )
  const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `class_${currentClassId.value}_learning_survey_template.xlsx`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

const uploadLearningSurvey = async (options: UploadRequestOptions) => {
  if (!currentClassId.value || currentRole !== 'teacher') return
  try {
    const formData = new FormData()
    formData.append('file', options.file)
    const res = await axios.post(
      `http://127.0.0.1:8000/teachers/${currentUserId}/classes/${currentClassId.value}/learning-stats/import`,
      formData
    )
    ElMessage.success(`导入完成：新增 ${res.data.created} 条，更新 ${res.data.updated} 条，跳过 ${res.data.skipped} 条`)
    options.onSuccess?.(res.data)
    await fetchLearningStats()
  } catch (e: any) {
    ElMessage.error(String(e?.response?.data?.detail || '问卷导入失败'))
    options.onError?.(e)
  }
}

const publishSemester = async () => {
  const { value } = await ElMessageBox.prompt('请输入学期名称（如 2026-秋）', '发布当前学期', {
    confirmButtonText: '发布',
    cancelButtonText: '取消'
  }).catch(() => ({ value: '' }))

  const name = String(value || '').trim()
  if (!name) return

  await axios.post('http://127.0.0.1:8000/admin/semesters/publish', { name })
  ElMessage.success('学期已发布')
  await fetchAll()
}

const createTeam = async () => {
  if (!currentClassId.value) return

  const { value } = await ElMessageBox.prompt('请输入队伍名称', '新增队伍', {
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).catch(() => ({ value: '' }))

  const name = String(value || '').trim()
  if (!name) return

  await axios.post(`http://127.0.0.1:8000/classes/${currentClassId.value}/teams`, { name })
  ElMessage.success('队伍已新增')
  await fetchTeams()
}

const removeTeam = async (teamId: number) => {
  await axios.delete(`http://127.0.0.1:8000/class-teams/${teamId}`)
  ElMessage.success('队伍已删除')
  await fetchTeams()
}

const updateTeamMembers = async (teamId: number, student_ids: number[]) => {
  await axios.put(`http://127.0.0.1:8000/class-teams/${teamId}/members`, { student_ids })
}

const onTeamMemberChange = async (teamId: number, val: unknown) => {
  const student_ids = Array.isArray(val)
    ? val.map((x) => Number(x)).filter((x) => !Number.isNaN(x))
    : []

  loadingTeams.value = true
  try {
    await updateTeamMembers(teamId, student_ids)
  } catch {
    ElMessage.error('更新组员失败')
  } finally {
    await fetchTeams()
  }
}

const openTransferDialog = () => {
  transferForm.value = { studentId: 0, targetTeamId: 0 }
  transferVisible.value = true
}

const transferMember = async () => {
  if (!currentClassId.value) return
  const { studentId, targetTeamId } = transferForm.value
  if (!studentId || !targetTeamId) return ElMessage.warning('请选择学生和目标队伍')

  await axios.post(`http://127.0.0.1:8000/classes/${currentClassId.value}/transfer-member`, {
    student_id: studentId,
    target_team_id: targetTeamId
  })

  transferVisible.value = false
  ElMessage.success('成员队伍已调整')
  await fetchTeams()
}
</script>

<style scoped>
.page-container { padding: 24px; background: #f8fafc; min-height: calc(100vh - 60px); }
.page-card { border-radius: 12px; }
.header-row { display: flex; justify-content: space-between; align-items: center; }
.title-row { display: flex; align-items: center; gap: 10px; }
.title { font-size: 18px; font-weight: 700; color: #1f2937; }
.sub-title { color: #64748b; margin-top: 4px; }
.toolbar { margin-bottom: 14px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.team-card { margin-bottom: 16px; }
.team-head { display: flex; justify-content: space-between; align-items: center; }
.member-tags { margin-top: 10px; display: flex; gap: 8px; flex-wrap: wrap; }
.score-grid { display: flex; flex-direction: column; gap: 8px; }
.score-row { display: flex; justify-content: space-between; align-items: center; }
.chart-card { border: 1px solid #eef2ff; border-radius: 10px; }
.cloud-card { margin-top: 16px; }
.cloud-header { display: flex; justify-content: space-between; align-items: center; }
.chart-box { width: 100%; height: 360px; }
.radar-chart-box { height: 560px; }
.cloud-chart-box { width: 100%; height: 360px; }
</style>
