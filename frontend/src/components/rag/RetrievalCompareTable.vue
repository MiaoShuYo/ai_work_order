<script setup lang="ts">
import { computed, ref } from 'vue'
import type { StrategyResult } from '../../api/debug'
import SourceSnippet from './SourceSnippet.vue'

const props = defineProps<{
  results: StrategyResult[]
}>()

// 当前选中的策略名，用于展示上下文预览
const selectedStrategy = ref<string | null>(null)

// 上下文预览是否展开
const showContextPreview = ref(false)

const selectedResult = computed(() => {
  if (!selectedStrategy.value) return props.results[0] || null
  return props.results.find((r) => r.strategy === selectedStrategy.value) || null
})

// 把所有策略的片段按 content 去重后合并，用来判断某条片段在哪些策略中出现过 content 相同的片段视为同一条，不管 metadata 是否完全一致
const allContents = computed(() => {
  const contentMap = new Map<string, Set<string>>()
  for (const result of props.results) {
    for (const snippet of result.snippets) {
      if (!contentMap.has(snippet.content)) {
        contentMap.set(snippet.content, new Set())
      }
      contentMap.get(snippet.content)!.add(result.strategy)
    }
  }
  return contentMap
})

// 判断某条片段是否被多种策略同时命中
function isCommonHit(content: string): boolean {
  const strategies = allContents.value.get(content)
  return strategies ? strategies.size > 1 : false
}

function copyToClipboard(text: string) {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text)
    return
  }
  // 非 HTTPS 或旧浏览器的降级方案
  const textarea = document.createElement('textarea')
  textarea.value = text
  document.body.appendChild(textarea)
  textarea.select()
  document.execCommand('copy')
  document.body.removeChild(textarea)
}

function toggleContextPreview(strategy: string) {
  if (selectedStrategy.value === strategy && showContextPreview.value) {
    showContextPreview.value = false
    return
  }
  selectedStrategy.value = strategy
  showContextPreview.value = true
}
</script>

<template>
  <div v-if="results.length === 0" class="empty-state">
    暂无检索结果，请先输入查询并选择至少一种检索策略。
  </div>

  <div v-else class="compare-container">
    <!-- 横向滚动的策略列 -->
    <div class="compare-scroll">
      <div
        v-for="result in results"
        :key="result.strategy"
        class="strategy-column"
      >
        <div class="column-header">
          <span class="strategy-name">{{ result.strategy }}</span>
          <span class="strategy-meta">
            {{ result.snippets.length }} 条 · {{ result.elapsed_ms.toFixed(0) }} ms
          </span>
        </div>

        <div v-if="result.snippets.length === 0" class="column-empty">
          未命中任何片段
        </div>

        <div v-else class="snippet-list">
          <div
            v-for="(snippet, index) in result.snippets"
            :key="index"
            class="snippet-wrapper"
            :class="{ 'common-hit': isCommonHit(snippet.content) }"
          >
            <SourceSnippet
              :filename="snippet.filename"
              :score="snippet.score"
              :content="snippet.content"
              :chunk-index="snippet.chunk_index"
            />
          </div>
        </div>

        <button
          class="context-toggle"
          @click="toggleContextPreview(result.strategy)"
        >
          {{ selectedStrategy === result.strategy && showContextPreview ? '收起上下文' : '查看上下文预览' }}
        </button>
      </div>
    </div>

    <!-- 上下文预览面板 -->
    <div v-if="showContextPreview && selectedResult" class="context-panel">
      <div class="context-header">
        <span>上下文预览 — {{ selectedResult.strategy }}</span>
        <button class="context-copy" @click="copyToClipboard(selectedResult.context_preview)">
          复制
        </button>
      </div>
      <pre class="context-text">{{ selectedResult.context_preview }}</pre>
    </div>
  </div>
</template>

<style scoped>
.empty-state {
  text-align: center;
  color: #9ca3af;
  padding: 40px 0;
  font-size: 14px;
}

.compare-container {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.compare-scroll {
  display: flex;
  overflow-x: auto;
  gap: 0;
}

.strategy-column {
  flex: 1;
  min-width: 280px;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
}

.strategy-column:last-child {
  border-right: none;
}

.column-header {
  padding: 12px 14px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
  gap: 2px;
  position: sticky;
  top: 0;
}

.strategy-name {
  font-weight: 700;
  font-size: 14px;
  color: #111827;
  text-transform: capitalize;
}

.strategy-meta {
  font-size: 12px;
  color: #6b7280;
}

.column-empty {
  padding: 20px 14px;
  text-align: center;
  color: #9ca3af;
  font-size: 13px;
}

.snippet-list {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.snippet-wrapper {
  border-radius: 4px;
  transition: background-color 0.15s;
}

/* 被多种策略同时命中的片段高亮显示，用一个浅蓝色背景区分 */
.snippet-wrapper.common-hit {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  padding: 2px;
}

.context-toggle {
  margin: 8px 14px 12px;
  padding: 6px 0;
  background: none;
  border: none;
  color: #2563eb;
  font-size: 13px;
  cursor: pointer;
  text-align: left;
}

.context-toggle:hover {
  text-decoration: underline;
}

.context-panel {
  border-top: 1px solid #e5e7eb;
  padding: 14px 18px;
  background: #f9fafb;
}

.context-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.context-copy {
  padding: 4px 12px;
  background: #fff;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  color: #374151;
}

.context-copy:hover {
  background: #f3f4f6;
}

.context-text {
  margin: 0;
  padding: 12px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 13px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-all;
  color: #374151;
  max-height: 300px;
  overflow-y: auto;
}
</style>