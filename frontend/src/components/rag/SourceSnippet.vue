<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
    filename: string
    score: number
    content: string
    chunkIndex: number
}>()

const expanded = ref(false)

// 分数转颜色，绿色表示高分、红色表示低分，中间用黄色过渡，颜色本身比数字更直观。
function scoreColor(score: number): string {
    if (score >= 0.8) return '#059669'
    if (score >= 0.6) return '#d97706'
    return '#dc2626'
}

// 截取内容前 200 个字符作为折叠态预览，完整内容点开后才展示。
const preview = props.content.length > 200 ? props.content.slice(0, 200) + '...' : props.content
</script>

<template>
    <div class="snippet" :class="{ expanded }">
        <div class="snippet-header" @click="expanded = !expanded">
            <span class="snippet-source">{{ filename }}（片段 #{{ chunkIndex + 1 }}）</span>
            <span class="snippet-score" :style="{ color: scoreColor(score) }">{{ (score * 100).toFixed(0) }}%</span>
        </div>
        <p class="snippet-text">{{ expanded ? content : preview }}</p>
    </div>
</template>

<style scoped>
.snippet {
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 8px 10px;
    font-size: 13px;
}

.snippet.expanded {
    border-color: #93c5fd;
    background-color: #f8fafc;
}

.snippet-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    user-select: none;
}

.snippet-source {
    font-weight: 600;
    color: #374151;
}

.snippet-score {
    font-weight: 700;
    font-size: 14px;
    flex-shrink: 0;
    margin-left: 8px;
}

.snippet-text {
    margin: 6px 0 0;
    color: #4b5563;
    line-height: 1.6;
    white-space: pre-wrap;
    word-break: break-all;
}
</style>