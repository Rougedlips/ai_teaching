<template>
  <div class="workspace-container">
    <el-row :gutter="20" class="workspace-row">
      <el-col :span="8" class="left-panel">
        <el-card shadow="never" class="task-card">
          <template #header><div class="card-header"><span>📄 作业详情</span></div></template>
          <h2 style="margin-top: 0; color: #303133;">任务：{{ currentTask.title || '加载中...' }}</h2>
          <div class="task-desc-container">
            <p class="task-desc">{{ currentTask.description || '正在获取任务详情，请稍后...' }}</p>
          </div>
          <p style="color: #F56C6C; font-weight: bold; margin-top: 15px;">截止时间：{{ currentTask.deadline || '-' }}</p>
        </el-card>

        <el-card shadow="never" class="ai-feedback-card" style="margin-top: 20px;">
          <template #header><span>📊 本题学情报告</span></template>
          <div v-if="reportStatus === 'none'"><el-empty description="本题暂未提交代码" :image-size="80" /></div>
          <div v-else-if="reportStatus === 'pending'"><el-empty description="已存入数据库，等待批阅..." :image-size="80" /></div>
          <div v-else-if="reportStatus === 'finished'">
            <el-tag type="success" size="large" style="margin-bottom:10px;">得分：{{ finalScore }}</el-tag>
            <div style="font-weight:bold; color:#409EFF;">老师评语：</div>
            <p class="comment-box">{{ finalTeacherComment }}</p>
            <el-divider border-style="dashed" />
            <p style="color: #606266; font-size: 13px;">🤖 AI 日志：{{ finalAIFeedback }}</p>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16" class="right-panel">
        <el-card shadow="never" class="editor-card">
          <div class="toolbar">
            <el-button type="info" size="small" @click="$router.push('/')">⬅ 返回列表</el-button>
            <div style="margin-left: auto;">
              <el-upload action="#" :auto-upload="false" :on-change="handleBatchUpload" :show-file-list="false" multiple style="display:inline-block; margin-right:10px;">
                <el-button type="warning" plain size="small">📂 批量导入</el-button>
              </el-upload>
              <el-button type="success" size="small" @click="submitCode">🚀 提交代码</el-button>
              <el-button type="primary" plain size="small" @click="checkReport">刷新报告</el-button>
            </div>
          </div>
          
          <div class="ide-container">
            <el-tabs v-model="activeFileName" type="card" editable @edit="handleTabsEdit">
              <el-tab-pane v-for="file in fileList" :key="file.name" :label="file.name" :name="file.name">
                <VueMonacoEditor 
                  v-if="activeFileName === file.name" 
                  v-model:value="file.content" 
                  theme="vs-dark" 
                  language="python" 
                  height="550px" 
                  :options="{ automaticLayout: true, fontSize: 14 }" 
                />
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
// 🌟 核心：不仅要引入，还要确保导出名称匹配
import { VueMonacoEditor } from '@guolao/vue-monaco-editor'

const route = useRoute()
const assignmentId = Number(route.query.id)

const currentTask = ref({ id: assignmentId, title: '', description: '', deadline: '' })
const reportStatus = ref('none')
const finalScore = ref(0)
const finalTeacherComment = ref('')
const finalAIFeedback = ref('')

const fileList = ref([{ name: 'main.py', content: '# 请在此开始作答\n' }])
const activeFileName = ref('main.py')

// 🌟 核心：彻底解决 user_id 为空的问题
const getValidUserId = () => {
  let uid = localStorage.getItem('user_id')
  // 过滤掉各种奇葩的空值情况
  if (!uid || uid === 'null' || uid === 'undefined' || uid === '[object Object]') {
    return 1 // 强制保底为 1 号学生，确保请求能发出去
  }
  return Number(uid)
}

const handleBatchUpload = (f: any) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    const content = e.target?.result as string
    const exist = fileList.value.find(file => file.name === f.raw.name)
    if (exist) exist.content = content
    else fileList.value.push({ name: f.raw.name, content: content })
    activeFileName.value = f.raw.name
  }
  reader.readAsText(f.raw)
}

const handleTabsEdit = (target: any, action: 'add' | 'remove') => {
  if (action === 'add') {
    const name = `file_${fileList.value.length + 1}.py`
    fileList.value.push({ name: name, content: '' })
    activeFileName.value = name
  } else {
    fileList.value = fileList.value.filter(f => f.name !== target)
    if (activeFileName.value === target) {
      const firstFile = fileList.value[0]
      activeFileName.value = firstFile ? firstFile.name : ''
    }
  }
}

const fetchTaskDetail = async () => {
  if (!assignmentId) return
  try {
    const res = await axios.get(`http://127.0.0.1:8000/assignments/${assignmentId}`)
    currentTask.value = res.data
  } catch (e) { 
    console.error('获取任务失败')
    currentTask.value.title = "任务加载失败"
  }
}

const submitCode = async () => {
  const uid = getValidUserId()
  let content = ''
  fileList.value.forEach(f => content += `# File: ${f.name}\n${f.content}\n`)
  try {
    await axios.post('http://127.0.0.1:8000/submissions/', {
      assignment_id: assignmentId,
      student_id: uid,
      code_content: content
    })
    ElMessage.success('提交成功！')
    reportStatus.value = 'pending'
  } catch (e) { ElMessage.error('提交失败') }
}

const checkReport = async () => {
  const uid = getValidUserId()
  try {
    const res = await axios.get(`http://127.0.0.1:8000/my_report/${uid}/${assignmentId}`)
    const d = res.data
    reportStatus.value = d.status
    if (d.status === 'finished') {
      finalScore.value = d.score
      finalTeacherComment.value = d.teacher_comment
      finalAIFeedback.value = d.ai_feedback
    }
  } catch (e) {}
}

onMounted(() => {
  fetchTaskDetail()
  checkReport()
})
</script>

<style scoped>
.workspace-container { padding: 20px; height: calc(100vh - 80px); }
.workspace-row { height: 100%; }
.task-desc-container { background: #f4f4f5; padding: 15px; border-radius: 8px; margin-top: 10px; min-height: 100px; }
.comment-box { background: #eef5fe; padding: 10px; border-radius: 4px; margin-top: 5px; }
.toolbar { margin-bottom: 15px; display: flex; align-items: center; border-bottom: 1px solid #f0f0f0; padding-bottom: 10px; }
.ide-container { border: 1px solid #ebeef5; border-radius: 8px; overflow: hidden; background: #fff; }
</style>