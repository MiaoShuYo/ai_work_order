<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useDocumentsStore } from '../../stores/documents';
import IndexStatusTag from './IndexStatusTag.vue';
import DocumentProcessLog from './DocumentProcessLog.vue';

const store = useDocumentsStore()
const expandedId = ref<string | null>(null)

function formatSize(bytes: number): string {
    return bytes < 1024 * 1024 ? `${(bytes / 1024).toFixed(1)} KB` : `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function toggleLog(docId: string) {
    expandedId.value = expandedId.value == docId ? null : docId
}

onMounted(async () => {
    await store.fetchDocuments()
    store.startPolling()
})
onUnmounted(() => {
    store.stopPolling()
})
</script>

<template>
    <table class="doc-table">
        <thead>
            <tr>
                <th>文件名</th>
                <th>类型</th>
                <th>大小</th>
                <th>状态</th>
                <th>上传时间</th>
                <th></th>
            </tr>
        </thead>
        <tbody>
            <template v-for="doc in store.documents" :key="doc.id">
                <tr>
                    <td>{{ doc.filename }}</td>
                    <td>{{ doc.file_type }}</td>
                    <td>{{ formatSize(doc.size) }}</td>
                    <td>
                        <IndexStatusTag :status="doc.status" :chunk-count="doc.chunk_count" :error="doc.error" />
                    </td>
                    <td>{{ new Date(doc.uploaded_at).toLocaleString() }}</td>
                    <td>
                        <button type="button" @click="toggleLog(doc.id)">查看日志</button>
                    </td>
                </tr>
                <tr v-if="expandedId === doc.id">
                    <td colspan="6">
                        <DocumentProcessLog :document-id="doc.id" />
                    </td>
                </tr>
            </template>
        </tbody>
    </table>
</template>

<style scoped>
.doc-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}

.doc-table th,
.doc-table td {
    padding: 8px 12px;
    text-align: left;
    border-bottom: 1px solid #e5e7eb;
}
</style>