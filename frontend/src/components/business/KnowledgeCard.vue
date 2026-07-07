<script setup lang="ts">
import { computed } from 'vue'

interface Snippet {
    title: string
    content: string
    source: string
}

const props = defineProps<{
    data: Record<string, unknown>
}>()

// 后端保证 snippets 字段一定存在，这里用空数组兜底只是防御性写法，避免个别一场场景下字段缺失导致模板报错
const snippets = computed(() => (props.data.snippets as Snippet[] | undefined) ?? [])
</script>

<template>
  <div class="knowledge-card">
    <p v-if="!snippets.length" class="knowledge-empty">知识库里没有找到相关说明</p>
    <div v-for="(snippet, index) in snippets" :key="index" class="knowledge-item">
      <div class="knowledge-title">{{ snippet.title }}</div>
      <p class="knowledge-content">{{ snippet.content }}</p>
      <div class="knowledge-source">来源：{{ snippet.source }}</div>
    </div>
  </div>
</template>

<style scoped>
.knowledge-card {
  margin-top: 4px;
}

.knowledge-item {
  padding: 8px 10px;
  border-radius: 6px;
  background-color: #fff;
  border: 1px solid #e5e7eb;
  margin-bottom: 6px;
}

.knowledge-title {
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
}

.knowledge-content {
  margin: 4px 0;
  font-size: 13px;
  color: #374151;
}

.knowledge-source {
  font-size: 12px;
  color: #9ca3af;
}

.knowledge-empty {
  font-size: 13px;
  color: #6b7280;
}
</style>