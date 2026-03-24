<template>
  <div class="page-container">
    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="header-row">
          <div>
            <div class="title">📄 报告管理</div>
            <div class="sub-title" v-if="classMeta">当前班级：{{ classMeta.name }}</div>
          </div>
          <el-button type="primary" @click="openPublishDialog" :disabled="!classMeta">发布报告任务</el-button>
        </div>
      </template>

      <el-empty v-if="!classMeta" description="当前学期暂无可管理班级" />

      <template v-else>
        <div class="task-plaza">
          <h3>已发布报告任务（{{ classMeta.name }}）</h3>
          <el-row :gutter="16" v-loading="loading">
            <el-col :span="8" v-for="item in reportTasks" :key="item.id" style="margin-bottom:16px">
              <el-card shadow="hover" class="task-card">
                <div class="task-head">
                  <div class="task-id">Report Task #{{ item.id }}</div>
                  <el-tag size="small" :type="item.target_type === 'group' ? 'warning' : 'info'">
                    {{ item.target_type === 'group' ? '小组报告' : '个人报告' }}
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

    <el-dialog v-model="publishDialogVisible" title="发布报告任务" width="620px">
      <el-form :model="publishForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="14">
            <el-form-item label="任务标题">
              <el-input v-model="publishForm.title" />
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="截止日期">
              <el-date-picker v-model="publishForm.deadline" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="任务描述">
          <el-input v-model="publishForm.description" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="发布方式">
          <el-radio-group v-model="publishForm.target_type">
            <el-radio label="individual">个人报告</el-radio>
            <el-radio label="group">小组报告</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="publishDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="publishReportTask">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editDialogVisible" title="修改报告任务" width="620px">
      <el-form :model="editForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="14">
            <el-form-item label="任务标题">
              <el-input v-model="editForm.title" />
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="截止日期">
              <el-date-picker v-model="editForm.deadline" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="任务描述">
          <el-input v-model="editForm.description" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveReportTaskEdit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="reviewDialogVisible" width="1240px" :title="`报告批改后台 - ${reviewTaskTitle || ''}`">
      <div class="review-workbench">
        <div class="review-student-list" v-loading="reviewLoading">
          <div class="review-panel-title">{{ reviewTargetType === 'group' ? '小组列表' : '学生列表' }}</div>
          <el-table
            :data="reviewRows"
            stripe
            highlight-current-row
            :row-class-name="rowClassName"
            @current-change="selectReviewRow"
          >
            <el-table-column prop="student_name" label="学生" min-width="110" />
            <el-table-column prop="student_no" label="学号" min-width="120" />
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
          <el-empty v-if="!activeReviewRow" description="请先在左侧选择学生" :image-size="90" />
          <template v-else>
            <div class="student-meta">
              <el-tag type="info">{{ activeReviewRow.student_name }}</el-tag>
              <el-tag effect="plain">{{ activeReviewRow.student_no || '无学号' }}</el-tag>
              <el-tag :type="statusTagType(activeReviewRow.status)">{{ activeReviewRow.status_label }}</el-tag>
            </div>
            <div class="file-path">报告文件：{{ activeReviewRow.saved_path || '暂无提交文件' }}</div>

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

              <div style="display:flex;gap:10px;margin-bottom:10px">
                <el-button
                  type="primary"
                  style="flex:1"
                  :loading="aiReviewing"
                  :disabled="!activeReviewRow.submission_id || activeReviewRow.status === 'returned' || !activeReviewRow.saved_path"
                  @click="runReportAIReview"
                >提交报告给 AI 模型审核</el-button>

                <el-popconfirm
                  title="确认退回该报告？退回后会删除服务器上的报告文件，学生可重新提交。"
                  @confirm="returnSubmission"
                >
                  <template #reference>
                    <el-button
                      type="danger"
                      plain
                      style="flex:1"
                      :loading="returningReview"
                      :disabled="!activeReviewRow.submission_id || activeReviewRow.status === 'returned'"
                    >退回学生报告</el-button>
                  </template>
                </el-popconfirm>
              </div>

              <div class="history-actions">
                <el-button plain :disabled="!activeReviewRow.submission_id" @click="openAIHistoryDialog">查看 AI 评测记录</el-button>
              </div>

              <el-form-item label="AI 评语">
                <el-input v-model="reviewForm.ai_feedback" type="textarea" :rows="6" />
              </el-form-item>

              <div v-if="reviewFeedbackBlocks.length" class="feedback-blocks">
                <div class="feedback-block" v-for="(block, idx) in reviewFeedbackBlocks" :key="`rrb-${idx}`">
                  <div class="feedback-block-title">{{ block.title }}</div>
                  <ul class="feedback-bullets">
                    <li v-for="(line, lineIdx) in block.items" :key="`rrb-${idx}-${lineIdx}`">{{ line }}</li>
                  </ul>
                </div>
              </div>

              <el-form-item label="老师点评">
                <el-input v-model="reviewForm.teacher_comment" type="textarea" :rows="3" />
              </el-form-item>

              <el-button
                type="success"
                :loading="publishingReview"
                :disabled="activeReviewRow.status === 'returned'"
                @click="publishReview"
                style="width:100%"
              >发布结果</el-button>
            </el-form>
          </template>
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="aiHistoryDialogVisible" title="AI 批改历史" width="900px">
      <div v-loading="aiHistoryLoading">
        <el-empty v-if="!aiHistoryRecords.length" description="暂无历史记录" :image-size="86" />
        <div v-else class="history-list">
          <el-card v-for="item in aiHistoryRecords" :key="item.record_id" class="history-item" shadow="never">
            <div class="history-item-head">
              <div>
                <el-tag type="info" size="small">#{{ item.record_id }}</el-tag>
                <el-tag size="small" style="margin-left:8px">{{ item.ai_model || '未知模型' }}</el-tag>
                <el-tag size="small" type="success" style="margin-left:8px">评分：{{ formatScore(item.score) }}</el-tag>
              </div>
              <div class="history-time">{{ item.created_at || '-' }}</div>
            </div>
            <div class="history-text">{{ item.review_text || '（无内容）' }}</div>
            <div class="history-item-actions">
              <el-button type="primary" link @click="applyHistoryRecord(item)">填充到当前评语</el-button>
              <el-popconfirm title="确认删除该条AI评测记录？" @confirm="deleteHistoryRecord(item.record_id)">
                <template #reference>
                  <el-button type="danger" link>删除记录</el-button>
                </template>
              </el-popconfirm>
            </div>
          </el-card>
        </div>
      </div>
      <template #footer>
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

