<template>
  <div class="student-assignments-page">
    <el-row :gutter="16">
      <el-col :span="14">
        <el-card shadow="never" class="panel-card">
          <template #header>
            <div class="panel-head">
              <div>
                <b>我的作业</b>
                <el-tag type="info" style="margin-left: 8px">{{ classInfo.class_name || '未选择班级' }}</el-tag>
                <el-tag v-if="classInfo.teacher_name" type="success" effect="plain" style="margin-left: 8px">任课老师：{{ classInfo.teacher_name }}</el-tag>
              </div>
              <el-button link type="primary" @click="loadAssignments">刷新</el-button>
            </div>
          </template>

          <el-table :data="assignmentList" v-loading="loading" stripe>
            <el-table-column prop="title" label="作业" min-width="160" show-overflow-tooltip />
            <el-table-column label="类型" width="100">
              <template #default="scope">
                <el-tag size="small" :type="scope.row.target_type === 'group' ? 'warning' : 'info'">
                  {{ scope.row.target_type === 'group' ? '小组' : '个人' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="scope">
                <el-tag :type="statusTagType(scope.row.status)">{{ scope.row.status_label }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="deadline" label="到期时间" width="170" />
            <el-table-column label="分数" width="90">
              <template #default="scope">{{ formatScore(scope.row.score) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button link type="primary" @click="openUpload(scope.row)">提交</el-button>
                <el-button link type="success" @click="openDetail(scope.row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="!loading && !assignmentList.length" description="当前班级暂无作业" :image-size="90" />
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card shadow="never" class="panel-card detail-card">
          <template #header>
            <div class="panel-head">
              <b>作业反馈详情</b>
              <el-tag v-if="selectedAssignment" :type="statusTagType(selectedAssignment.status)">{{ selectedAssignment.status_label }}</el-tag>
            </div>
          </template>

          <el-empty v-if="!selectedAssignment" description="请先在左侧选择作业" :image-size="90" />

          <template v-else>
            <h3 class="title">{{ selectedAssignment.title }}</h3>
            <p class="desc">{{ selectedAssignment.description || '暂无作业描述' }}</p>

            <div class="meta-row">
              <span>到期时间：{{ selectedAssignment.deadline || '-' }}</span>
              <span>分数：{{ formatScore(selectedAssignment.score) }}</span>
            </div>
            <div class="meta-row" v-if="selectedAssignment.target_type === 'group'">
              <span>发布方式：小组作业</span>
              <span>我的小组：{{ selectedAssignment.team_name || '未加入小组' }}</span>
            </div>

            <el-divider>模型评估维度（按评测提示词）</el-divider>
            <div class="criteria-tags">
              <el-tag v-for="item in promptDimensions" :key="item" effect="plain">{{ item }}</el-tag>
            </div>

            <el-divider>教师设定评测重点</el-divider>
            <el-empty
              v-if="!selectedAssignment.feedback?.ai_criteria"
              description="老师暂未填写本作业的评测重点"
              :image-size="70"
            />
            <ul v-else class="bullets">
              <li v-for="(line, idx) in splitLines(selectedAssignment.feedback.ai_criteria)" :key="`c-${idx}`">{{ line }}</li>
            </ul>

            <el-divider>模型最终评审回复（分区展示）</el-divider>
            <el-empty v-if="!feedbackRawText" description="暂无模型反馈" :image-size="70" />
            <template v-else>
              <div class="section-box" v-for="(block, idx) in feedbackBlocks" :key="`af-${idx}`">
                <div class="section-title">{{ block.title }}</div>
                <ul class="bullets">
                  <li v-for="(line, lineIdx) in block.items" :key="`af-${idx}-${lineIdx}`">{{ line }}</li>
                </ul>
              </div>
            </template>

            <el-divider>老师点评</el-divider>
            <p class="teacher-comment">{{ selectedAssignment.feedback?.teacher_comment || '暂无老师点评' }}</p>
          </template>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="uploadDialogVisible" title="提交作业压缩包" width="520px">
      <el-alert type="info" show-icon :closable="false" style="margin-bottom: 12px">
        <template #title>
          将上传到服务器目录 <b>codedoc/学号</b>，文件名为“学期_班级名_作业名.扩展名”
        </template>
      </el-alert>
      <div class="upload-target" v-if="uploadTarget">
        当前作业：{{ uploadTarget.title }}
      </div>
      <el-upload
        drag
        :auto-upload="false"
        :limit="1"
        :file-list="uploadFileList"
        :on-change="handleUploadFileChange"
        :on-remove="handleUploadFileRemove"
        accept=".zip,.rar,.7z,.tar,.gz,.bz2,.xz"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">拖拽文件到此处，或 <em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">支持 zip / rar / 7z / tar / gz / bz2 / xz</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="submitPackage">确认提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios'

interface Feedback {
  ai_criteria?: string | null
  ai_feedback?: string | null
  teacher_comment?: string | null
  score?: number | null
}

interface AssignmentItem {
  assignment_id: number
  title: string
  description: string
  deadline: string
  target_type?: 'individual' | 'group'
  team_name?: string | null
  status: 'unsubmitted' | 'submitted' | 'finished'
  status_label: string
  score: number | null
  submission_id: number | null
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
const assignmentList = ref<AssignmentItem[]>([])
const selectedAssignment = ref<AssignmentItem | null>(null)

const uploadDialogVisible = ref(false)
const uploadTarget = ref<AssignmentItem | null>(null)
const uploadFile = ref<File | null>(null)
const uploadFileList = ref<any[]>([])

const promptDimensions = computed(() => [
  '代码质量和规范性',
  'Top3 潜在 Bug/问题',
  '功能和性能优化空间',
  'AIGC 特征检测比率',
  '评分构成（功能/质量/原创性）',
  '可执行的改进建议'
])

const statusTagType = (status: string) => {
  if (status === 'finished') return 'success'
  if (status === 'submitted') return 'warning'
  return 'info'
}

const formatScore = (score: number | null | undefined) => (score === null || score === undefined ? '-' : score)

const splitLines = (text?: string | null) => {
  if (!text) return []
  return text
    .split(/\r?\n/)
    .map(x => x.trim().replace(/^[-•\d.)\s]+/, '').trim())
    .filter(Boolean)
}

const feedbackRawText = computed(() => selectedAssignment.value?.feedback?.ai_feedback || '')

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
    const first = rows[0] || ''
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
      title: `评测分区 ${idx + 1}`,
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
  router.replace(`/my-assignments/${cid}`)
}

const loadAssignments = async () => {
  const cid = activeClassId.value
  if (!studentId || !cid) {
    assignmentList.value = []
    selectedAssignment.value = null
    classInfo.value = {}
    return
  }

  loading.value = true
  try {
    const res = await axios.get(`http://127.0.0.1:8000/students/${studentId}/classes/${cid}/assignments`)
    classInfo.value = {
      class_id: res.data?.class_id,
      class_name: res.data?.class_name,
      teacher_name: res.data?.teacher_name
    }
    assignmentList.value = res.data?.assignments || []
    selectedAssignment.value = assignmentList.value[0] || null
  } catch (e: any) {
    assignmentList.value = []
    selectedAssignment.value = null
    ElMessage.error(e?.response?.data?.detail || '获取作业列表失败')
  } finally {
    loading.value = false
  }
}

const openDetail = (row: AssignmentItem) => {
  selectedAssignment.value = row
}

const openUpload = (row: AssignmentItem) => {
  if (row.target_type === 'group' && !row.team_name) {
    return ElMessage.warning('该任务为小组作业，请先在“我的组队”加入小组')
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

const submitPackage = async () => {
  if (!uploadTarget.value) {
    ElMessage.warning('请先选择作业')
    return
  }
  const cid = activeClassId.value
  if (!cid) {
    ElMessage.warning('未识别班级信息')
    return
  }
  if (!uploadFile.value) {
    ElMessage.warning('请先选择压缩包文件')
    return
  }

  const form = new FormData()
  form.append('file', uploadFile.value)

  uploading.value = true
  try {
    await axios.post(
      `http://127.0.0.1:8000/students/${studentId}/classes/${cid}/assignments/${uploadTarget.value.assignment_id}/submit`,
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
    ElMessage.success('提交成功')
    uploadDialogVisible.value = false
    await loadAssignments()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '提交失败')
  } finally {
    uploading.value = false
  }
}

watch(() => route.params.classId, loadAssignments)

onMounted(async () => {
  if (!studentId) {
    ElMessage.error('未获取到学生信息，请重新登录')
    return
  }

  await loadStudentClasses()
  ensureRouteClass()
  await loadAssignments()
})
</script>

<style scoped>
.student-assignments-page { padding: 8px; }
.panel-card { border-radius: 12px; min-height: 640px; }
.panel-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.detail-card { background: #fafbff; }
.title { margin: 0 0 8px 0; color: #1f2937; }
.desc { margin: 0; color: #475569; line-height: 1.6; }
.meta-row { margin-top: 12px; display: flex; justify-content: space-between; color: #334155; font-size: 13px; }
.criteria-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.bullets { margin: 0; padding-left: 18px; color: #334155; line-height: 1.8; }
.section-box {
  background: #ffffff;
  border: 1px solid #e8edf8;
  border-radius: 10px;
  padding: 10px 12px;
  margin-bottom: 10px;
}
.section-title { font-weight: 700; color: #1e293b; margin-bottom: 8px; }
.upload-target { margin-bottom: 10px; color: #334155; font-weight: 600; }
.teacher-comment {
  margin: 0;
  padding: 10px 12px;
  border-radius: 8px;
  background: #eef5ff;
  color: #1e3a8a;
  line-height: 1.7;
}
</style>
