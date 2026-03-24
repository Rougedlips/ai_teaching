<template>
  <div class="page-container">
    <el-card shadow="never" class="card-box">
      <template #header>
        <div class="header-row">
          <span>🤖 大模型批改参数配置</span>
          <el-button type="primary" @click="saveConfig">保存配置</el-button>
        </div>
      </template>

      <el-alert type="info" :closable="false" show-icon style="margin-bottom: 12px">
        <template #title>
          作业/报告提示词都支持占位符 <b>{functionality_checks}</b>，系统会在评测时替换为老师配置的“重点检查项”。
        </template>
      </el-alert>

      <el-form label-width="140px" :model="config" class="config-form">
        <el-form-item label="默认评测模型">
          <el-select v-model="config.model" style="width: 100%">
            <el-option label="OpenAI GPT-4o" value="GPT-4o" />
            <el-option label="DeepSeek 模型" value="DeepSeek" />
            <el-option label="阿里通义千问 (Qwen)" value="Qwen" />
            <el-option label="百度文心一言 (Ernie)" value="Ernie" />
          </el-select>
        </el-form-item>

        <section class="model-api-section">
          <div class="model-api-title">模型 API 配置</div>
          <el-tabs v-model="activeModelTab" class="model-tabs" type="card">
            <el-tab-pane v-for="item in modelTabs" :key="item.key" :label="item.label" :name="item.key">
              <div class="model-api-pane">
                <el-alert :closable="false" type="warning" show-icon class="tip-alert">
                  <template #title>
                    {{ item.tip }}
                  </template>
                </el-alert>

                <div class="api-field">
                  <div class="api-label">API 地址 / Base URL</div>
                  <el-input
                    v-model="config.providers[item.key].base_url"
                    :placeholder="item.baseUrlPlaceholder"
                    clearable
                  />
                </div>

                <div class="api-field">
                  <div class="api-label">访问密钥</div>
                  <el-input
                    v-model="config.providers[item.key].api_key"
                    type="password"
                    show-password
                    :placeholder="item.keyPlaceholder"
                    clearable
                  />
                </div>

                <div class="api-field">
                  <div class="api-label">模型名称</div>
                  <el-input
                    v-model="config.providers[item.key].model_name"
                    :placeholder="item.modelPlaceholder"
                    clearable
                  />
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </section>

        <el-form-item label="温度 (Temperature)">
          <el-slider v-model="config.temperature" :min="0" :max="1" :step="0.1" show-input />
        </el-form-item>

        <el-form-item label="最大 Token">
          <el-input-number v-model="config.max_tokens" :min="1024" :max="200000" :step="1024" />
        </el-form-item>

        <el-form-item label="批改提示词模板">
          <el-tabs v-model="activePromptTab" class="prompt-tabs" type="border-card">
            <el-tab-pane label="作业提示词" name="assignment">
              <el-input v-model="config.prompt_template" type="textarea" :rows="8" />
            </el-tab-pane>
            <el-tab-pane label="报告提示词" name="report">
              <el-input v-model="config.report_prompt_template" type="textarea" :rows="8" />
            </el-tab-pane>
          </el-tabs>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import defaultPromptTemplate from './modelpromt.md?raw'

type ProviderKey = 'gpt4o' | 'deepseek' | 'qwen' | 'ernie'

const storageKey = 'ai_review_model_config'

const modelTabs: Array<{
  key: ProviderKey
  label: string
  tip: string
  baseUrlPlaceholder: string
  keyPlaceholder: string
  modelPlaceholder: string
  modelOptions?: Array<{ label: string; value: string }>
}> = [
  {
    key: 'gpt4o',
    label: 'OpenAI GPT-4o',
    tip: '启用后将使用 OpenAI Chat Completions 接口。',
    baseUrlPlaceholder: 'https://api.openai.com/v1',
    keyPlaceholder: 'sk-xxx',
    modelPlaceholder: 'gpt-4o'
  },
  {
    key: 'deepseek',
    label: 'DeepSeek Coder',
    tip: '启用后将调用 DeepSeek OpenAI 兼容接口。',
    baseUrlPlaceholder: 'https://api.deepseek.com/v1',
    keyPlaceholder: 'sk-xxx',
    modelPlaceholder: 'deepseek-coder'
  },
  {
    key: 'qwen',
    label: '阿里通义千问 (Qwen)',
    tip: '推荐使用阿里云百炼平台兼容 OpenAI 的接口地址。',
    baseUrlPlaceholder: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    keyPlaceholder: 'sk-xxx',
    modelPlaceholder: 'qwen-plus'
  },
  {
    key: 'ernie',
    label: '百度文心一言 (Ernie)',
    tip: '启用后将使用千帆平台 OpenAI 兼容接口。',
    baseUrlPlaceholder: 'https://qianfan.baidubce.com/v2',
    keyPlaceholder: 'bce-v3/ak-sk-xxx',
    modelPlaceholder: 'ernie-4.0-8k'
  }
]