interface ReportTaskItem {
  id: number
  title: string
  description?: string
  deadline?: string
  target_type?: 'individual' | 'group'
  pending_review_count: number
  unsubmitted_count: number
  unit_total?: number
  student_total?: number
}

interface ReviewStudentRow {
  student_id: number
  student_name: string
  student_no?: string
  status: 'unsubmitted' | 'submitted' | 'finished' | 'returned'
  status_label: string
  submission_id: number | null
  score: number | null
  saved_path?: string | null
  feedback?: {
    ai_feedback?: string | null
    teacher_comment?: string | null
    ai_criteria?: string | null
    score?: number | null
  }
}

interface AIHistoryRecord {
  record_id: number
  ai_model?: string | null
  score?: number | null
  created_at?: string | null
  review_text?: string | null
}

const route = useRoute()
const router = useRouter()

const role = localStorage.getItem('role') || 'teacher'
const userId = Number(localStorage.getItem('user_id') || 0)

const classes = ref<ClassItem[]>([])
const reportTasks = ref<ReportTaskItem[]>([])
const loading = ref(false)
const publishDialogVisible = ref(false)
const editDialogVisible = ref(false)

const reviewDialogVisible = ref(false)
const reviewLoading = ref(false)
const reviewTaskId = ref(0)
const reviewTaskTitle = ref('')
const reviewRows = ref<ReviewStudentRow[]>([])
const activeReviewRowId = ref<number | null>(null)
const reviewTargetType = ref<'individual' | 'group'>('individual')

const publishingReview = ref(false)
const returningReview = ref(false)
const aiReviewing = ref(false)
const aiHistoryDialogVisible = ref(false)
const aiHistoryLoading = ref(false)
const aiHistoryRecords = ref<AIHistoryRecord[]>([])

type ProviderKey = 'gpt4o' | 'deepseek' | 'qwen' | 'ernie'
interface ProviderConfig {
  base_url?: string
  api_key?: string
  model_name?: string
}
interface SavedModelConfig {
  prompt_template?: string
  report_prompt_template?: string
  temperature?: number
  max_tokens?: number
  providers?: Record<ProviderKey, ProviderConfig>
}

const modelToProvider: Record<string, ProviderKey> = {
  'GPT-4o': 'gpt4o',
  DeepSeek: 'deepseek',
  Qwen: 'qwen',
  Ernie: 'ernie'
}
const modelConfigKey = 'ai_review_model_config'

const publishForm = reactive({
  title: '',
  description: '',
  deadline: '',
  target_type: 'individual' as 'individual' | 'group'
})

