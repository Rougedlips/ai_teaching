<template>
  <div class="group-manager-container">
    <el-card shadow="never" class="main-card" v-loading="loading">
      <template #header>
        <div class="header-content">
          <div class="title-area">
            <h3>综合项目申请管理</h3>
            <p>队伍管理 + 课题申请</p>
          </div>
          <el-button type="primary" plain @click="fetchAll">刷新</el-button>
        </div>
      </template>

      <el-alert v-if="entry.setting" :type="entry.setting.is_window_open ? 'success' : 'warning'" show-icon :closable="false" style="margin-bottom: 12px">
        <template #title>
          组队开关：{{ entry.setting.is_enabled ? '开启' : '关闭' }}；
          组队时段：{{ entry.setting.open_start || '-' }} ~ {{ entry.setting.open_end || '-' }}；
          人数限制：{{ entry.setting.min_team_size }} - {{ entry.setting.max_team_size }} 人；
          我的专业方向：{{ entry.student_major_direction || '-' }}

        </template>
      </el-alert>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="我的队伍" name="teams">
          <div class="toolbar"><el-button type="primary" @click="openCreateTeamDialog">新增队伍</el-button></div>
          <el-table :data="myTeams" stripe>
            <el-table-column prop="team_no" label="队伍编号" width="130" />
            <el-table-column prop="team_name" label="队伍名称" width="180" />
            <el-table-column prop="class_name" label="班级" width="170" />
            <el-table-column prop="direction" label="方向" width="140" />
            <el-table-column label="成员" min-width="300">
              <template #default="scope">
                <el-tag v-for="m in scope.row.members || []" :key="m.id" effect="plain" style="margin:0 6px 6px 0">
                  {{ m.real_name || m.username }}{{ m.student_no ? `（${m.student_no}）` : '' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="申请状态" width="110" />
            <el-table-column label="操作" width="180">
              <template #default="scope">
                <el-button link type="primary" :disabled="scope.row.leader_id !== studentId" @click="openMemberDialog(scope.row)">添加队员</el-button>
                <el-button link type="danger" :disabled="scope.row.leader_id !== studentId" @click="removeMemberPrompt(scope.row)">移除队员</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="申请课题" name="apply">
          <el-form label-width="120px" style="max-width: 780px">
            <el-form-item label="选择队伍">
              <el-select v-model="applyForm.team_id" style="width:100%" @change="onApplyTeamChange">
                <el-option
                  v-for="t in leaderTeams"
                  :key="t.id"
                  :label="`${t.team_no} ${t.team_name}`"
                  :value="t.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="可选课题">
              <el-select v-model="applyForm.topic_id" filterable style="width:100%">
                <el-option
                  v-for="t in availableTopics"
                  :key="t.id"
                  :label="`${t.title}（${t.teacher_name || '未设置老师'}）`"
                  :value="t.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="申请说明"><el-input v-model="applyForm.note" type="textarea" :rows="4" /></el-form-item>
            <el-form-item label="申请附件路径"><el-input v-model="applyForm.attachment_path" placeholder="可先通过 /project/upload 上传后粘贴路径" /></el-form-item>
            <el-form-item>
              <el-button type="primary" :disabled="!applyForm.team_id || !applyForm.topic_id" @click="submitApply">提交申请</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="createTeamDialogVisible" title="新增队伍" width="600px">
      <el-form label-width="100px">
        <el-form-item label="所属班级">
          <el-select v-model="createTeamForm.class_id" style="width:100%">
            <el-option v-for="c in entry.classes || []" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="队伍名称"><el-input v-model="createTeamForm.team_name" /></el-form-item>
        <el-form-item label="专业方向"><el-input v-model="createTeamForm.direction" disabled /></el-form-item>

      </el-form>
      <template #footer>
        <el-button @click="createTeamDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createTeam">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="memberDialogVisible" title="添加队员" width="680px">
      <el-form label-width="120px">
        <el-form-item label="搜索学生">
          <el-input v-model="memberSearch.keyword" placeholder="输入学号/姓名/账号" @keyup.enter="searchStudents" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchStudents">搜索</el-button>
        </el-form-item>
        <el-form-item label="搜索结果">
          <el-table :data="searchResults" style="width:100%" max-height="260">
            <el-table-column prop="student_no" label="学号" width="140" />
            <el-table-column prop="real_name" label="姓名" width="120" />
            <el-table-column prop="major_direction" label="专业方向" width="180" />
            <el-table-column prop="username" label="账号" min-width="120" />
            <el-table-column label="操作" width="100">

              <template #default="scope"><el-button link type="primary" @click="addMember(scope.row.id)">添加</el-button></template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const api = 'http://127.0.0.1:8000'
const studentId = Number(localStorage.getItem('user_id') || 0)

const loading = ref(false)
const activeTab = ref('teams')
const entry = reactive<any>({ setting: null, classes: [] })
const myTeams = ref<any[]>([])
const availableTopics = ref<any[]>([])

const createTeamDialogVisible = ref(false)
const createTeamForm = reactive({ class_id: 0, team_name: '', direction: '' })

const memberDialogVisible = ref(false)
const memberSearch = reactive({ team_id: 0, class_id: 0, keyword: '' })
const searchResults = ref<any[]>([])

const applyForm = reactive({ team_id: 0, topic_id: 0, note: '', attachment_path: '' })

const leaderTeams = computed(() => myTeams.value.filter(x => x.leader_id === studentId))

const fetchEntry = async () => {
  const res = await axios.get(`${api}/students/${studentId}/project/entry`)
  Object.assign(entry, res.data || { setting: null, classes: [] })
}
const fetchTeams = async () => {
  const res = await axios.get(`${api}/students/${studentId}/project/teams`)
  myTeams.value = res.data || []
}
const fetchAll = async () => {
  if (!studentId) return
  loading.value = true
  try {
    await Promise.all([fetchEntry(), fetchTeams()])
    if (!applyForm.team_id && leaderTeams.value.length) {
      applyForm.team_id = leaderTeams.value[0].id
      await onApplyTeamChange(applyForm.team_id)
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '综合项目申请数据加载失败')
  } finally {
    loading.value = false
  }
}
fetchAll()

const openCreateTeamDialog = () => {
  createTeamForm.class_id = entry.classes?.[0]?.id || 0
  createTeamForm.team_name = ''
  createTeamForm.direction = entry.student_major_direction || localStorage.getItem('major_direction') || ''
  createTeamDialogVisible.value = true
}


const createTeam = async () => {
  if (!createTeamForm.class_id) return ElMessage.warning('请选择所属班级')
  if (!createTeamForm.team_name.trim()) return ElMessage.warning('请输入队伍名称')
  if (!createTeamForm.direction.trim()) return ElMessage.warning('请输入专业方向')
  await axios.post(`${api}/students/${studentId}/project/teams`, createTeamForm)
  createTeamDialogVisible.value = false
  ElMessage.success('队伍创建成功')
  await fetchTeams()
}

const openMemberDialog = (row: any) => {
  memberSearch.team_id = row.id
  memberSearch.class_id = row.class_id
  memberSearch.keyword = ''
  searchResults.value = []
  memberDialogVisible.value = true
}

const searchStudents = async () => {
  if (!memberSearch.keyword.trim()) return ElMessage.warning('请输入搜索关键词')
  const res = await axios.get(`${api}/students/${studentId}/project/students/search`, {
    params: { class_id: memberSearch.class_id, keyword: memberSearch.keyword.trim() }
  })
  searchResults.value = res.data || []
}

const addMember = async (targetStudentId: number) => {
  await axios.post(`${api}/students/${studentId}/project/teams/${memberSearch.team_id}/members`, { student_id: targetStudentId })
  ElMessage.success('成员添加成功')
  await fetchTeams()
  memberDialogVisible.value = false
}

const removeMemberPrompt = async (row: any) => {
  const candidates = (row.members || []).filter((m: any) => m.id !== studentId)
  if (!candidates.length) return ElMessage.warning('暂无可移除成员')

  const options = candidates.map((x: any) => `${x.id}:${x.real_name || x.username}`).join('\n')
  const { value } = await ElMessageBox.prompt(`请输入要移除的成员ID：\n${options}`, '移除队员', {
    inputType: 'text',
    confirmButtonText: '确认',
    cancelButtonText: '取消',
  })
  const memberId = Number(value)
  if (!memberId) return

  await axios.delete(`${api}/students/${studentId}/project/teams/${row.id}/members/${memberId}`)
  ElMessage.success('成员已移除')
  await fetchTeams()
}

const onApplyTeamChange = async (teamId: number) => {
  if (!teamId) return
  const res = await axios.get(`${api}/students/${studentId}/project/topics/available`, { params: { team_id: teamId } })
  availableTopics.value = res.data || []
  applyForm.topic_id = availableTopics.value[0]?.id || 0
}

const submitApply = async () => {
  const formData = new FormData()
  formData.append('topic_id', String(applyForm.topic_id))
  formData.append('note', applyForm.note || '')
  formData.append('attachment_path', applyForm.attachment_path || '')
  await axios.post(`${api}/students/${studentId}/project/teams/${applyForm.team_id}/apply-topic`, formData)
  ElMessage.success('课题申请已提交')
  await fetchTeams()
}
</script>

<style scoped>
.group-manager-container { padding: 0; }
.main-card { border-radius: 10px; }
.header-content { display: flex; justify-content: space-between; align-items: center; }
.title-area h3 { margin: 0; color: #1e293b; }
.title-area p { margin: 4px 0 0; color: #64748b; font-size: 13px; }
.toolbar { margin-bottom: 10px; display: flex; gap: 8px; }
</style>
