<template>
  <div class="page-container">
    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="header-row">
          <div>
            <div class="title">📝 作业管理</div>
            <div class="sub-title" v-if="classMeta">当前班级：{{ classMeta.name }}</div>
          </div>
          <el-button type="primary" @click="openPublishDialog" :disabled="!classMeta">发布新作业任务</el-button>
        </div>
      </template>

      <el-empty v-if="!classMeta" description="当前学期暂无可管理班级" />

      <template v-else>
        <div class="task-plaza">
          <h3>已发布作业（{{ classMeta.name }}）</h3>
          <el-row :gutter="16" v-loading="loading">
            <el-col :span="8" v-for="item in assignments" :key="item.id" style="margin-bottom:16px">
              <el-card shadow="hover" class="task-card">
                <div class="task-head">
                  <div class="task-id">Assignment #{{ item.id }}</div>
                  <el-tag size="small" :type="item.target_type === 'group' ? 'warning' : 'info'">
                    {{ item.target_type === 'group' ? '小组作业' : '个人作业' }}
                  </el-tag>
                </div>
                <h4 class="task-title">{{ item.title }}</h4>
                <p class="task-desc">{{ item.description || '暂无描述' }}</p>

                <div class="stat-row">
                  <el-tag type="warning">待批改：{{ item.pending_review_count }}</el-tag>
                  <el-tag type="danger">未提交：{{ item.unsubmitted_count }}/{{ item.unit_total || item.student_total || 0 }}</el-tag>
                </div>

                <div class="deadline">截止：{{ (item.deadline || '').split(' ')[0] || '长期' }}</div>
                <div class="action-spacer"></div>

                <div class="card-actions">
                  <el-button type="primary" size="small" @click="openEditDialog(item)">修改</el-button>
                  <el-button type="warning" size="small" @click="openReviewDialog(item)">进入批改后台</el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </template>
    </el-card>

    <el-dialog v-model="publishDialogVisible" title="发布新作业任务" width="620px">
      <el-form :model="publishForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="14">
            <el-form-item label="作业标题">
              <el-input v-model="publishForm.title" />
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="截止日期">
              <el-date-picker v-model="publishForm.deadline" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="详细描述">
          <el-input v-model="publishForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="发布方式">
          <el-radio-group v-model="publishForm.target_type">
            <el-radio label="individual">个人作业</el-radio>
            <el-radio label="group">小组作业</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="本次作业 AI 评测重点（可逐条添加）">
          <div class="criteria-editor">
            <div v-for="(_, idx) in publishForm.aiCriteriaItems" :key="`p-${idx}`" class="criteria-row">
              <el-input v-model="publishForm.aiCriteriaItems[idx]" :placeholder="`评测重点 ${idx + 1}`" />
              <el-button type="danger" plain @click="removeCriteriaItem('publish', idx)">删除</el-button>
            </div>
            <el-button type="primary" plain @click="addCriteriaItem('publish')">+ 添加评测重点</el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="publishDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="publishAssignment">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editDialogVisible" title="修改作业" width="620px">
      <el-form :model="editForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="14">
            <el-form-item label="作业标题">
              <el-input v-model="editForm.title" />
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="截止日期">
              <el-date-picker v-model="editForm.deadline" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="详细描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="本次作业 AI 评测重点（可逐条添加）">
          <div class="criteria-editor">
            <div v-for="(_, idx) in editForm.aiCriteriaItems" :key="`e-${idx}`" class="criteria-row">
              <el-input v-model="editForm.aiCriteriaItems[idx]" :placeholder="`评测重点 ${idx + 1}`" />
              <el-button type="danger" plain @click="removeCriteriaItem('edit', idx)">删除</el-button>
            </div>
            <el-button type="primary" plain @click="addCriteriaItem('edit')">+ 添加评测重点</el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAssignmentEdit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="reviewDialogVisible" width="1240px" :title="`作业批改后台 - ${reviewAssignmentTitle || ''}`">
      <div class="review-workbench">
        <div class="review-student-list" v-loading="reviewLoading">
          <div class="review-panel-title">{{ reviewTargetType === 'group' ? '小组列表' : '学生列表' }}</div>
          <el-table
            :data="reviewRows"
            stripe
            highlight-current-row
            :row-class-name="reviewRowClassName"
            @current-change="selectReviewRow"
          >
            <el-table-column prop="student_name" :label="reviewTargetType === 'group' ? '小组' : '学生'" min-width="120" />
            <el-table-column v-if="reviewTargetType === 'group'" label="成员名单" min-width="200">
              <template #default="scope">
                {{ scope.row.team_members?.length ? scope.row.team_members.join('、') : '-' }}
              </template>
            </el-table-column>
            <el-table-column v-else prop="student_no" label="学号" min-width="120" />
            <el-table-column label="状态" width="100">
              <template #default="scope">
                <el-tag :type="statusTagType(scope.row.status)">{{ scope.row.status_label }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="分数" width="80">
              <template #default="scope">{{ formatScore(scope.row.score) }}</template>
            </el-table-column>
          </el-table>
        </div>

        <div class="review-result-panel">
          <div class="review-panel-title">批改结果</div>
          <el-empty v-if="!activeReviewRow" :description="`请先在左侧选择${reviewTargetType === 'group' ? '小组' : '学生'}`" :image-size="90" />
          <template v-else>
            <div class="student-meta">
              <el-tag type="info">{{ activeReviewRow.student_name }}</el-tag>
              <el-tag effect="plain">{{ activeReviewRow.student_no || '无学号' }}</el-tag>
              <el-tag :type="statusTagType(activeReviewRow.status)">{{ activeReviewRow.status_label }}</el-tag>
            </div>
            <div class="file-path">作业文件：{{ activeReviewRow.saved_path || '暂无提交文件' }}</div>

            <el-form :model="reviewForm" label-position="top" class="review-form">
              <el-row :gutter="12">
                <el-col :span="10">
                  <el-form-item label="选择模型">
                    <el-select v-model="reviewForm.ai_model" style="width:100%">
                      <el-option label="OpenAI GPT-4o" value="GPT-4o" />
                      <el-option label="DeepSeek 模型" value="DeepSeek" />
                      <el-option label="阿里通义千问 (Qwen)" value="Qwen" />
                      <el-option label="百度文心一言 (Ernie)" value="Ernie" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="14">
                  <el-form-item label="分数(0-100)">
                    <el-input-number v-model="reviewForm.score" :min="0" :max="100" style="width:100%" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="本次批改要点">
                <el-input v-model="reviewForm.ai_criteria" type="textarea" :rows="3" placeholder="可选" />
              </el-form-item>

              <el-button
                type="primary"
                style="width:100%;margin-bottom:10px"
                :loading="aiReviewing"
                :disabled="!activeReviewRow.submission_id"
                @click="runAssignmentAIReview"
              >提交作业给 AI 模型审核</el-button>

              <div class="history-actions">
                <el-button plain :disabled="!activeReviewRow.submission_id" @click="openAIHistoryDialog">查看 AI 评测记录</el-button>
              </div>

              <el-form-item label="AI 评语">
                <el-input v-model="reviewForm.ai_feedback" type="textarea" :rows="6" />
              </el-form-item>

              <div v-if="reviewFeedbackBlocks.length" class="feedback-blocks">
                <div class="feedback-block" v-for="(block, idx) in reviewFeedbackBlocks" :key="`arb-${idx}`">
                  <div class="feedback-block-title">{{ block.title }}</div>
                  <ul class="feedback-bullets">
                    <li v-for="(line, lineIdx) in block.items" :key="`arb-${idx}-${lineIdx}`">{{ line }}</li>
                  </ul>
                </div>
              </div>

              <el-form-item label="老师点评">
                <el-input v-model="reviewForm.teacher_comment" type="textarea" :rows="3" />
              </el-form-item>

              <el-button type="success" :loading="publishingReview" @click="publishReview" style="width:100%">发布结果</el-button>
            </el-form>
          </template>
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="aiHistoryDialogVisible" title="AI 批改历史" width="900px">
      <div v-loading="aiHistoryLoading">
        <el-empty v-if="!aiHistoryRecords.length" description="暂无历史记录" :image-size="86" />
        <div v-else class="history-list">
          <el-card v-for="item in aiHistoryRecords" :key="item.id" class="history-item" shadow="never">
            <div class="history-item-head">
              <div>
                <el-tag type="info" size="small">#{{ item.id }}</el-tag>
                <el-tag size="small" style="margin-left:8px">{{ item.ai_model || '未知模型' }}</el-tag>
              </div>
              <div class="history-time">{{ item.created_at || '-' }}</div>
            </div>
            <div class="history-text">{{ item.review_text || '（无内容）' }}</div>
            <div class="history-item-actions">
              <el-button type="primary" link @click="applyHistoryRecord(item)">填充到当前评语</el-button>
            </div>
          </el-card>
        </div>
      </div>
      <template #footer>
        <el-button @click="clearAIHistory" :disabled="!activeReviewRow?.submission_id">清空当前提交历史</el-button>
        <el-button @click="aiHistoryDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

interface ClassItem {
  id: number
  name: string
  teacher_id: number
}

interface AssignmentItem {
  id: number
  title: string
  description?: string
  deadline?: string
  ai_criteria?: string
  target_type?: 'individual' | 'group'
  pending_review_count: number
  unsubmitted_count: number
  unit_total?: number
  student_total?: number
}

interface ReviewRow {
  student_id: number
  student_name: string
  student_no?: string
  status: 'unsubmitted' | 'submitted' | 'finished'
  status_label: string
  submission_id: number | null
  score: number | null
  saved_path?: string | null
  code_content?: string | null
  team_members?: string[]
  feedback?: {
    ai_feedback?: string | null
    teacher_comment?: string | null
    ai_criteria?: string | null
    score?: number | null
  }
}

interface AIHistoryRecord {
  id: number
  ai_model?: string
  review_text?: string
  created_at?: string
}

type ProviderKey = 'gpt4o' | 'deepseek' | 'qwen' | 'ernie'
interface ProviderConfig {
  base_url?: string
  api_key?: string
  model_name?: string
}
interface SavedModelConfig {
  prompt_template?: string
  temperature?: number
  max_tokens?: number
  providers?: Record<ProviderKey, ProviderConfig>
}

const route = useRoute()
const router = useRouter()

const role = localStorage.getItem('role') || 'teacher'
const userId = Number(localStorage.getItem('user_id') || 0)

const classes = ref<ClassItem[]>([])
const assignments = ref<AssignmentItem[]>([])
const loading = ref(false)
const publishDialogVisible = ref(false)
const editDialogVisible = ref(false)

const reviewDialogVisible = ref(false)
const reviewLoading = ref(false)
const reviewAssignmentId = ref(0)
const reviewAssignmentTitle = ref('')
const reviewRows = ref<ReviewRow[]>([])
const activeReviewRowId = ref<number | null>(null)
const reviewTargetType = ref<'individual' | 'group'>('individual')

const aiReviewing = ref(false)
const publishingReview = ref(false)
const aiHistoryDialogVisible = ref(false)
const aiHistoryLoading = ref(false)
const aiHistoryRecords = ref<AIHistoryRecord[]>([])

const modelConfigKey = 'ai_review_model_config'
const modelToProvider: Record<string, ProviderKey> = {
  'GPT-4o': 'gpt4o',
  DeepSeek: 'deepseek',
  Qwen: 'qwen',
  Ernie: 'ernie'
}

const publishForm = reactive({
  title: '',
  description: '',
  deadline: '',
  target_type: 'individual' as 'individual' | 'group',
  aiCriteriaItems: [''] as string[]
})

const editForm = reactive({
  id: 0,
  title: '',
  description: '',
  deadline: '',
  aiCriteriaItems: [''] as string[]
})

const reviewForm = reactive({
  ai_model: 'DeepSeek',
  score: 0,
  ai_feedback: '',
  teacher_comment: '',
  ai_criteria: ''
})

const classId = computed(() => Number(route.params.classId || 0))
const classMeta = computed(() => classes.value.find((c) => c.id === classId.value) || null)
const activeTeacherId = computed(() => Number(classMeta.value?.teacher_id || userId || 0))
const activeReviewRow = computed(() => reviewRows.value.find(x => x.student_id === activeReviewRowId.value) || null)

const statusTagType = (status: string) => {
  if (status === 'finished') return 'success'
  if (status === 'submitted') return 'warning'
  return 'info'
}

const formatScore = (score: number | null | undefined) => (score === null || score === undefined ? '-' : score)

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

const reviewFeedbackBlocks = computed(() => {
  const text = (reviewForm.ai_feedback || '').trim()
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

const reviewRowClassName = ({ row }: { row: ReviewRow }) => {
  return row.student_id === activeReviewRowId.value ? 'active-row' : ''
}

const getSavedModelConfig = (): SavedModelConfig => {
  const saved = localStorage.getItem(modelConfigKey)
  if (!saved) return {}
  try {
    return JSON.parse(saved) || {}
  } catch {
    return {}
  }
}

const getProviderConfigByModel = (modelName: string, savedConfig: SavedModelConfig): ProviderConfig => {
  const key = modelToProvider[modelName]
  if (!key) return {}
  return savedConfig.providers?.[key] || {}
}

const fetchBase = async () => {
  const url = role === 'admin'
    ? 'http://127.0.0.1:8000/admin/classes/current'
    : `http://127.0.0.1:8000/teachers/${userId}/classes/current`
  const clsRes = await axios.get(url)
  classes.value = clsRes.data || []

  if (!classes.value.length) return
  if (!classMeta.value) {
    const firstClass = classes.value[0]
    if (firstClass) {
      await router.replace(`/assignment-management/${firstClass.id}`)
    }
  }
}

const fetchAssignments = async () => {
  if (!classId.value) {
    assignments.value = []
    return
  }
  if (role === 'admin' && !classMeta.value) {
    assignments.value = []
    return
  }
  if (!activeTeacherId.value) {
    assignments.value = []
    return
  }

  loading.value = true
  try {
    const res = await axios.get(`http://127.0.0.1:8000/teachers/${activeTeacherId.value}/classes/${classId.value}/assignments`)
    assignments.value = res.data?.assignments || []
  } catch {
    assignments.value = []
    throw new Error('assignments_fetch_failed')
  } finally {
    loading.value = false
  }
}

const openPublishDialog = () => {
  publishForm.title = ''
  publishForm.description = ''
  publishForm.deadline = ''
  publishForm.target_type = 'individual'
  publishForm.aiCriteriaItems = ['']
  publishDialogVisible.value = true
}

const publishAssignment = async () => {
  if (!classId.value) return
  if (!publishForm.title.trim()) return ElMessage.warning('请填写作业标题')

  const criteria = publishForm.aiCriteriaItems.map(x => x.trim()).filter(Boolean)

  await axios.post('http://127.0.0.1:8000/assignments/', {
    title: publishForm.title,
    description: publishForm.description,
    deadline: publishForm.deadline,
    course_id: classId.value,
    target_type: publishForm.target_type,
    ai_criteria: criteria.join('\n')
  })

  publishDialogVisible.value = false
  ElMessage.success('作业发布成功')
  await fetchAssignments()
}

const openEditDialog = (item: AssignmentItem) => {
  editForm.id = item.id
  editForm.title = item.title || ''
  editForm.description = item.description || ''
  editForm.deadline = item.deadline || ''
  const criteriaRows = (item.ai_criteria || '').split(/\r?\n/).map(x => x.trim()).filter(Boolean)
  editForm.aiCriteriaItems = criteriaRows.length ? criteriaRows : ['']
  editDialogVisible.value = true
}

const saveAssignmentEdit = async () => {
  if (!classId.value || !editForm.id || !activeTeacherId.value) return
  if (!editForm.title.trim()) return ElMessage.warning('请填写作业标题')

  const criteria = editForm.aiCriteriaItems.map(x => x.trim()).filter(Boolean)

  await axios.put(`http://127.0.0.1:8000/teachers/${activeTeacherId.value}/classes/${classId.value}/assignments/${editForm.id}`, {
    title: editForm.title,
    description: editForm.description,
    deadline: editForm.deadline,
    ai_criteria: criteria.join('\n')
  })

  editDialogVisible.value = false
  ElMessage.success('作业修改成功')
  await fetchAssignments()
}

const addCriteriaItem = (target: 'publish' | 'edit') => {
  const arr = target === 'publish' ? publishForm.aiCriteriaItems : editForm.aiCriteriaItems
  arr.push('')
}

const removeCriteriaItem = (target: 'publish' | 'edit', idx: number) => {
  const arr = target === 'publish' ? publishForm.aiCriteriaItems : editForm.aiCriteriaItems
  if (arr.length <= 1) {
    arr[0] = ''
    return
  }
  arr.splice(idx, 1)
}

const fetchAssignmentSubmissions = async () => {
  if (!reviewAssignmentId.value) return

  reviewLoading.value = true
  try {
    const res = await axios.get(`http://127.0.0.1:8000/assignments/${reviewAssignmentId.value}/submissions`)
    const rowsRaw = Array.isArray(res.data)
      ? res.data
      : (Array.isArray(res.data?.students) ? res.data.students : [])

    reviewRows.value = rowsRaw.map((item: any, idx: number) => {
      const submissionId = Number(item.submission_id || item.id || 0) || null
      const status = (item.status === 'finished' || item.status === 'submitted' || item.status === 'unsubmitted')
        ? item.status
        : (submissionId ? 'submitted' : 'unsubmitted')
      const status_label = status === 'finished' ? '已批改' : (status === 'submitted' ? '已提交' : '未提交')

      return {
        student_id: Number(item.student_id ?? submissionId ?? (idx + 1)),
        student_name: String(item.student_name || item.team_name || '未知'),
        student_no: item.student_no || '',
        status,
        status_label,
        submission_id: submissionId,
        score: typeof item.score === 'number' ? item.score : null,
        saved_path: item.saved_path || item.file_path || null,
        code_content: item.code_content || null,
        team_members: Array.isArray(item.team_members) ? item.team_members : [],
        feedback: {
          ai_feedback: item.feedback?.ai_feedback ?? item.ai_feedback ?? null,
          teacher_comment: item.feedback?.teacher_comment ?? item.teacher_comment ?? null,
          ai_criteria: item.feedback?.ai_criteria ?? item.ai_criteria ?? null,
          score: item.feedback?.score ?? item.score ?? null
        }
      } as ReviewRow
    })

    const fromTask = (assignments.value.find(x => x.id === reviewAssignmentId.value)?.target_type || 'individual') as 'individual' | 'group'
    reviewTargetType.value = rowsRaw.some((x: any) => x?.target_type === 'group') ? 'group' : fromTask

    if (!reviewRows.value.length) {
      activeReviewRowId.value = null
      return
    }

    const preferred = reviewRows.value.find(x => x.student_id === activeReviewRowId.value)
      || reviewRows.value.find(x => !!x.submission_id)
      || reviewRows.value[0]
    selectReviewRow(preferred || null)
  } catch (e: any) {
    reviewRows.value = []
    activeReviewRowId.value = null
    ElMessage.error(e?.response?.data?.detail || '获取作业提交列表失败')
  } finally {
    reviewLoading.value = false
  }
}

const openReviewDialog = async (item: AssignmentItem) => {
  reviewAssignmentId.value = item.id
  reviewAssignmentTitle.value = item.title
  reviewTargetType.value = item.target_type === 'group' ? 'group' : 'individual'
  reviewDialogVisible.value = true
  await fetchAssignmentSubmissions()
}

const selectReviewRow = (row: ReviewRow | null) => {
  if (!row) return
  activeReviewRowId.value = row.student_id
  reviewForm.ai_model = reviewForm.ai_model || 'DeepSeek'
  reviewForm.score = row.score ?? 0
  reviewForm.ai_feedback = row.feedback?.ai_feedback || ''
  reviewForm.teacher_comment = row.feedback?.teacher_comment || ''
  reviewForm.ai_criteria = row.feedback?.ai_criteria || ''
  aiHistoryRecords.value = []
}

const runAssignmentAIReview = async () => {
  const row = activeReviewRow.value
  if (!row?.submission_id) return ElMessage.warning(`该${reviewTargetType.value === 'group' ? '小组' : '学生'}尚未提交作业，无法进行 AI 审核`)

  const codeContent = (row.code_content || '').trim()
  if (!codeContent) return ElMessage.warning('未找到作业代码内容，无法进行 AI 审核')

  aiReviewing.value = true
  const checks = (reviewForm.ai_criteria || '').trim() || '1. 核心功能正确性\n2. 异常处理与边界情况\n3. 代码规范与可维护性'
  const savedConfig = getSavedModelConfig()
  const assignmentPromptTemplate = (savedConfig.prompt_template || '请根据{functionality_checks}对学生代码进行评分与反馈，并严格输出三段评分格式。').trim()
  const provider = getProviderConfigByModel(reviewForm.ai_model, savedConfig)

  try {
    const res = await axios.post('http://127.0.0.1:8000/ai/review', {
      code_content: codeContent,
      task_type: 'assignment',
      prompt_template: assignmentPromptTemplate,
      assignment_prompt_template: assignmentPromptTemplate,
      functionality_checks: checks,
      ai_model: reviewForm.ai_model,
      submission_id: row.submission_id,
      assignment_id: reviewAssignmentId.value,
      temperature: Number(savedConfig.temperature ?? 0.2),
      max_tokens: Number(savedConfig.max_tokens ?? 100000),
      provider: {
        base_url: (provider.base_url || '').trim(),
        api_key: (provider.api_key || '').trim(),
        model_name: (provider.model_name || '').trim()
      }
    })

    reviewForm.ai_feedback = res.data?.ai_feedback || ''
    if (typeof res.data?.score === 'number') {
      reviewForm.score = Math.max(0, Math.min(100, Number(res.data.score)))
    }

    if (aiHistoryDialogVisible.value) {
      await fetchAIHistory()
    }
    ElMessage.success('AI 审核完成，请确认后发布')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'AI 审核失败')
  } finally {
    aiReviewing.value = false
  }
}

const publishReview = async () => {
  const row = activeReviewRow.value
  if (!row?.submission_id) return ElMessage.warning('未找到可发布的作业提交记录')
  if (!reviewForm.ai_feedback.trim()) return ElMessage.warning('请先生成或填写 AI 评语')

  publishingReview.value = true
  try {
    await axios.post('http://127.0.0.1:8000/publish_report/', {
      submission_id: row.submission_id,
      ai_model: reviewForm.ai_model,
      score: reviewForm.score,
      ai_feedback: reviewForm.ai_feedback,
      teacher_comment: reviewForm.teacher_comment,
      ai_criteria: reviewForm.ai_criteria
    })

    ElMessage.success('作业批改结果已发布')
    await fetchAssignmentSubmissions()
    await fetchAssignments()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '发布作业批改结果失败')
  } finally {
    publishingReview.value = false
  }
}

const fetchAIHistory = async () => {
  const row = activeReviewRow.value
  if (!row?.submission_id) {
    aiHistoryRecords.value = []
    return
  }

  aiHistoryLoading.value = true
  try {
    const res = await axios.get(`http://127.0.0.1:8000/ai/review/history/${row.submission_id}`, {
      params: { limit: 50 }
    })
    aiHistoryRecords.value = Array.isArray(res.data) ? res.data as AIHistoryRecord[] : []
  } catch (e: any) {
    aiHistoryRecords.value = []
    ElMessage.error(e?.response?.data?.detail || '获取AI评测历史失败')
  } finally {
    aiHistoryLoading.value = false
  }
}

const openAIHistoryDialog = async () => {
  const row = activeReviewRow.value
  if (!row?.submission_id) return ElMessage.warning('该条记录尚无可查询的提交')
  aiHistoryDialogVisible.value = true
  await fetchAIHistory()
}

const applyHistoryRecord = (item: AIHistoryRecord) => {
  reviewForm.ai_feedback = (item.review_text || '').trim()
  ElMessage.success('已填充该条历史评语')
}

const clearAIHistory = async () => {
  const row = activeReviewRow.value
  if (!row?.submission_id) return

  try {
    await axios.delete(`http://127.0.0.1:8000/ai/review/history/${row.submission_id}`)
    ElMessage.success('当前提交历史已清空')
    await fetchAIHistory()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '清空历史失败')
  }
}

