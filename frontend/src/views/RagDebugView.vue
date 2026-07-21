<script setup lang="ts">
import { ref } from 'vue'
import { debugRetrieval, type DebugRetrievalResponse } from '../api/debug'
import RetrievalConfigPanel from '../components/rag/RetrievalConfigPanel.vue'
import RetrievalCompareTable from '../components/rag/RetrievalCompareTable.vue'

const loading = ref(false)
const error = ref('')
const results = ref<DebugRetrievalResponse | null>(null)

async function handleSearch(params: {
    query: string
    top_k: number
    strategies: string[]
    enable_rerank: boolean
}) {
    loading.value = true
    error.value = ''
    results.value = null

    try {
        results.value = await debugRetrieval(params)
    } catch (e: any) {
        error.value = e?.response?.data?.detail || e.message || '检索失败，请稍后重试'
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <div class="reg-debug-view">
        <div class="page-header">
            <h2 class="page-title">知识库检索调试</h2>
            <p class="page-desc">
                输入查询文本，对比不同检索策略的召回效果。共同命中的片段会高亮显示，
                点击各策略下方的"查看上下文预览"可以查看最终送入模型的知识库内容。
            </p>
        </div>
        <RetrievalConfigPanel @search="handleSearch" />
        <div v-if="loading" class="loading-state">检索中…</div>
        <div v-else-if="error" class="error-state">{{ error }}</div>
        <RetrievalCompareTable v-else-if="results" :results="results.results" />
        <div v-else class="hint-state">
            请输入查询并选择检索策略后点击「检索」按钮开始调试。
        </div>
    </div>
</template>

<style scoped>
.rag-debug-view {
    max-width: 1200px;
    margin: 0 auto;
    padding: 24px;
}

.page-header {
    margin-bottom: 20px;
}

.page-title {
    margin: 0 0 6px;
    font-size: 20px;
    font-weight: 700;
    color: #111827;
}

.page-desc {
    margin: 0;
    font-size: 14px;
    color: #6b7280;
    line-height: 1.6;
}

.loading-state {
    text-align: center;
    color: #6b7280;
    padding: 40px 0;
    font-size: 14px;
}

.error-state {
    text-align: center;
    color: #dc2626;
    padding: 20px 0;
    font-size: 14px;
}

.hint-state {
    text-align: center;
    color: #9ca3af;
    padding: 60px 0 40px;
    font-size: 14px;
}
</style>