<script setup lang="ts">
defineProps<{
    actions: string[]
}>()

const emit = defineEmits<{
    select: [action: string]
}>()
</script>

<template>
    <div v-if="actions.length" class="suggested-actions">
        <span class="label">建议操作</span>
        <button v-for="action in actions" :key="action" class="action-button" @click="emit('select', action)">
            {{ action }}
        </button>
    </div>
</template>

<style scoped>
.suggested-actions {
    margin-top: 8px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
}
.label {
    font-size: 12px;
    color: #6b7280;
}
.action-button {
    padding: 4px 10px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 12px;
    cursor: pointer;
}
.action-button:hover {
    background-color: #2563eb;
    color: #ffffff;
}
</style>