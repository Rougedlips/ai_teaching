<template>
  <div class="console-container">
    <el-page-header @back="$router.push('/')" :content="'批改控制台：' + taskTitle" />
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="7">
        <el-card shadow="never" class="list-card">
          <template #header><b>{{ reviewTargetLabel }}提交列表</b></template>
          <el-table :data="submissionList" highlight-current-row @current-change="selectSubmission">
            <el-table-column prop="student_name" :label="reviewTargetNameLabel" />
            <el-table-column v-if="reviewTargetType === 'group'" label="成员名单" min-width="220">
              <template #default="s">
                <span class="team-members-text">{{ s.row.team_members?.length ? s.row.team_members.join('、') : '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="s">
                <el-tag :type="s.row.status==='finished'?'success':'warning'" size="small">
                  {{s.row.status==='finished'?'已批阅':'待处理'}}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="17">
        <el-card v-if="currSub" shadow="never" class="review-card">
          <div class="code-header">📁 {{ reviewTargetLabel }}源码预览 (ID: {{ currSub.id }})</div>
          <div class="code-box"><pre>{{ currSub.code_content }}</pre></div>

          <el-form label-position="top" style="margin-top:25px;">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="🤖 选择 AI 评测模型">
                  <el-select v-model="form.ai_model" placeholder="请选择模型" style="width: 100%">
                    <el-option label="OpenAI GPT-4o" value="GPT-4o" />
                    <el-option label="DeepSeek 模型" value="DeepSeek" />
                    <el-option label="阿里通义千问 (Qwen)" value="Qwen" />
                    <el-option label="百度文心一言 (Ernie)" value="Ernie" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="💯 建议得分 (AI 自动计算参考)">
                  <el-input-number v-model="form.score" :min="0" :max="100" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="🎯 本次作业 AI 评测重点（来自作业配置）">
              <ul v-if="criteriaLines.length" class="criteria-list">
                <li v-for="(line, idx) in criteriaLines" :key="`c-${idx}`">{{ line }}</li>
              </ul>
              <el-empty v-else description="当前作业未配置评测重点" :image-size="60" />
            </el-form-item>

            <el-button
              type="primary"
              class="analyze-btn"
              @click="runAIReview"
              :loading="aiLoading"
            >⚡ 呼叫 {{ form.ai_model || 'AI' }} 进行分析</el-button>

            <el-form-item label="🕘 AI评测历史记录" style="margin-top: 18px;">
              <div class="history-toolbar">
                <el-select
                  v-model="historyFilterModel"
                  clearable
                  filterable
                  placeholder="按模型筛选"
                  class="history-filter"
                  @change="onHistoryFilterChange"
                >
                  <el-option
                    v-for="model in historyModelOptions"
                    :key="model"
                    :label="model"
                    :value="model"
                  />
                </el-select>
                <el-button
                  type="danger"
                  plain
                  :disabled="!currSub || historyLoading"
                  @click="clearCurrentHistory"
                >清空当前提交历史</el-button>
              </div>

              <el-empty v-if="!historyList.length && !historyLoading" description="暂无历史评测记录" :image-size="50" />
              <div v-else class="history-list" v-loading="historyLoading">
                <div
                  v-for="item in historyList"
                  :key="item.id"
                  class="history-item"
                  :class="{ active: item.id === activeHistoryId }"
                  @click="applyHistory(item)"
                >
                  <div class="history-item-title">
                    <span>{{ item.ai_model || 'AI模型' }}</span>
                    <span>{{ formatHistoryTime(item.created_at) }}</span>
                  </div>
                  <div class="history-item-preview">{{ item.review_text.slice(0, 80) }}{{ item.review_text.length > 80 ? '...' : '' }}</div>
                </div>
              </div>
            </el-form-item>


            <el-form-item label="📊 AI 诊断报告分析 (可由老师二次润色)">
              <el-input v-model="form.ai_feedback" type="textarea" :rows="6" />
            </el-form-item>

            <el-form-item label="🧮 评分构成（正则解析）">
              <div class="score-card-grid">
                <el-card shadow="never" class="score-card">
                  <div class="score-card-title">功能评分</div>
                  <div class="score-card-main">{{ scoreBreakdown.function.scoreText }}</div>
                  <div class="score-card-comment">{{ scoreBreakdown.function.comment }}</div>
                </el-card>
                <el-card shadow="never" class="score-card">
                  <div class="score-card-title">代码质量</div>
                  <div class="score-card-main">{{ scoreBreakdown.quality.scoreText }}</div>
                  <div class="score-card-comment">{{ scoreBreakdown.quality.comment }}</div>
                </el-card>
                <el-card shadow="never" class="score-card">
                  <div class="score-card-title">原创性分析</div>
                  <div class="score-card-main">{{ scoreBreakdown.originality.scoreText }}</div>
                  <div class="score-card-comment">{{ scoreBreakdown.originality.comment }}</div>
                </el-card>
              </div>
            </el-form-item>

            <el-form-item label="🛠 代码问题解析（来自AI报告）">
              <div class="issue-grid">
                <el-card shadow="never" class="issue-card">
                  <div class="issue-title">代码错误</div>
                  <ul class="issue-list">
                    <li v-for="(x, i) in issueBreakdown.codeErrors" :key="`e-${i}`">{{ x }}</li>
                  </ul>
                </el-card>
                <el-card shadow="never" class="issue-card">
                  <div class="issue-title">潜在问题</div>
                  <ul class="issue-list">
                    <li v-for="(x, i) in issueBreakdown.potentialIssues" :key="`p-${i}`">{{ x }}</li>
                  </ul>
                </el-card>
                <el-card shadow="never" class="issue-card">
                  <div class="issue-title">代码风格问题</div>
                  <ul class="issue-list">
                    <li v-for="(x, i) in issueBreakdown.styleIssues" :key="`s-${i}`">{{ x }}</li>
                  </ul>
                </el-card>
              </div>
            </el-form-item>


            <el-form-item label="✍️ 教师最终意见 (将与 AI 报告合并发送)">
              <el-input v-model="form.teacher_comment" type="textarea" :rows="2" placeholder="请输入您的补充建议..." />
            </el-form-item>
            
            <el-button type="success" @click="submitReview" size="large" style="width:100%; font-weight: bold;">
              生成并发送学情报告分析
            </el-button>
          </el-form>
        </el-card>
        <el-empty v-else :description="`请从左侧选择${reviewTargetLabel}开始批改`" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElNotification } from 'element-plus'

interface SubmissionItem {
  id: number
  student_name?: string
  team_name?: string
  team_members?: string[]
  target_type?: 'individual' | 'group' | string
  status?: string
  score?: number
  code_content?: string
  ai_criteria?: string
  ai_feedback?: string
  teacher_comment?: string
}

interface ReviewHistoryItem {
  id: number
  submission_id: number
  assignment_id?: number
  ai_model?: string
  review_text: string
  created_at?: string
}


const route = useRoute()
const aid = Number(route.query.aid || 0)
const taskTitle = ref('')
const taskCriteria = ref('')
const submissionList = ref<SubmissionItem[]>([])
const currSub = ref<SubmissionItem | null>(null)
const aiLoading = ref(false)
const historyLoading = ref(false)
const historyList = ref<ReviewHistoryItem[]>([])
const activeHistoryId = ref<number | null>(null)
const historyFilterModel = ref('')
const historyModelPool = ref<string[]>([])

const reviewTargetType = computed<'individual' | 'group'>(() => {
  if (currSub.value?.target_type === 'group') return 'group'
  if (submissionList.value.some(item => item.target_type === 'group')) return 'group'
  return 'individual'
})
const reviewTargetLabel = computed(() => (reviewTargetType.value === 'group' ? '小组' : '学生'))
const reviewTargetNameLabel = computed(() => (reviewTargetType.value === 'group' ? '小组名称' : '学生姓名'))

const modelConfigKey = 'ai_review_model_config'


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

const form = reactive({
  ai_model: 'DeepSeek',
  ai_feedback: '',
  teacher_comment: '',
  score: 0
})


const criteriaLines = computed(() =>
  (taskCriteria.value || '').split(/\r?\n/).map(x => x.trim()).filter(Boolean)
)

const parseScoreLine = (raw: string, label: string, fallbackScoreText: string) => {
  const reg = new RegExp(`${label}[:：]\\s*([0-9]{1,3}(?:\\s*[-~—]\\s*[0-9]{1,3})?\\s*分?)\\s*[（(]评语[:：]\\s*([^)）\\n]+)[)）]?`)
  const m = raw.match(reg)
  if (!m) {
    return { scoreText: fallbackScoreText, comment: '未解析到评语' }
  }
  return {
    scoreText: m[1].replace(/\s+/g, ''),
    comment: m[2].trim()
  }
}

const scoreBreakdown = computed(() => {
  const raw = form.ai_feedback || ''
  return {
    function: parseScoreLine(raw, '1\\.\\s*功能评分', '0-70分'),
    quality: parseScoreLine(raw, '2\\.\\s*代码质量', '0-25分'),
    originality: parseScoreLine(raw, '3\\.\\s*原创性分析', '0-5分')
  }
})

const extractIssueSection = (raw: string, labels: string[], nextLabels: string[]) => {
  for (const label of labels) {
    const next = nextLabels.length ? `(?=\\n\\s*(?:${nextLabels.join('|')})\\s*[:：]|$)` : '$'
    const reg = new RegExp(`(?:^|\\n)\\s*(?:[-*\\d.）(\\s]*)?${label}\\s*[:：]\\s*([\\s\\S]*?)${next}`, 'i')
    const m = raw.match(reg)
    if (m?.[1]?.trim()) return m[1].trim()
  }
  return ''
}

const normalizeIssueLines = (text: string) => {
  const lines = text
    .split(/\r?\n/)
    .map(x => x.replace(/^[-*•\d.）(\s]+/, '').trim())
    .filter(Boolean)
  return lines.length ? lines : ['未解析到相关内容']
}

const issueBreakdown = computed(() => {
  const raw = form.ai_feedback || ''
  const codeErrors = extractIssueSection(raw, ['本组代码存在的代码错误', '代码错误'], ['潜在问题', '代码风格问题'])
  const potentialIssues = extractIssueSection(raw, ['潜在问题'], ['代码风格问题'])
  const styleIssues = extractIssueSection(raw, ['代码风格问题'], [])

  return {
    codeErrors: normalizeIssueLines(codeErrors),
    potentialIssues: normalizeIssueLines(potentialIssues),
    styleIssues: normalizeIssueLines(styleIssues)
  }
})

const formatHistoryTime = (v?: string) => {
  if (!v) return '--'
  const d = new Date(v)
  if (Number.isNaN(d.getTime())) return v
  const p = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

const historyModelOptions = computed(() => historyModelPool.value)

const syncHistoryModelPool = (rows: ReviewHistoryItem[]) => {
  const uniq = new Set(historyModelPool.value)
  rows.forEach(x => {
    if (x.ai_model) uniq.add(x.ai_model)
  })
  historyModelPool.value = Array.from(uniq)
}

const fetchReviewHistory = async (submissionId?: number, aiModel?: string) => {
  if (!submissionId) {
    historyList.value = []
    activeHistoryId.value = null
    historyModelPool.value = []
    return
  }
  historyLoading.value = true
  try {
    const params: Record<string, any> = { limit: 50 }
    if (aiModel) params.ai_model = aiModel
    const res = await axios.get(`http://127.0.0.1:8000/ai/review/history/${submissionId}`, { params })
    const rows = Array.isArray(res.data) ? res.data : []
    historyList.value = rows
    if (!aiModel) {
      historyModelPool.value = []
      syncHistoryModelPool(rows)
    } else {
      syncHistoryModelPool(rows)
    }
    activeHistoryId.value = historyList.value.some(x => x.id === activeHistoryId.value) ? activeHistoryId.value : null
  } catch {
    historyList.value = []
    ElMessage.warning('获取AI评测历史失败')
  } finally {
    historyLoading.value = false
  }
}

const onHistoryFilterChange = async () => {
  if (!currSub.value) return
  await fetchReviewHistory(currSub.value.id, historyFilterModel.value || undefined)
}

const clearCurrentHistory = async () => {
  if (!currSub.value) return ElMessage.warning(`请先选择${reviewTargetLabel.value}提交记录`)
  if (!window.confirm('确定清空当前提交的全部AI评测历史吗？')) return

  historyLoading.value = true
  try {
    const res = await axios.delete(`http://127.0.0.1:8000/ai/review/history/${currSub.value.id}`)
    historyList.value = []
    historyModelPool.value = []
    activeHistoryId.value = null
    historyFilterModel.value = ''
    ElMessage.success(res.data?.message || '已清空当前提交历史')
  } catch {
    ElMessage.error('清空历史失败')
  } finally {
    historyLoading.value = false
  }
}

const applyHistory = (item: ReviewHistoryItem) => {
  form.ai_feedback = item.review_text || ''
  activeHistoryId.value = item.id
}


const fetchSubs = async () => {

  const res = await axios.get(`http://127.0.0.1:8000/assignments/${aid}/submissions`)
  submissionList.value = res.data || []
}

const loadAssignmentMeta = async () => {
  const res = await axios.get(`http://127.0.0.1:8000/assignments/${aid}`)
  taskTitle.value = res.data?.title || ''
  taskCriteria.value = res.data?.ai_criteria || ''
}

const selectSubmission = async (row: SubmissionItem | null) => {
  if (!row) return
  currSub.value = row
  form.ai_feedback = row.ai_feedback || ''
  form.teacher_comment = row.teacher_comment || ''
  form.score = row.score || 0
  historyFilterModel.value = ''
  await fetchReviewHistory(row.id)
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

const runAIReview = async () => {
  if (!currSub.value) return ElMessage.warning(`请先选择${reviewTargetLabel.value}提交记录`)

  aiLoading.value = true

  const checks = criteriaLines.value.length
    ? criteriaLines.value.map((x, i) => `${i + 1}. ${x}`).join('\n')
    : '1. 核心功能正确性\n2. 异常处理与边界情况\n3. 代码规范与可维护性'

  const defaultPrompt = `请根据{functionality_checks}对${reviewTargetLabel.value}代码进行评分与反馈，并严格输出三段评分格式。`
  const defaultReportPrompt = `请根据{functionality_checks}对${reviewTargetLabel.value}报告进行结构化评分与反馈，并给出总分(0-100)与改进建议。`
  const savedConfig = getSavedModelConfig()
  const assignmentPromptTemplate = (savedConfig.prompt_template || defaultPrompt).trim()
  const reportPromptTemplate = (savedConfig.report_prompt_template || defaultReportPrompt).trim()
  const provider = getProviderConfigByModel(form.ai_model, savedConfig)


  try {
    const res = await axios.post('http://127.0.0.1:8000/ai/review', {
      code_content: currSub.value.code_content || '',
      task_type: 'assignment',
      prompt_template: assignmentPromptTemplate,
      assignment_prompt_template: assignmentPromptTemplate,
      report_prompt_template: reportPromptTemplate,
      functionality_checks: checks,
      ai_model: form.ai_model,
      submission_id: currSub.value.id,
      assignment_id: aid,
      temperature: Number(savedConfig.temperature ?? 0.2),
      max_tokens: Number(savedConfig.max_tokens ?? 100000),
      provider: {
        base_url: (provider.base_url || '').trim(),
        api_key: (provider.api_key || '').trim(),
        model_name: (provider.model_name || '').trim()
      }
    })


    form.ai_feedback = res.data?.ai_feedback || ''
    if (typeof res.data?.score === 'number') {
      form.score = Math.max(0, Math.min(100, Number(res.data.score)))
    }
    await fetchReviewHistory(currSub.value.id, historyFilterModel.value || undefined)
    if (historyList.value.length) {
      activeHistoryId.value = historyList.value[0].id
    }


    const promptTokens = Number(res.data?.prompt_tokens_submitted || 0)
    ElNotification({ title: 'AI 分析完成', message: `已使用 ${form.ai_model} 完成评测（Prompt Tokens: ${promptTokens || '未知'}）`, type: 'success' })


  } catch (error: any) {
    const message = error?.response?.data?.detail || 'AI 评测失败'
    ElMessage.error(message)
  } finally {
    aiLoading.value = false
  }
}


const submitReview = async () => {
  if (!currSub.value) return ElMessage.warning(`请先选择${reviewTargetLabel.value}提交记录`)
  if (!form.ai_feedback) return ElMessage.warning('请先生成 AI 诊断报告')

  try {
    await axios.post('http://127.0.0.1:8000/publish_report/', {
      submission_id: currSub.value.id,
      ai_model: form.ai_model,
      ai_feedback: form.ai_feedback,
      teacher_comment: form.teacher_comment,
      score: form.score,
      ai_criteria: criteriaLines.value.join('\n')
    })
    ElMessage.success('学情报告分析已发送！')
    await fetchSubs()
  } catch {
    ElMessage.error('发布失败')
  }
}

onMounted(async () => {
  await fetchSubs()
  await loadAssignmentMeta()
})
</script>

<style scoped>
.console-container { padding: 20px; background-color: #f8f9fa; min-height: 100vh; }
.code-header { background: #333; color: #fff; padding: 8px 15px; border-radius: 8px 8px 0 0; font-family: monospace; font-size: 13px; }
.code-box { background: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 0 0 8px 8px; overflow: auto; max-height: 300px; border: 1px solid #333; }
.review-card { border-radius: 10px; }
.criteria-list { margin: 0; padding-left: 18px; line-height: 1.8; color: #334155; }
.analyze-btn { width: 100%; height: 52px; margin-top: 6px; font-size: 22px; font-weight: 700; }
.history-toolbar { width: 100%; display: flex; gap: 10px; margin-bottom: 10px; }
.history-filter { flex: 1; min-width: 180px; }
.history-list { width: 100%; max-height: 220px; overflow: auto; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff; }

.history-item { padding: 10px 12px; border-bottom: 1px solid #f1f5f9; cursor: pointer; }
.history-item:last-child { border-bottom: none; }
.history-item:hover { background: #f8fafc; }
.history-item.active { background: #eaf2ff; }
.history-item-title { display: flex; justify-content: space-between; font-size: 12px; color: #64748b; }
.history-item-preview { margin-top: 6px; color: #334155; font-size: 13px; line-height: 1.5; }
.team-members-text { color: #475569; font-size: 12px; line-height: 1.6; }
.score-card-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; width: 100%; }
.score-card { border-radius: 10px; }
.score-card-title { color: #64748b; font-size: 13px; }
.score-card-main { margin-top: 6px; font-size: 22px; font-weight: 700; color: #1e293b; }
.score-card-comment { margin-top: 6px; color: #334155; font-size: 12px; line-height: 1.6; }
.issue-grid { width: 100%; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
.issue-card { border-radius: 10px; min-height: 170px; }
.issue-title { color: #64748b; font-size: 13px; margin-bottom: 6px; }
.issue-list { margin: 0; padding-left: 18px; color: #334155; line-height: 1.7; }
pre { margin: 0; font-family: 'Consolas', monospace; }

</style>