const editForm = reactive({
  id: 0,
  title: '',
  description: '',
  deadline: ''
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
const activeTeacherId = computed(() => {
  if (role === 'admin') return Number(classMeta.value?.teacher_id || 0)
  return Number(userId || 0)
})
const activeReviewRow = computed(() => reviewRows.value.find(x => x.student_id === activeReviewRowId.value) || null)

const statusTagType = (status: string) => {
  if (status === 'finished') return 'success'
  if (status === 'submitted') return 'warning'
  if (status === 'returned') return 'danger'
  return 'info'
}

const formatScore = (score: number | null | undefined) => (score === null || score === undefined ? '-' : score)

const rowClassName = ({ row }: { row: ReviewStudentRow }) => {
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
      await router.replace(`/report-management/${firstClass.id}`)
    }
  }
}

const fetchReportTasks = async () => {
  if (!classId.value) {
    reportTasks.value = []
    return
  }
  if (role === 'admin' && !classMeta.value) {
    reportTasks.value = []
    return
  }
  if (!activeTeacherId.value) {
    reportTasks.value = []
    return
  }

  loading.value = true
  try {
    const res = await axios.get(`http://127.0.0.1:8000/teachers/${activeTeacherId.value}/classes/${classId.value}/report-tasks`)
    reportTasks.value = Array.isArray(res.data) ? res.data : (res.data?.report_tasks || [])
  } catch {
    reportTasks.value = []
    throw new Error('report_tasks_fetch_failed')
  } finally {
    loading.value = false
  }
}

const fetchReportTaskSubmissions = async () => {
  if (!classId.value || !reviewTaskId.value) {
    reviewRows.value = []
    activeReviewRowId.value = null
    return
  }
  if (role === 'admin' && !classMeta.value) {
    reviewRows.value = []
    activeReviewRowId.value = null
    return
  }
  if (!activeTeacherId.value) {
    reviewRows.value = []
    activeReviewRowId.value = null
    return
  }

  reviewLoading.value = true
  try {
    const res = await axios.get(
      `http://127.0.0.1:8000/teachers/${activeTeacherId.value}/classes/${classId.value}/report-tasks/${reviewTaskId.value}/submissions`
    )
    reviewTargetType.value = (res.data?.target_type === 'group' ? 'group' : 'individual')
    reviewRows.value = Array.isArray(res.data?.students)
      ? res.data.students
      : (Array.isArray(res.data) ? res.data : [])

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
    ElMessage.error(e?.response?.data?.detail || '获取报告提交列表失败')
  } finally {
    reviewLoading.value = false
  }
}

const openPublishDialog = () => {
  publishForm.title = ''
  publishForm.description = ''
  publishForm.deadline = ''
  publishForm.target_type = 'individual'
  publishDialogVisible.value = true
}

const publishReportTask = async () => {
  if (!classId.value) return
  if (!publishForm.title.trim()) return ElMessage.warning('请填写报告任务标题')

  await axios.post('http://127.0.0.1:8000/report-tasks/', {
    title: publishForm.title,
    description: publishForm.description,
    deadline: publishForm.deadline,
    class_id: classId.value,
    target_type: publishForm.target_type
  })

  publishDialogVisible.value = false
  ElMessage.success('报告任务发布成功')
  await fetchReportTasks()
}

const openEditDialog = (task: ReportTaskItem) => {
  editForm.id = task.id
  editForm.title = task.title || ''
  editForm.description = task.description || ''
  editForm.deadline = task.deadline || ''
  editDialogVisible.value = true
}

const saveReportTaskEdit = async () => {
  if (!classId.value || !activeTeacherId.value || !editForm.id) return
  if (!editForm.title.trim()) return ElMessage.warning('请填写报告任务标题')

  await axios.put(
    `http://127.0.0.1:8000/teachers/${activeTeacherId.value}/classes/${classId.value}/report-tasks/${editForm.id}`,
    {
      title: editForm.title,
      description: editForm.description,
      deadline: editForm.deadline
    }
  )

  editDialogVisible.value = false
  ElMessage.success('报告任务修改成功')
  await fetchReportTasks()
}

const selectReviewRow = (row: ReviewStudentRow | null) => {
  if (!row) return
  activeReviewRowId.value = row.student_id
  reviewForm.ai_model = reviewForm.ai_model || 'DeepSeek'
  reviewForm.score = row.score ?? 0
  reviewForm.ai_feedback = row.feedback?.ai_feedback || ''
  reviewForm.teacher_comment = row.feedback?.teacher_comment || ''
  reviewForm.ai_criteria = row.feedback?.ai_criteria || ''
  aiHistoryRecords.value = []
}