const modelToTab: Record<string, ProviderKey> = {
  'GPT-4o': 'gpt4o',
  DeepSeek: 'deepseek',
  Qwen: 'qwen',
  Ernie: 'ernie'
}

const defaultReportPromptTemplate = `你是一名教学助教。请根据{functionality_checks}对学生上传的报告文档进行结构化评测，覆盖：
1) 报告结构完整性
2) 技术内容准确性
3) 结论与数据一致性
4) 表达规范性
并给出总分(0-100)与改进建议。`

const config = reactive({
  model: 'DeepSeek',
  temperature: 0.2,
  max_tokens: 100000,
  prompt_template: (defaultPromptTemplate || '').trim(),
  report_prompt_template: defaultReportPromptTemplate,
  providers: {
    gpt4o: {
      base_url: 'https://api.openai.com/v1',
      api_key: '',
      model_name: 'gpt-4o'
    },
    deepseek: {
      base_url: 'https://api.deepseek.com/v1',
      api_key: '',
      model_name: 'deepseek-coder'
    },
    qwen: {
      base_url: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
      api_key: '',
      model_name: 'qwen-plus'
    },
    ernie: {
      base_url: 'https://qianfan.baidubce.com/v2',
      api_key: '',
      model_name: 'ernie-4.0-8k'
    }
  }
})

const activeModelTab = ref<ProviderKey>(modelToTab[config.model] || 'deepseek')
const activePromptTab = ref<'assignment' | 'report'>('assignment')

const saved = localStorage.getItem(storageKey)
if (saved) {
  try {
    const parsed = JSON.parse(saved)
    if (parsed && typeof parsed === 'object') {
      Object.assign(config, {
        model: parsed.model ?? config.model,
        temperature: parsed.temperature ?? config.temperature,
        max_tokens: parsed.max_tokens ?? config.max_tokens,
        prompt_template: parsed.prompt_template ?? config.prompt_template,
        report_prompt_template: parsed.report_prompt_template ?? config.report_prompt_template
      })

      if (parsed.providers && typeof parsed.providers === 'object') {
        modelTabs.forEach(item => {
          const provider = parsed.providers[item.key]
          if (provider && typeof provider === 'object') {
            Object.assign(config.providers[item.key], {
              base_url: provider.base_url ?? config.providers[item.key].base_url,
              api_key: provider.api_key ?? config.providers[item.key].api_key,
              model_name: provider.model_name ?? config.providers[item.key].model_name
            })
          }
        })
      }
    }
  } catch {
    // ignore invalid cache
  }
}

watch(
  () => config.model,
  model => {
    activeModelTab.value = modelToTab[model] || 'deepseek'
  },
  { immediate: true }
)

const saveConfig = () => {
  localStorage.setItem(storageKey, JSON.stringify(config))
  ElMessage.success('参数配置已保存')
}
</script>

<style scoped>
.page-container { padding: 24px; background: #f8fafc; min-height: calc(100vh - 60px); }
.card-box { border-radius: 12px; }
.header-row { display: flex; justify-content: space-between; align-items: center; font-weight: 700; }
.config-form { max-width: 980px; }
.model-api-section { margin-bottom: 18px; }
.model-api-title {
  margin: 0 0 10px;
  font-size: 14px;
  color: var(--el-text-color-regular);
  font-weight: 600;
}
.model-tabs { width: 100%; }
.model-api-pane { padding: 10px 4px 0; }
.tip-alert { margin-bottom: 14px; }
.api-field { margin-bottom: 14px; }
.api-label {
  margin-bottom: 6px;
  color: var(--el-text-color-regular);
  font-size: 14px;
  line-height: 1.4;
}
.prompt-tabs { width: 100%; }
</style>
