<script setup lang="ts">
defineProps<{
    status: string
    chunkCount: number
    error: string | null
}>()


const STATUS_COLOR: Record<string, string> = {
    解析中: '#f59e0b',
    切片完成: '#0891b2',
    向量化中: '#7c3aed',
    可检索: '#059669',
    失败: '#dc2626',
}
</script>

<template>
    <div class="status-cell">
        <span class="status-tag" :style="{ color: STATUS_COLOR[status] }">{{ chunkCount }} 个片段</span>
    </div>
</template>

<style scoped>
.status-cell {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.status-tag {
    font-weight: 600;
    font-size: 13px;
}

.chunk-count {
    font-size: 12px;
    color: #6b7280;
}

.error-tip {
    font-size: 12px;
    color: #dc2626;
}
</style>