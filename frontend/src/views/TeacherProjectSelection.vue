<template>
  <div class="page-container">
    <el-card shadow="never" class="main-card">
      <template #header>
        <div class="header-row">
          <div>
            <div class="title">综合项目选题管理</div>
            <div class="subtitle">教师题目管理 + 学生组队申请处理</div>
          </div>
          <el-button @click="fetchAll">刷新</el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="教师题目管理" name="topics">
          <div class="toolbar"><el-button type="primary" @click="openTopicDialog()">新增题目</el-button></div>
          <el-table :data="topics" stripe>
            <el-table-column prop="title" label="题目名称" min-width="220" />
            <el-table-column prop="direction" label="方向" width="140" />
            <el-table-column prop="materials" label="题目资料" min-width="220" show-overflow-tooltip />
            <el-table-column label="附件" width="120">
              <template #default="scope">
                <el-link v-if="scope.row.attachment_path" type="primary" :href="`http://127.0.0.1:8000/file/preview?path=${encodeURIComponent(scope.row.attachment_path)}`" target="_blank">查看</el-link>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="发布" width="90">
              <template #default="scope">
                <el-tag :type="scope.row.is_published ? 'success' : 'info'">{{ scope.row.is_published ? '是' : '否' }}</el-tag>
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

        <el-tab-pane label="学生组队申请列表" name="applications">
          <el-form inline class="filter-row">
            <el-form-item label="状态">
              <el-select v-model="statusFilter" clearable style="width: 180px" @change="fetchApplications">
                <el-option label="待审核" value="pending" />
                <el-option label="已通过" value="accepted" />
                <el-option label="已拒绝" value="rejected" />
              </el-select>
            </el-form-item>
          </el-form>
          <el-table :data="applications" stripe>
            <el-table-column prop="team_no" label="队伍编号" width="120" />
            <el-table-column prop="team_name" label="队伍名称" width="140" />
            <el-table-column prop="class_name" label="班级" width="160" />
            <el-table-column prop="direction" label="方向" width="120" />
            <el-table-column prop="topic_name" label="申请课题" min-width="200" />
            <el-table-column prop="apply_note" label="申请说明" min-width="220" show-overflow-tooltip />
            <el-table-column label="申请附件" width="120">
              <template #default="scope">
                <el-link v-if="scope.row.apply_attachment_path" type="primary" :href="`http://127.0.0.1:8000/file/preview?path=${encodeURIComponent(scope.row.apply_attachment_path)}`" target="_blank">查看</el-link>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="成员" min-width="220">
              <template #default="scope">
                <el-tag v-for="m in scope.row.members || []" :key="m.id" effect="plain" style="margin:0 6px 6px 0">
                  {{ m.real_name || m.username }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100" />
            <el-table-column label="操作" width="210">
              <template #default="scope">
                <el-button link type="success" :disabled="scope.row.status === 'accepted'" @click="reviewApplication(scope.row, 'accept')">接受</el-button>
                <el-button link type="danger" :disabled="scope.row.status === 'rejected'" @click="reviewApplication(scope.row, 'reject')">拒绝</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="topicDialogVisible" :title="topicForm.id ? '编辑题目' : '新增题目'" width="620px">
      <el-form label-width="100px">
        <el-form-item label="题目名称"><el-input v-model="topicForm.title" /></el-form-item>
        <el-form-item label="方向"><el-input v-model="topicForm.direction" /></el-form-item>
        <el-form-item label="题目资料"><el-input v-model="topicForm.materials" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="附件路径"><el-input v-model="topicForm.attachment_path" /></el-form-item>
        <el-form-item label="是否发布"><el-switch v-model="topicForm.is_published" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="topicDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTopic">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const api = 'http://127.0.0.1:8000'
const teacherId = Number(localStorage.getItem('user_id') || 0)

const activeTab = ref('topics')
const topics = ref<any[]>([])
const applications = ref<any[]>([])
const statusFilter = ref('pending')

const topicDialogVisible = ref(false)
const topicForm = reactive({ id: 0, title: '', direction: '', materials: '', attachment_path: '', is_published: false })

const fetchTopics = async () => {
  const res = await axios.get(`${api}/teachers/${teacherId}/project/topics`)
  topics.value = res.data || []
}

const fetchApplications = async () => {
  const res = await axios.get(`${api}/teachers/${teacherId}/project/applications`, {
    params: { status: statusFilter.value || undefined }
  })
  applications.value = res.data || []
}

const fetchAll = async () => {
  try {
    await Promise.all([fetchTopics(), fetchApplications()])
  } catch {
    ElMessage.error('综合项目选题管理数据加载失败')
  }
}
fetchAll()

const openTopicDialog = (row?: any) => {
  if (row) Object.assign(topicForm, row)
  else Object.assign(topicForm, { id: 0, title: '', direction: '', materials: '', attachment_path: '', is_published: false })
  topicDialogVisible.value = true
}

const saveTopic = async () => {
  if (!topicForm.title.trim()) return ElMessage.warning('请输入题目名称')
  if (!topicForm.direction.trim()) return ElMessage.warning('请输入方向')

  const payload = {
    title: topicForm.title,
    teacher_id: teacherId,
    direction: topicForm.direction,
    materials: topicForm.materials || null,
    attachment_path: topicForm.attachment_path || null,
    is_published: topicForm.is_published,
  }

  if (topicForm.id) await axios.put(`${api}/teachers/${teacherId}/project/topics/${topicForm.id}`, payload)
  else await axios.post(`${api}/teachers/${teacherId}/project/topics`, payload)

  topicDialogVisible.value = false
  ElMessage.success('题目保存成功')
  await fetchTopics()
}

const deleteTopic = async (id: number) => {
  await ElMessageBox.confirm('确认删除该题目吗？', '提示', { type: 'warning' })
  await axios.delete(`${api}/teachers/${teacherId}/project/topics/${id}`)
  ElMessage.success('删除成功')
  await fetchTopics()
}

const reviewApplication = async (row: any, action: 'accept' | 'reject') => {
  const { value } = await ElMessageBox.prompt(`请输入${action === 'accept' ? '接受' : '拒绝'}备注（可选）`, '审核申请', {
    inputType: 'textarea',
    confirmButtonText: '确认',
    cancelButtonText: '取消',
  })
  await axios.post(`${api}/teachers/${teacherId}/project/applications/${row.id}/${action}`, { comment: String(value || '').trim() || null })
  ElMessage.success(action === 'accept' ? '已接受申请' : '已拒绝申请')
  await fetchApplications()
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
