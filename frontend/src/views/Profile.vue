<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <el-col :span="10">
        <el-card shadow="never" class="card-box">
          <template #header>
            <div class="card-header">
              <span>👤 个人能力画像</span>
              <el-tag type="success">AI 实时分析中</el-tag>
            </div>
          </template>
          
          <el-form label-position="top">
            <el-form-item label="我的技术栈 (用逗号分隔)">
              <el-input v-model="profile.skills" placeholder="例如: Python, Vue, 深度学习" />
            </el-form-item>
            <el-form-item label="个人简介">
              <el-input type="textarea" v-model="profile.bio" :rows="3" placeholder="介绍一下你自己..." />
            </el-form-item>
            <el-button type="primary" @click="saveProfile" style="width: 100%">保存个人资料</el-button>
          </el-form>

          <el-divider>能力维度分析 (基于历史成绩)</el-divider>
          <div id="radar-chart" style="width: 100%; height: 350px;"></div>
        </el-card>
      </el-col>

      <el-col :span="14">
        <el-card shadow="never" class="card-box">
          <template #header>
            <div class="card-header">
              <span>🤝 智能组队推荐 (基于能力互补原则)</span>
              <el-button link type="primary" @click="fetchRecommendations">刷新推荐</el-button>
            </div>
          </template>

          <el-table :data="recommendList" style="width: 100%" v-loading="loading">
            <el-table-column label="推荐队友" width="120">
              <template #default="scope">
                <div style="display: flex; align-items: center; gap: 8px;">
                  <el-avatar :size="28">{{ scope.row.name[0] }}</el-avatar>
                  <span>{{ scope.row.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="skills" label="技术栈" />
            <el-table-column label="匹配度" width="100">
              <template #default="scope">
                <el-progress type="circle" :percentage="parseInt(scope.row.match_rate)" :width="40" :stroke-width="4" />
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="互补理由" />
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button type="primary" size="small" plain @click="sendInvite(scope.row.name)">邀约</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="team-status" v-if="myTeam">
            <el-divider>我的小组</el-divider>
            <div class="team-info">
              <span class="team-name">🏆 当前小组：{{ myTeam.name }}</span>
              <div class="team-members">
                <el-tag v-for="m in myTeam.members" :key="m" effect="plain">{{ m }}</el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import axios from 'axios'

interface Recommendation {
  id: number
  name: string
  skills: string
  match_rate: string
  reason: string
}

interface TeamInfo {
  name: string
  members: string[]
}

const userId = localStorage.getItem('user_id')
const profile = ref({ skills: '', bio: '' })
const recommendList = ref<Recommendation[]>([])
const myTeam = ref<TeamInfo | null>(null)
const loading = ref(false)

// 保存资料
const saveProfile = async () => {
  try {
    await axios.post('http://127.0.0.1:8000/users/profile/update/', {
      user_id: parseInt(userId!),
      bio: profile.value.bio,
      skills: profile.value.skills
    })
    ElMessage.success('个人资料已更新！')
    fetchRecommendations()
  } catch (e) { ElMessage.error('保存失败') }
}

// 获取推荐
const fetchRecommendations = async () => {
  loading.value = true
  try {
    const res = await axios.get(`http://127.0.0.1:8000/teams/recommendations/${userId}`)
    recommendList.value = res.data
  } finally { loading.value = false }
}

const sendInvite = (name: string) => ElMessage.success(`已向 ${name} 发送组队邀约，请等待回复`)

// 初始化雷达图

const initChart = async () => {
  const chartDom = document.getElementById('radar-chart');
  if (!chartDom) return;
  const myChart = echarts.init(chartDom);

  try {
    // 🌟 核心：调用后端真实计算接口
    const res = await axios.get(`http://127.0.0.1:8000/analytics/student_profile/${userId}`);
    const realData = res.data.radar_data;

    myChart.setOption({
      radar: {
        indicator: [
          { name: '代码规范', max: 100 },
          { name: '算法逻辑', max: 100 },
          { name: '工程能力', max: 100 },
          { name: '按时提交', max: 100 },
          { name: 'AI 交互', max: 100 }
        ],
        shape: 'circle',
        splitNumber: 4,
        axisName: { color: '#64748b' }
      },
      series: [{
        type: 'radar',
        data: [{
          value: realData, // 🌟 使用后端返回的真实数组
          name: '能力分布',
          areaStyle: {
            color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
              { color: 'rgba(64, 158, 255, 0.5)', offset: 0 },
              { color: 'rgba(64, 158, 255, 0.1)', offset: 1 }
            ])
          },
          lineStyle: { color: '#409EFF', width: 2 },
          symbol: 'none'
        }]
      }]
    });
  } catch (e) {
    console.error("图表数据加载失败", e);
  }
};

// Profile.vue
onMounted(async () => {
  if (!userId || userId === 'undefined') return;

  // 🌟 修改：确保作业 ID 是存在的数字，不要传 NaN
  const assignmentId = 1; // 临时先写死一个作业ID 1，或者从路由获取
  
  try {
    // 只有当 assignmentId 为数字时才发起请求
    if (assignmentId) {
      const res = await axios.get(`http://127.0.0.1:8000/my_report/${userId}/${assignmentId}`);
      profile.value.skills = res.data.skills || '';
      profile.value.bio = res.data.bio || '';
    }
  } catch (e) {
    console.warn("未找到关联作业的报告，仅加载个人资料");
  }

  fetchRecommendations();
  await nextTick();
  initChart(); // 这会调用刚才 404 的那个接口
});
</script>

<style scoped>
.profile-container { padding: 25px; background-color: #f8fafc; min-height: calc(100vh - 60px); }
.card-box { border-radius: 12px; height: 100%; }
.card-header { display: flex; justify-content: space-between; align-items: center; font-weight: bold; }
.team-info { background: #f0f9eb; padding: 15px; border-radius: 8px; margin-top: 15px; }
.team-name { display: block; margin-bottom: 10px; font-weight: bold; color: #67c23a; }
.team-members { display: flex; gap: 10px; }
</style>