const fetchAIHistory = async () => {
  const row = activeReviewRow.value
  if (!row?.submission_id) {
    aiHistoryRecords.value = []
    return
  }

  aiHistoryLoading.value = true
  try {
    const res = await axios.get(
      `http://127.0.0.1:8000/teachers/${activeTeacherId.value}/report-submissions/${row.submission_id}/ai-history`
    )
    aiHistoryRecords.value = (res.data?.records || []) as AIHistoryRecord[]
  } catch (e: any) {
    aiHistoryRecords.value = []
    ElMessage.error(e?.response?.data?.detail || '获取AI评测历史失败')
  } finally {
    aiHistoryLoading.value = false
  }
}

const openAIHistoryDialog = async () => {
  const row = activeReviewRow.value
  if (!row?.submission_id) return ElMessage.warning('该学生尚无可查询的提交记录')
  aiHistoryDialogVisible.value = true
  await fetchAIHistory()
}

const applyHistoryRecord = (item: AIHistoryRecord) => {
  reviewForm.ai_feedback = (item.review_text || '').trim()
  if (typeof item.score === 'number') {
    reviewForm.score = Math.max(0, Math.min(100, Number(item.score)))
  }
  ElMessage.success('已填充该条历史评语')
}

const deleteHistoryRecord = async (recordId: number) => {
  const row = activeReviewRow.value
  if (!row?.submission_id) return

  try {
    await axios.delete(
      `http://127.0.0.1:8000/teachers/${activeTeacherId.value}/report-submissions/${row.submission_id}/ai-history/${recordId}`
    )
    ElMessage.success('历史记录已删除')
    await fetchAIHistory()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '删除历史记录失败')
  }
}

const openReviewDialog = async (task: ReportTaskItem) => {
  reviewTaskId.value = task.id
  reviewTaskTitle.value = task.title
  reviewDialogVisible.value = true
  await fetchReportTaskSubmissions()
}

const runReportAIReview = async () => {
  const row = activeReviewRow.value
  if (!row?.submission_id) return ElMessage.warning('该学生尚未提交报告，无法进行 AI 审核')

  aiReviewing.value = true
  const checks = (reviewForm.ai_criteria || '').trim() || '1. 报告结构完整性\n2. 技术内容准确性\n3. 结论与数据一致性\n4. 表达规范性'
  const savedConfig = getSavedModelConfig()
  const reportPromptTemplate = (savedConfig.report_prompt_template || '请根据{functionality_checks}对学生报告进行结构化评分与反馈，并给出总分(0-100)和改进建议。').trim()
  const provider = getProviderConfigByModel(reviewForm.ai_model, savedConfig)

  try {
    const savedPath = (row.saved_path || '').trim()
    if (!savedPath) return ElMessage.warning('未找到报告文件路径，无法进行 AI 审核')

    const res = await axios.post('http://127.0.0.1:8000/ai/review', {
      code_content: `[报告文件] ${savedPath}`,
      task_type: 'report',
      prompt_template: reportPromptTemplate,
      report_prompt_template: reportPromptTemplate,
      functionality_checks: checks,
      ai_model: reviewForm.ai_model,
      submission_id: row.submission_id,
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
  if (!row?.submission_id) return ElMessage.warning('未找到可发布的报告提交记录')
  if (row.status === 'returned') return ElMessage.warning('该报告已退回，请等待学生重新提交')
  if (!reviewForm.ai_feedback.trim()) return ElMessage.warning('请先生成或填写 AI 评语')

  publishingReview.value = true
  try {
    await axios.post(
      `http://127.0.0.1:8000/teachers/${activeTeacherId.value}/report-submissions/${row.submission_id}/publish-report`,
      {
        ai_model: reviewForm.ai_model,
        score: reviewForm.score,
        ai_feedback: reviewForm.ai_feedback,
        teacher_comment: reviewForm.teacher_comment,
        ai_criteria: reviewForm.ai_criteria
      }
    )
    ElMessage.success('报告批改结果已发布')
    await fetchReportTaskSubmissions()
    await fetchReportTasks()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '发布报告批改结果失败')
  } finally {
    publishingReview.value = false
  }
}

const returnSubmission = async () => {
  const row = activeReviewRow.value
  if (!row?.submission_id) return ElMessage.warning('未找到可退回的报告提交记录')
  if (row.status === 'returned') return ElMessage.warning('该报告已处于退回状态')

  returningReview.value = true
  try {
    await axios.post(
      `http://127.0.0.1:8000/teachers/${activeTeacherId.value}/report-submissions/${row.submission_id}/return`,
      { reason: '请根据评语修改后重新提交' }
    )
    ElMessage.success('报告已退回，学生可重新提交')
    await fetchReportTaskSubmissions()
    await fetchReportTasks()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '退回报告失败')
  } finally {
    returningReview.value = false
  }
}

watch(() => route.path, async () => {
  try {
    await fetchBase()
    await fetchReportTasks()
  } catch {
    ElMessage.error('报告管理数据加载失败')
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