watch(() => route.path, async () => {
  try {
    await fetchBase()
    await fetchAssignments()
  } catch {
    ElMessage.error('作业管理数据加载失败')
  }
}, { immediate: true })
</script>

<style scoped>
.page-container { padding: 24px; background: #f8fafc; min-height: calc(100vh - 60px); }
.page-card { border-radius: 12px; }
.header-row { display: flex; justify-content: space-between; align-items: center; }
.title { font-size: 18px; font-weight: 700; color: #1f2937; }
.sub-title { color: #64748b; margin-top: 4px; }
.task-plaza h3 { margin: 8px 0 16px; color: #1f2937; }
.task-card { border-radius: 10px; }
.task-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
.task-id { font-size: 12px; color: #64748b; }
.task-title { margin: 8px 0; color: #0f172a; }
.task-desc { min-height: 34px; color: #64748b; font-size: 13px; }
.stat-row { display: flex; gap: 8px; margin: 8px 0 10px; flex-wrap: wrap; }
.deadline { margin: 6px 0 0; font-size: 12px; color: #ef4444; }
.action-spacer { height: 20px; }
.card-actions { display: flex; gap: 8px; }
.criteria-editor { display: flex; flex-direction: column; gap: 8px; width: 100%; }
.criteria-row { display: grid; grid-template-columns: 1fr auto; gap: 8px; }
.review-workbench { display: grid; grid-template-columns: 0.95fr 2.7fr; gap: 16px; min-height: 560px; }
.review-student-list, .review-result-panel { border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; background: #fff; }
.review-panel-title { font-size: 14px; font-weight: 700; color: #1f2937; margin-bottom: 10px; }
.student-meta { display: flex; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }
.file-path { font-size: 12px; color: #64748b; margin-bottom: 8px; word-break: break-all; }
.history-actions { display: flex; justify-content: flex-end; margin-bottom: 10px; }
.feedback-blocks { display: grid; gap: 10px; margin: 0 0 12px; }
.feedback-block { border: 1px solid #e6ebf5; border-radius: 10px; padding: 10px; background: #f8faff; }
.feedback-block-title { color: #334155; font-size: 13px; font-weight: 700; margin-bottom: 6px; }
.feedback-bullets { margin: 0; padding-left: 18px; color: #1e293b; line-height: 1.7; }
.history-list { max-height: 64vh; overflow: auto; padding-right: 4px; }
.history-item { margin-bottom: 10px; }
.history-item-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.history-time { color: #64748b; font-size: 12px; }
.history-text { white-space: pre-wrap; color: #1e293b; line-height: 1.6; background: #f8fafc; border-radius: 8px; padding: 10px; }
.history-item-actions { margin-top: 8px; display: flex; justify-content: flex-end; gap: 8px; }
:deep(.el-table .active-row > td) { background: #eff6ff !important; }
</style>
