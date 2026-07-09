<script setup lang="ts">
import DocumentUpload from '../components/documents/DocumentUpload.vue'
import DocumentTable from '../components/documents/DocumentTable.vue'
</script>

<template>
    <div class="documents-view">
        <h2>知识库文档管理</h2>
        <DocumentUpload />
        <DocumentTable />
    </div>
</template>

<style scoped>
.documents-view {
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}
</style>