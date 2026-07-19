<script setup lang="ts">
import { reactive } from 'vue';

const emit = defineEmits<{
    search: [params: { query: string; top_k: number; strategies: string[]; enable_rerank: boolean }]
}>()

const state = reactive({
    query: '',
    top_k: 5,
    strategies: ['vector', 'keyword', 'hybrid'] as string[],
    enable_rerank: false
})

const ALL_STRATEGIES = [
    { value: 'vector', label: '向量检索' },
    { value: 'keyword', label: '关键词检索' },
    { value: 'hybrid', label: '混合检索' },
]

function toggleStrategy(strategy: string) {
    const index = state.strategies.indexOf(strategy)
    if (index === -1) {
        state.strategies.push(strategy)
    } else if (state.strategies.length > 1) {
        // 至少保留一种策略，不允许全部取消
        state.strategies.splice(index, 1)
    }
}

function handleSearch() {
    if (!state.query.trim()) return
    emit('search', { ...state, query: state.query.trim() })
}
</script>

<template>
    <div class="config-panel">
        <div class="query-row">
            <input v-model="state.query" type="text" class="query-input" placeholder="输入检索查询，例如：7 天无理由退款的到账时间是多久"
                @keyup.enter="handleSearch" />
            <button class="search-btn" :disabled="!state.query.trim()" @click="handleSearch">检索</button>
        </div>
        <div class="params-row">
            <div class="param-group">
                <label class="param-label">Top-K: {{ state.top_k }}</label>
                <input v-model.number="state.top_k" type="range" min="1" max="20" class="slider" />
            </div>
            <div class="param-group">
                <label class="param-label">检索策略</label>
                <div class="strategy-checkboxes">
                    <label v-for="s in ALL_STRATEGIES" :key="s.value" class="checkbox-label"
                        :class="{ checked: state.strategies.includes(s.value) }">
                        <input type="checkbox" :checked="state.strategies.includes(s.value)"
                            @change="toggleStrategy(s.value)" />{{ s.label }}
                    </label>
                </div>
            </div>
            <div class="param-group">
                <label class="checkbox-label" :class="{ checked: state.enable_rerank }">
                    <input type="checkbox" :checked="state.enable_rerank"
                        @change="state.enable_rerank = !state.enable_rerank" />
                    启用重排序（FlashRank）
                </label>
            </div>
        </div>
    </div>
</template>

<style scoped>
.config-panel {
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 20px;
}

.query-row {
    display: flex;
    gap: 8px;
    margin-bottom: 14px;
}

.query-input {
    flex: 1;
    padding: 8px 12px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 14px;
    outline: none;
    transition: border-color 0.15s;
}

.query-input:focus {
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.search-btn {
    padding: 8px 20px;
    background: #2563eb;
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    white-space: nowrap;
    transition: background-color 0.15s;
}

.search-btn:hover:not(:disabled) {
    background: #1d4ed8;
}

.search-btn:disabled {
    background: #9ca3af;
    cursor: not-allowed;
}

.params-row {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    align-items: flex-end;
}

.param-group {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.param-label {
    font-size: 13px;
    color: #6b7280;
    font-weight: 500;
}

.slider {
    width: 120px;
    accent-color: #2563eb;
}

.strategy-checkboxes {
    display: flex;
    gap: 12px;
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 13px;
    color: #374151;
    cursor: pointer;
    user-select: none;
    padding: 4px 8px;
    border-radius: 4px;
    transition: background-color 0.15s;
}

.checkbox-label.checked {
    background: #eff6ff;
    color: #2563eb;
}
</style>