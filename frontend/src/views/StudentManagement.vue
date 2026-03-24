<template>
  <div class="page-container">
    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="header-row">
          <div>
            <div class="title-row">
              <div class="title">👨‍🎓 学生管理</div>
              <el-button
                v-if="currentClassId"
                type="primary"
                plain
                size="small"
                @click="openClassAnalytics"
              >
                学情统计
              </el-button>
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
        </el-tabs>
      </template>
    </el-card>

    <el-dialog v-model="rankingVisible" title="班级学情统计" width="560px">
      <el-table :data="rankingRows" stripe v-loading="rankingLoading">
        <el-table-column type="index" label="排名" width="70" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="count" label="已批改次数" width="110" />
        <el-table-column prop="score" label="平均分" width="100" />
      </el-table>
    </el-dialog>

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
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
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
interface RankingItem { name: string; count: number; score: number }

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
const transferVisible = ref(false)
const transferForm = ref({ studentId: 0, targetTeamId: 0 })
const rankingVisible = ref(false)
const rankingLoading = ref(false)
const rankingRows = ref<RankingItem[]>([])

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
      return
    }

    const [overviewRes, teamsRes] = await Promise.all([
      axios.get(`http://127.0.0.1:8000/classes/${currentClassId.value}/overview`),
      axios.get(`http://127.0.0.1:8000/classes/${currentClassId.value}/teams`)
    ])
    assignments.value = overviewRes.data.assignments || []
    students.value = overviewRes.data.students || []
    teams.value = teamsRes.data || []
  } catch {
    assignments.value = []
    students.value = []
    teams.value = []
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

const getScore = (student: StudentItem, assignmentId: number) => {
  const v = student.scores[String(assignmentId)]
  return v == null ? '-' : v
}

const getStudentName = (studentId: number) => {
  const s = students.value.find((x) => x.id === studentId)
  return s ? s.name : `学生${studentId}`
}

const openClassAnalytics = async () => {
  if (!currentClassId.value) return
  rankingVisible.value = true
  rankingLoading.value = true

  try {
    const res = await axios.get(`http://127.0.0.1:8000/classes/${currentClassId.value}/analytics/student_ranking`)
    rankingRows.value = res.data || []
  } finally {
    rankingLoading.value = false
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
.toolbar { margin-bottom: 14px; display: flex; gap: 10px; }
.team-card { margin-bottom: 16px; }
.team-head { display: flex; justify-content: space-between; align-items: center; }
.member-tags { margin-top: 10px; display: flex; gap: 8px; flex-wrap: wrap; }
.score-grid { display: flex; flex-direction: column; gap: 8px; }
.score-row { display: flex; justify-content: space-between; align-items: center; }
</style>
