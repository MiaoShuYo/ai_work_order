<script setup lang="ts">
import { computed, watch } from 'vue'

interface SourceInfo {
    index: number
    filename: string
    chunk_index: number
    content: string
    score: number
    page?: number | null
}

const props = defineProps<{
    source: SourceInfo | null
    visible: boolean
}>()

const emit = defineEmits<{
    close: []
}>()

// 面板可见时禁止页面滚动，关闭时恢复
watch(
    () => props.visible,
    (v) => {
        document.body.style.overflow = v ? 'hidden' : ''
    }
)

const scorePercent = computed(() => (props.source ? (props.source.score * 100).toFixed(0) + '%' : ''))

const locationText = computed(() => {
    if (!props.source) return ''
    return props.source.page ? `第 ${props.source.page} 页` : `片段 #${props.source.chunk_index + 1}`
})

function copyContent() {
    if (!props.source) return
    navigator.clipboard.writeText(props.source.content).catch(() => {
        // 兜底：某些浏览器或非 HTTPS 环境下 clipboard API 不可用
        const textarea = document.createElement('textarea')
        textarea.value = props.source!.content
        document.body.appendChild(textarea)
        textarea.select()
        document.execCommand('copy')
        document.body.removeChild(textarea)
    })
}

function goToDocument() {
    if (!props.source) return
    // 跳转到文档详情页，路径格式如 /documents/{document_id}，
    // 这里暂时通过 router 跳转，document_id 从 SourceInfo 里取。
    // 实际跳转逻辑取决于项目中路由和文档详情页的实现。
}
</script>

<template>
    <Teleport to="body">
        <div v-if="visible" class="drawer-overlay" @click.self="emit('close')">
            <div class="drawer-panel">
                <div class="drawer-header">
                    <h3 class="drawer-title">引用来源详情</h3>
                    <button class="drawer-close" @click="emit('close')">✕</button>
                </div>

                <div v-if="source" class="drawer-body">
                    <div class="source-meta">
                        <div class="meta-row">
                            <span class="meta-label">来源文档</span>
                            <span class="meta-value">{{ source.filename }}</span>
                        </div>
                        <div class="meta-row">
                            <span class="meta-label">位置</span>
                            <span class="meta-value">{{ locationText }}</span>
                        </div>
                        <div class="meta-row">
                            <span class="meta-label">相关度</span>
                            <span class="meta-value score" :class="{
                                'score-high': source.score >= 0.8,
                                'score-mid': source.score >= 0.6 && source.score < 0.8,
                                'score-low': source.score < 0.6,
                            }">
                                {{ scorePercent }}
                            </span>
                        </div>
                    </div>

                    <div class="source-content">
                        <div class="content-label">原文片段</div>
                        <pre class="content-text">{{ source.content }}</pre>
                    </div>
                </div>

                <div v-if="source" class="drawer-footer">
                    <button class="footer-btn" @click="copyContent">复制原文</button>
                    <button class="footer-btn secondary" @click="goToDocument">查看文档</button>
                </div>
            </div>
        </div>
    </Teleport>
</template>

<style scoped>
.drawer-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.3);
    z-index: 1000;
    display: flex;
    justify-content: flex-end;
}

.drawer-panel {
    width: 440px;
    max-width: 90vw;
    height: 100%;
    background: #fff;
    box-shadow: -4px 0 16px rgba(0, 0, 0, 0.08);
    display: flex;
    flex-direction: column;
    animation: slideIn 0.2s ease-out;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
    }

    to {
        transform: translateX(0);
    }
}

.drawer-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    border-bottom: 1px solid #e5e7eb;
    flex-shrink: 0;
}

.drawer-title {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #111827;
}

.drawer-close {
    background: none;
    border: none;
    font-size: 18px;
    color: #6b7280;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 4px;
}

.drawer-close:hover {
    background: #f3f4f6;
    color: #111827;
}

.drawer-body {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
}

.source-meta {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 20px;
}

.meta-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
}

.meta-label {
    color: #6b7280;
    flex-shrink: 0;
}

.meta-value {
    color: #1f2937;
    font-weight: 500;
    text-align: right;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 60%;
}

.score-high {
    color: #059669;
}

.score-mid {
    color: #d97706;
}

.score-low {
    color: #dc2626;
}

.source-content {
    border-top: 1px solid #e5e7eb;
    padding-top: 16px;
}

.content-label {
    font-size: 13px;
    font-weight: 600;
    color: #6b7280;
    margin-bottom: 8px;
}

.content-text {
    margin: 0;
    padding: 12px;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    font-size: 13px;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-all;
    color: #374151;
    max-height: 360px;
    overflow-y: auto;
}

.drawer-footer {
    display: flex;
    gap: 8px;
    padding: 12px 20px;
    border-top: 1px solid #e5e7eb;
    flex-shrink: 0;
}

.footer-btn {
    flex: 1;
    padding: 8px 0;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    background: #2563eb;
    color: #fff;
    transition: background-color 0.15s;
}

.footer-btn:hover {
    background: #1d4ed8;
}

.footer-btn.secondary {
    background: #f3f4f6;
    color: #374151;
}

.footer-btn.secondary:hover {
    background: #e5e7eb;
}
</style>