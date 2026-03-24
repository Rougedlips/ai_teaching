<template>
  <div class="page-container">
    <el-card shadow="never" class="main-card">
      <template #header>
        <div class="header-row">
          <div>
            <div class="title">综合项目管理</div>
            <div class="subtitle">课题库、组队、申请设置、班级课题配置</div>
          </div>
          <el-button @click="fetchAll">刷新</el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="课题库管理" name="topics">
          <div class="toolbar">
            <el-button type="primary" @click="openTopicDialog()">新增课题</el-button>
            <el-input v-model="topicKeyword" placeholder="按课题名称搜索" clearable style="width: 240px" @change="fetchTopics" />
          </div>
          <el-table :data="topics" stripe>
            <el-table-column prop="title" label="课题名称" min-width="220" />
            <el-table-column prop="teacher_name" label="指导老师" width="140" />
            <el-table-column prop="direction" label="开设方向" width="140" />
            <el-table-column prop="materials" label="课题资料" min-width="200" show-overflow-tooltip />
            <el-table-column label="课题附件" width="140">
              <template #default="scope">
                <el-link v-if="scope.row.attachment_path" type="primary" :href="`http://127.0.0.1:8000/file/preview?path=${encodeURIComponent(scope.row.attachment_path)}`" target="_blank">查看</el-link>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="是否发布" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.is_published ? 'success' : 'info'">{{ scope.row.is_published ? '已发布' : '未发布' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160">
              <template #default="scope">
                <el-button link type="primary" @click="openTopicDialog(scope.row)">编辑</el-button>
                <el-button link type="danger" @click="deleteTopic(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="历学期组队情况" name="teams">
          <el-form inline class="filter-row">
            <el-form-item label="学期">
              <el-select v-model="teamFilters.semester_id" clearable style="width:180px">
                <el-option v-for="s in semesters" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="方向"><el-input v-model="teamFilters.direction" clearable /></el-form-item>
            <el-form-item label="课题"><el-input v-model="teamFilters.topic_keyword" clearable /></el-form-item>
            <el-form-item label="老师"><el-input v-model="teamFilters.teacher_keyword" clearable /></el-form-item>
            <el-form-item label="队伍"><el-input v-model="teamFilters.team_keyword" clearable /></el-form-item>
            <el-form-item><el-button type="primary" @click="fetchTeams">筛选</el-button></el-form-item>
          </el-form>
          <div class="toolbar"><el-button type="primary" @click="openTeamDialog()">新增队伍</el-button></div>
          <el-table :data="teams" stripe>
            <el-table-column prop="team_no" label="队伍编号" width="120" />
            <el-table-column prop="direction" label="课程方向" width="140" />
            <el-table-column prop="topic_name" label="课题名称" min-width="220" />
            <el-table-column prop="advisor_teacher_name" label="指导老师" width="140" />
            <el-table-column label="队伍成员" min-width="260">
              <template #default="scope">
                <el-tag v-for="m in scope.row.members || []" :key="m.id" effect="plain" style="margin:0 6px 6px 0">
                  {{ m.real_name || m.username }}{{ m.student_no ? `（${m.student_no}）` : '' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160">
              <template #default="scope">
                <el-button link type="primary" @click="openTeamDialog(scope.row)">编辑</el-button>
                <el-button link type="danger" @click="deleteTeam(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="综设申请设置" name="settings">
          <el-form label-width="170px" style="max-width: 640px">
            <el-form-item label="综设组队是否开启"><el-switch v-model="settings.is_enabled" /></el-form-item>
            <el-form-item label="开启时间段">
              <el-date-picker v-model="settingRange" type="daterange" value-format="YYYY-MM-DD" style="width:100%" />
            </el-form-item>
            <el-form-item label="队伍人数下限"><el-input-number v-model="settings.min_team_size" :min="1" /></el-form-item>
            <el-form-item label="队伍人数上限"><el-input-number v-model="settings.max_team_size" :min="1" /></el-form-item>
            <el-form-item><el-button type="primary" @click="saveSettings">保存设置</el-button></el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="班级课题设置" name="class-topics">
          <el-table :data="classTopicRows" stripe>
            <el-table-column prop="class_name" label="教学班" width="220" />
            <el-table-column label="已配置课题" min-width="420">
              <template #default="scope">
                <el-select
                  v-model="scope.row.topic_ids"
                  multiple
                  filterable
                  style="width:100%"
                  placeholder="请选择课题"
                  @change="saveClassTopics(scope.row)"
                >
                  <el-option
                    v-for="t in topics"
                    :key="t.id"
                    :label="`${t.title}（${t.direction}）`"
                    :value="t.id"
                  />
                </el-select>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="topicDialogVisible" :title="topicForm.id ? '编辑课题' : '新增课题'" width="620px">
      <el-form label-width="100px">
        <el-form-item label="课题名称"><el-input v-model="topicForm.title" /></el-form-item>
        <el-form-item label="指导老师">
          <el-select v-model="topicForm.teacher_id" style="width:100%">
            <el-option v-for="t in teachers" :key="t.id" :label="t.real_name || t.username" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="开设方向"><el-input v-model="topicForm.direction" /></el-form-item>
        <el-form-item label="课题资料"><el-input v-model="topicForm.materials" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="附件路径"><el-input v-model="topicForm.attachment_path" placeholder="可先通过 /project/upload 上传后粘贴路径" /></el-form-item>
        <el-form-item label="是否发布"><el-switch v-model="topicForm.is_published" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="topicDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTopic">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="teamDialogVisible" :title="teamForm.id ? '编辑队伍' : '新增队伍'" width="680px">
      <el-form label-width="100px">
        <el-form-item label="所属班级">
          <el-select v-model="teamForm.class_id" style="width:100%" :disabled="!!teamForm.id" @change="onTeamClassChange">
            <el-option v-for="c in allClasses" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="队伍名称"><el-input v-model="teamForm.team_name" /></el-form-item>
        <el-form-item label="课程方向"><el-input v-model="teamForm.direction" /></el-form-item>
        <el-form-item label="队长" v-if="!teamForm.id">
          <el-select v-model="teamForm.leader_id" filterable style="width:100%">
            <el-option v-for="s in classStudents" :key="s.id" :label="`${s.real_name || s.username}（${s.student_no || s.id}）`" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="队员">
          <el-select v-model="teamForm.member_ids" multiple filterable style="width:100%">
            <el-option v-for="s in classStudents" :key="s.id" :label="`${s.real_name || s.username}（${s.student_no || s.id}）`" :value="s.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="teamDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTeam">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const api = 'http://127.0.0.1:8000'
const activeTab = ref('topics')

const semesters = ref<any[]>([])
const teachers = ref<any[]>([])
const topics = ref<any[]>([])
const teams = ref<any[]>([])
const allClasses = ref<any[]>([])
const classTopicRows = ref<any[]>([])
const classStudents = ref<any[]>([])

const topicKeyword = ref('')
const teamFilters = reactive({ semester_id: undefined as number | undefined, direction: '', topic_keyword: '', teacher_keyword: '', team_keyword: '' })

const settings = reactive({ is_enabled: false, open_start: '', open_end: '', min_team_size: 2, max_team_size: 6 })
const settingRange = ref<string[]>([])

const topicDialogVisible = ref(false)
const teamDialogVisible = ref(false)

const topicForm = reactive({ id: 0, title: '', teacher_id: 0, materials: '', attachment_path: '', direction: '', is_published: false })
const teamForm = reactive({ id: 0, class_id: 0, team_name: '', direction: '', leader_id: 0, member_ids: [] as number[] })

const fetchSemesters = async () => {
  const res = await axios.get(`${api}/semesters`)
  semesters.value = res.data || []
}
const fetchTeachers = async () => {
  const res = await axios.get(`${api}/admin/teachers`)
  teachers.value = res.data || []
}
const fetchClasses = async () => {
  const res = await axios.get(`${api}/admin/classes/manage`)
  allClasses.value = res.data || []
}

const fetchTopics = async () => {
  const res = await axios.get(`${api}/admin/project/topics`, { params: { keyword: topicKeyword.value || undefined } })
  topics.value = res.data || []
}

const fetchTeams = async () => {
  const res = await axios.get(`${api}/admin/project/teams`, { params: { ...teamFilters } })
  teams.value = res.data || []
}

const fetchSettings = async () => {
  const res = await axios.get(`${api}/admin/project/settings/current`)
  Object.assign(settings, res.data || {})
  settingRange.value = [settings.open_start, settings.open_end].filter(Boolean)
}

const fetchClassTopicConfigs = async () => {
  const res = await axios.get(`${api}/admin/project/class-topic-configs`)
  classTopicRows.value = res.data || []
}

const fetchAll = async () => {
  try {
    await Promise.all([fetchSemesters(), fetchTeachers(), fetchClasses(), fetchTopics(), fetchTeams(), fetchSettings(), fetchClassTopicConfigs()])
  } catch {
    ElMessage.error('综合项目管理数据加载失败')
  }
}
fetchAll()

const saveSettings = async () => {
  settings.open_start = settingRange.value?.[0] || ''
  settings.open_end = settingRange.value?.[1] || ''
  await axios.put(`${api}/admin/project/settings/current`, settings)
  ElMessage.success('设置已保存')
}

const openTopicDialog = (row?: any) => {
  if (row) Object.assign(topicForm, row)
  else Object.assign(topicForm, { id: 0, title: '', teacher_id: teachers.value[0]?.id || 0, materials: '', attachment_path: '', direction: '', is_published: false })
  topicDialogVisible.value = true
}

const saveTopic = async () => {
  if (!topicForm.title.trim()) return ElMessage.warning('请输入课题名称')
  if (!topicForm.teacher_id) return ElMessage.warning('请选择指导老师')
  if (!topicForm.direction.trim()) return ElMessage.warning('请输入开设方向')

  const payload = {
    title: topicForm.title,
    teacher_id: topicForm.teacher_id,
    materials: topicForm.materials || null,
    attachment_path: topicForm.attachment_path || null,
    direction: topicForm.direction,
    is_published: topicForm.is_published,
  }
  if (topicForm.id) await axios.put(`${api}/admin/project/topics/${topicForm.id}`, payload)
  else await axios.post(`${api}/admin/project/topics`, payload)

  topicDialogVisible.value = false
  ElMessage.success('课题保存成功')
  await Promise.all([fetchTopics(), fetchClassTopicConfigs()])
}

const deleteTopic = async (id: number) => {
  await ElMessageBox.confirm('确认删除该课题吗？', '提示', { type: 'warning' })
  await axios.delete(`${api}/admin/project/topics/${id}`)
  ElMessage.success('删除成功')
  await Promise.all([fetchTopics(), fetchClassTopicConfigs()])
}

const saveClassTopics = async (row: any) => {
  await axios.put(`${api}/admin/project/classes/${row.class_id}/topics`, { topic_ids: row.topic_ids || [] })
  ElMessage.success(`已更新 ${row.class_name} 的课题配置`)
}

const onTeamClassChange = (classId: number) => {
  const cls = allClasses.value.find((x: any) => x.id === classId)
  classStudents.value = cls?.students || []
  teamForm.member_ids = []
  teamForm.leader_id = 0
}

const openTeamDialog = (row?: any) => {
  if (row) {
    teamForm.id = row.id
    teamForm.class_id = row.class_id
    teamForm.team_name = row.team_name
    teamForm.direction = row.direction
    teamForm.leader_id = row.leader_id
    teamForm.member_ids = (row.members || []).map((m: any) => m.id)
  } else {
    Object.assign(teamForm, { id: 0, class_id: allClasses.value[0]?.id || 0, team_name: '', direction: '', leader_id: 0, member_ids: [] })
  }
  onTeamClassChange(teamForm.class_id)
  teamDialogVisible.value = true
}

const saveTeam = async () => {
  if (!teamForm.class_id) return ElMessage.warning('请选择所属班级')
  if (!teamForm.team_name.trim()) return ElMessage.warning('请输入队伍名称')
  if (!teamForm.direction.trim()) return ElMessage.warning('请输入课程方向')

  if (teamForm.id) {
    await axios.put(`${api}/admin/project/teams/${teamForm.id}`, {
      team_name: teamForm.team_name,
      direction: teamForm.direction,
      member_ids: teamForm.member_ids,
    })
  } else {
    if (!teamForm.leader_id) return ElMessage.warning('请选择队长')
    await axios.post(`${api}/admin/project/teams`, {
      class_id: teamForm.class_id,
      team_name: teamForm.team_name,
      direction: teamForm.direction,
      leader_id: teamForm.leader_id,
      member_ids: teamForm.member_ids,
    })
  }
  teamDialogVisible.value = false
  ElMessage.success('队伍保存成功')
  await fetchTeams()
}

const deleteTeam = async (id: number) => {
  await ElMessageBox.confirm('确认删除该队伍吗？', '提示', { type: 'warning' })
  await axios.delete(`${api}/admin/project/teams/${id}`)
  ElMessage.success('删除成功')
  await fetchTeams()
}
</script>

<style scoped>
.page-container { padding: 0; }
.main-card { border-radius: 10px; }
.header-row { display: flex; justify-content: space-between; align-items: center; }
.title { font-size: 18px; font-weight: 700; color: #28334a; }
.subtitle { margin-top: 4px; color: #8590a6; font-size: 12px; }
.toolbar { display: flex; gap: 10px; margin-bottom: 12px; }
.filter-row { margin-bottom: 10px; background: #f7f9ff; padding: 10px 10px 0; border-radius: 8px; }
</style>
