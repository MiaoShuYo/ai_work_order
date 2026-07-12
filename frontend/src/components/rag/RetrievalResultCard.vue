<script setup lang="ts">
import SourceSnippet from './SourceSnippet.vue'

export interface SearchSnippet {
    content: string
    score: number
    document_id: string
    filename: string
    chunk_index: number
}

defineProps<{
    snippets: SearchSnippet[]
}>()
</script>

<template>
  <div class="retrieval-card">
    <div class="retrieval-summary">
      检索到 <strong>{{ snippets.length }}</strong> 个相关片段
    </div>
    <div v-if="snippets.length === 0" class="retrieval-empty">
      未在知识库中找到相关内容
    </div>
    <div v-else class="snippet-list">
      <SourceSnippet
        v-for="(snippet, index) in snippets"
        :key="index"
        :filename="snippet.filename"
        :score="snippet.score"
        :content="snippet.content"
        :chunk-index="snippet.chunk_index"
      />
    </div>
  </div>
</template>

<style scoped>
.retrieval-card {
    font-size: 14px;
}

.retrieval-summary {
    margin-bottom: 8px;
    color: #6b7280;
    font-size: 13px;
}

.retrieval-empty {
    color: #9ca3af;
    font-style: italic;
}

.snippet-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
</style>