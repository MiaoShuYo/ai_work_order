<script setup lang="ts">
interface SourceInfo {
    index: number
    filename: string
    chunk_index: number
    content: string
    score: number
    page?: number | null
}

defineProps<{
    sources: SourceInfo[]
}>()

const emit = defineEmits<{
    select: [source: SourceInfo]
}>()
</script>

<template>
    <div v-if="sources.length > 0" class="source-list">
        <div class="source-list-title">引用来源</div>
        <div v-for="source in sources" :key="source.index" class="source-item" @click="emit('select', source)">
            <span class="source-index">[{{ source.index }}]</span>
            <span class="source-filename">{{ source.filename }}</span>
            <span class="source-location">
                {{ source.page ? `第 ${source.page} 页` : `片段 #${source.chunk_index + 1}` }}
            </span>
            <span class="source-arrow">→</span>
        </div>
    </div>
</template>

<style scoped>
.source-list {
    margin-top: 16px;
    border-top: 1px solid #e5e7eb;
    padding-top: 10px;
}

.source-list-title {
    font-size: 12px;
    font-weight: 600;
    color: #6b7280;
    margin-bottom: 6px;
    letter-spacing: 0.5px;
}

.source-item {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 8px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    transition: background-color 0.15s;
}

.source-item:hover {
    background-color: #f3f4f6;
}

.source-index {
    font-weight: 700;
    color: #2563eb;
    min-width: 24px;
    flex-shrink: 0;
}

.source-filename {
    color: #1f2937;
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.source-location {
    color: #9ca3af;
    font-size: 12px;
    flex-shrink: 0;
}

.source-arrow {
    color: #9ca3af;
    font-size: 12px;
    flex-shrink: 0;
    margin-left: auto;
}
</style>