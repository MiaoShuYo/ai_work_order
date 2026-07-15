<script setup lang="ts">
import { onMounted } from 'vue';
import { useDocumentsStore } from '../../stores/documents';

const store = useDocumentsStore()

const STATUS_COLOR: Record<string, string> = {
    处理中: '#f59e0b',
    已完成: '#059669',
    失败: '#dc2626',
}

function formatSize(bytes: number): string {
    return bytes < 1024 * 1024 ? `${(bytes / 1024).toFixed(1)} KB` : `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

onMounted(() => {
    store.fetchDocuments()
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
            </tr>
        </thead>
        <tbody>
            <tr v-for="doc in store.documents" :key="doc.id">
                <td>{{ doc.filename }}</td>
                <td>{{ doc.file_type }}</td>
                <td>{{ formatSize(doc.size) }}</td>
                <td>
                    <span class="status-tag" :style="{ color: STATUS_COLOR[doc.status] }">{{ doc.status }}</span>
                    <span v-if="doc.error" class="error-tip">{{ doc.error }}</span>
                </td>
                <td>{{ new Date(doc.uploaded_at).toLocaleString() }}</td>
            </tr>
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

.status-tag {
    font-weight: 600;
}

.error-tip {
    display: block;
    color: #dc2626;
    font-size: 12px;
    margin-top: 2px;
}
</style>