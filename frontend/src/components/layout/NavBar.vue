<script setup lang="ts"></script>

<template>
    <nav class="nav-bar">
        <RouterLink to="/chat" class="nav-link">对话</RouterLink>
        <RouterLink to="/documents" class="nav-link">知识库文档</RouterLink>
    </nav>
</template>

<style scoped>
.nav-bar {
    display: flex;
    gap: 16px;
    padding: 12px 24px;
    border-bottom: 1px solid #e5e7eb;
}

.nav-link {
    color: #374151;
    text-decoration: none;
    font-size: 14px;
}

.nav-link.router-link-active {
    color: #2563eb;
    font-weight: 600;
}
</style>