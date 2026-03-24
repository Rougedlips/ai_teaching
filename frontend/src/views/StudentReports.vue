<template>
  <div class="student-reports-page">
    <el-card shadow="never" class="panel-card">
      <template #header>
        <div class="panel-head">
          <div>
            <b>我的报告</b>
            <el-tag type="info" style="margin-left: 8px">{{ classInfo.class_name || '未选择班级' }}</el-tag>
            <el-tag v-if="classInfo.teacher_name" type="success" effect="plain" style="margin-left: 8px">任课老师：{{ classInfo.teacher_name }}</el-tag>
          </div>
          <el-button link type="primary" @click="loadReportTasks">刷新</el-button>
        </div>
      </template>

      <el-table :data="reportTaskList" v-loading="loading" stripe>
        <el-table-column prop="title" label="报告任务" min-width="180" show-overflow-tooltip />
        <el-table-column label="类型" width="100">
          <template #default="scope">
            <el-tag size="small" :type="scope.row.target_type === 'group' ? 'warning' : 'info'">
              {{ scope.row.target_type === 'group' ? '小组' : '个人' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="scope">
            <el-tag :type="statusTagType(scope.row.status)">{{ scope.row.status_label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="deadline" label="截止时间" width="180" />
        <el-table-column label="分数" width="90">
          <template #default="scope">{{ formatScore(scope.row.score) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220">
          <template #default="scope">
            <el-button
              v-if="canUploadReport(scope.row)"
              link
              type="primary"
              @click="openUpload(scope.row)"
            >{{ uploadActionText(scope.row) }}</el-button>
            <el-button link type="success" @click="openDetail(scope.row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && !reportTaskList.length" description="当前班级暂无报告任务" :image-size="90" />
    </el-card>

    <el-card shadow="never" class="panel-card detail-card" style="margin-top: 16px;">
      <template #header>
        <div class="panel-head">
          <b>报告反馈详情</b>
          <el-tag v-if="selectedTask" :type="statusTagType(selectedTask.status)">{{ selectedTask.status_label }}</el-tag>
        </div>
      </template>

      <el-empty v-if="!selectedTask" description="请先在上方选择任务" :image-size="90" />
      <template v-else>
        <h3 class="title">{{ selectedTask.title }}</h3>
        <p class="desc">{{ selectedTask.description || '暂无任务描述' }}</p>
        <div class="meta-row">
          <span>截止时间：{{ selectedTask.deadline || '-' }}</span>
          <span>分数：{{ formatScore(selectedTask.score) }}</span>
        </div>
        <div class="meta-row" v-if="selectedTask.target_type === 'group'">
          <span>发布方式：小组报告</span>
          <span>我的小组：{{ selectedTask.team_name || '未加入小组' }}</span>
        </div>
        <el-divider>AI 反馈</el-divider>
        <el-empty v-if="!feedbackRawText" description="暂无 AI 反馈" :image-size="70" />
        <template v-else>
          <div class="section-box" v-for="(block, idx) in feedbackBlocks" :key="`fb-${idx}`">
            <div class="section-title">{{ block.title }}</div>
            <ul class="bullets">
              <li v-for="(line, lineIdx) in block.items" :key="`fb-${idx}-${lineIdx}`">{{ line }}</li>
            </ul>
          </div>
        </template>
        <el-divider>老师点评</el-divider>
        <p class="feedback">{{ selectedTask.feedback?.teacher_comment || '暂无老师点评' }}</p>
      </template>
    </el-card>

    <el-dialog v-model="uploadDialogVisible" title="提交报告文件" width="520px">
      <el-alert type="info" show-icon :closable="false" style="margin-bottom: 12px">
        <template #title>
          将上传到服务器目录 <b>document/学号</b>，并重命名为“班级_姓名_报告任务名称.扩展名”
        </template>
      </el-alert>
      <div class="upload-target" v-if="uploadTarget">
        当前任务：{{ uploadTarget.title }}
      </div>
      <el-upload
        drag
        :auto-upload="false"
        :limit="1"
        :file-list="uploadFileList"
        :on-change="handleUploadFileChange"
        :on-remove="handleUploadFileRemove"
        accept=".doc,.docx,.pdf"
      >
        <div class="el-upload__text">拖拽文件到此处，或 <em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">仅支持 doc / docx / pdf</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="submitReport">确认提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

interface Feedback {
  ai_feedback?: string | null
  teacher_comment?: string | null
  score?: number | null
}

interface ReportTaskItem {
  report_task_id: number
  title: string
  description: string
  deadline: string
  target_type?: 'individual' | 'group'
  team_name?: string | null
  status: 'unsubmitted' | 'submitted' | 'finished' | 'returned'
  status_label: string
  score: number | null
  submission_id: number | null
  saved_path?: string | null
  feedback: Feedback
}

interface ClassItem {
  id: number
  name: string
}

const route = useRoute()
const router = useRouter()
const studentId = Number(localStorage.getItem('user_id') || 0)

const loading = ref(false)
const uploading = ref(false)
const classList = ref<ClassItem[]>([])
const classInfo = ref<{ class_id?: number; class_name?: string; teacher_name?: string }>({})
const reportTaskList = ref<ReportTaskItem[]>([])
const selectedTask = ref<ReportTaskItem | null>(null)

const uploadDialogVisible = ref(false)
const uploadTarget = ref<ReportTaskItem | null>(null)
const uploadFile = ref<File | null>(null)
const uploadFileList = ref<any[]>([])

const statusTagType = (status: string) => {
  if (status === 'finished') return 'success'
  if (status === 'submitted') return 'warning'
  if (status === 'returned') return 'danger'
  return 'info'
}

const formatScore = (score: number | null | undefined) => (score === null || score === undefined ? '-' : score)

const canUploadReport = (row: ReportTaskItem) => row.status !== 'finished'

const uploadActionText = (row: ReportTaskItem) => {
  if (row.status === 'submitted') return '更新报告'
  if (row.status === 'returned') return '重新提交'
  return '提交报告'
}

const splitFeedbackItems = (text?: string | null) => {
  const raw = String(text || '').trim()
  if (!raw) return []

  const lineBased = raw
    .split(/\r?\n/)
    .map(x => x.trim().replace(/^[-•\d.)\s]+/, '').trim())
    .filter(Boolean)
  if (lineBased.length > 1) return lineBased

  return raw
    .split(/(?<=[。！？；;])\s*/)
    .map(x => x.trim().replace(/^[-•\d.)\s]+/, '').trim())
    .filter(Boolean)
}

const feedbackRawText = computed(() => selectedTask.value?.feedback?.ai_feedback || '')

const feedbackBlocks = computed(() => {
  const text = feedbackRawText.value
  if (!text) return []

  const chunks = text
    .replace(/\r/g, '\n')
    .split(/\n\s*\n+/)
    .map(x => x.trim())
    .filter(Boolean)

  const source = chunks.length ? chunks : [text]

  return source.map((chunk, idx) => {
    const rows = chunk.split(/\n/).map(x => x.trim()).filter(Boolean)
    if (!rows.length) {
      return {
        title: `反馈要点 ${idx + 1}`,
        items: ['暂无内容']
      }
    }

    const first = rows[0]
    const rest = rows.slice(1).join('\n')
    const hasTitle = rows.length > 1 && /[：:]$/.test(first)
    if (hasTitle) {
      const items = splitFeedbackItems(rest)
      return {
        title: first.replace(/[：:]$/, ''),
        items: items.length ? items : ['暂无内容']
      }
    }

    const items = splitFeedbackItems(chunk)
    return {
      title: `反馈要点 ${idx + 1}`,
      items: items.length ? items : ['暂无内容']
    }
  })
})

const loadStudentClasses = async () => {
  const res = await axios.get(`http://127.0.0.1:8000/students/${studentId}/classes/current`)
  classList.value = res.data || []
}

const activeClassId = computed(() => {
  const raw = Number(route.params.classId)
  if (raw) return raw
  return classList.value[0]?.id
})

const ensureRouteClass = () => {
  const cid = activeClassId.value
  if (!cid) return
  if (route.params.classId && Number(route.params.classId) === cid) return
  router.replace(`/my-reports/${cid}`)
}

const loadReportTasks = async () => {
  const cid = activeClassId.value
  if (!studentId || !cid) {
    reportTaskList.value = []
    selectedTask.value = null
    classInfo.value = {}
    return
  }

  loading.value = true
  try {
    const res = await axios.get(`http://127.0.0.1:8000/students/${studentId}/classes/${cid}/report-tasks`)
    classInfo.value = {
      class_id: res.data?.class_id,
      class_name: res.data?.class_name,
      teacher_name: res.data?.teacher_name
    }
    reportTaskList.value = res.data?.report_tasks || []
    selectedTask.value = reportTaskList.value[0] || null
  } catch (e: any) {
    reportTaskList.value = []
    selectedTask.value = null
    ElMessage.error(e?.response?.data?.detail || '获取报告任务失败')
  } finally {
    loading.value = false
  }
}

const openDetail = (row: ReportTaskItem) => {
  selectedTask.value = row
}

const openUpload = (row: ReportTaskItem) => {
  if (!canUploadReport(row)) {
    return ElMessage.warning('该报告已完成批改，如需修改请联系老师先退回')
  }
  if (row.target_type === 'group' && !row.team_name) {
    return ElMessage.warning('该任务为小组报告，请先在“我的组队”加入小组')
  }
  uploadTarget.value = row
  uploadFile.value = null
  uploadFileList.value = []
  uploadDialogVisible.value = true
}

const handleUploadFileChange = (file: any) => {
  uploadFile.value = file?.raw || null
  uploadFileList.value = file ? [file] : []
}

const handleUploadFileRemove = () => {
  uploadFile.value = null
  uploadFileList.value = []
}

const submitReport = async () => {
  if (!uploadTarget.value) return ElMessage.warning('请先选择报告任务')
  const cid = activeClassId.value
  if (!cid) return ElMessage.warning('未识别班级信息')
  if (!uploadFile.value) return ElMessage.warning('请先选择报告文件')

  const form = new FormData()
  form.append('file', uploadFile.value)

  uploading.value = true
  try {
    await axios.post(
      `http://127.0.0.1:8000/students/${studentId}/classes/${cid}/report-tasks/${uploadTarget.value.report_task_id}/submit`,
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
    ElMessage.success('报告提交成功')
    uploadDialogVisible.value = false
    await loadReportTasks()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '报告提交失败')
  } finally {
    uploading.value = false
  }
}

watch(() => route.params.classId, loadReportTasks)

onMounted(async () => {
  if (!studentId) {
    ElMessage.error('未获取到学生信息，请重新登录')
    return
  }

  await loadStudentClasses()
  ensureRouteClass()
  await loadReportTasks()
})
</script>

<style scoped>
.student-reports-page { padding: 8px; }
.panel-card { border-radius: 12px; }
.panel-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.detail-card { background: #fafbff; }
.title { margin: 0 0 8px 0; color: #1f2937; }
.desc { margin: 0; color: #475569; line-height: 1.6; }
.meta-row { margin-top: 12px; display: flex; justify-content: space-between; color: #334155; font-size: 13px; }
.section-box {
  background: #ffffff;
  border: 1px solid #e8edf8;
  border-radius: 10px;
  padding: 10px 12px;
  margin-bottom: 10px;
}
.section-title { font-weight: 700; color: #1e293b; margin-bottom: 8px; }
.bullets { margin: 0; padding-left: 18px; color: #334155; line-height: 1.8; }
.feedback {
  margin: 0;
  padding: 10px 12px;
  border-radius: 8px;
  background: #eef5ff;
  color: #1e3a8a;
  line-height: 1.7;
}
.upload-target { margin-bottom: 10px; color: #334155; font-weight: 600; }
</style>
