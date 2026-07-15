<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { DocumentLogEntry, useDocumentsStore } from '../../stores/documents'

const props = defineProps<{ documentId: string }>()
const store = useDocumentsStore()
const logs = ref<DocumentLogEntry[]>([])
const loading = ref(false)

onMounted(async () => {
    loading.value = true
    try {
        logs.value = await store.fetchDocumentLogs(props.documentId)
    } finally {
        loading.value = false
    }
})
</script>

<template>
    <div class="process-log">
        <p v-if="loading">日志加载中...</p>
        <ul v-else class="log-list">
            <li v-for="log in logs" :key="log.id">
                <span class="log-step">{{ log.step }}</span>
                <span class="log-message">{{ log.message }}</span>
                <span class="log-time">{{ new Date(log.created_at).toLocaleTimeString() }}</span>
            </li>
        </ul>
    </div>
</template>

<style scoped>
.process-log {
    padding: 8px 12px;
    background-color: #f9fafb;
    border-radius: 6px;
    font-size: 13px;
}

.log-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.log-step {
    font-weight: 600;
    margin-right: 8px;
}

.log-time {
    float: right;
    color: #9ca3af;
}
</style>