<script setup lang="ts">
import { useSessionStore } from '../../stores/sessionStore'

// AI 回答流式生成期间禁用一切会话切换，防止中途换会话导致事件错挂
defineProps<{ disabled?: boolean }>()

const { state, currentSession, initSessions, createNewSession, selectSession, removeSession } =
    useSessionStore()

async function handleCreate() {
    if (state.loading) return
    try {
        await createNewSession()
    } catch (error) {
        window.alert(error instanceof Error ? error.message : '创建会话失败')
    }
}

async function handleDelete(event: MouseEvent, sessionId: string, title: string) {
    // 删除按钮嵌在列表项里，不阻止冒泡会同时触发选中
    event.stopPropagation()
    if (!window.confirm(`确定删除会话“${title}”吗？历史消息将一并删除。`)) return
    try {
        await removeSession(sessionId)
    } catch (error) {
        window.alert(error instanceof Error ? error.message : '删除会话失败')
    }
}

// 组件挂载即初始化，store 内部有幂等保护，重复调用不会重复请求
void initSessions()
</script>

<template>
  <aside class="session-list">
    <div class="session-list-header">
      <span class="session-list-title">会话列表</span>
      <button class="create-btn" :disabled="disabled" @click="handleCreate">＋ 新建</button>
    </div>

    <div v-if="state.loading" class="session-tip">加载中……</div>
    <div v-else-if="state.sessions.length === 0" class="session-tip">暂无会话</div>

    <ul v-else class="session-items">
      <li
        v-for="session in state.sessions"
        :key="session.session_id"
        class="session-item"
        :class="{ active: session.session_id === currentSession?.session_id, disabled }"
        @click="!disabled && selectSession(session.session_id)"
      >
        <span class="session-name" :title="session.title">{{ session.title }}</span>
        <button
          class="delete-btn"
          title="删除会话"
          @click="handleDelete($event, session.session_id, session.title)"
        >
          ✕
        </button>
      </li>
    </ul>
  </aside>
</template>

<style scoped>
.session-list {
    width: 220px;
    flex-shrink: 0;
    border-right: 1px solid #e5e7eb;
    padding: 12px;
    overflow-y: auto;
    box-sizing: border-box;
}

.session-list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.session-list-title {
    font-size: 13px;
    font-weight: 600;
    color: #374151;
}

.create-btn {
    padding: 3px 10px;
    border: 1px solid #2563eb;
    border-radius: 4px;
    background: #fff;
    color: #2563eb;
    font-size: 12px;
    cursor: pointer;
}

.create-btn:hover:not(:disabled) {
    background: #eff6ff;
}

.create-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.session-tip {
    padding: 16px 0;
    text-align: center;
    color: #9ca3af;
    font-size: 13px;
}

.session-items {
    list-style: none;
    margin: 0;
    padding: 0;
}

.session-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 6px;
    padding: 8px 10px;
    border-radius: 6px;
    font-size: 13px;
    color: #374151;
    cursor: pointer;
}

.session-item:hover {
    background: #f3f4f6;
}

.session-item.active {
    background: #eff6ff;
    color: #2563eb;
}

.session-item.disabled {
    cursor: not-allowed;
}

.session-name {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.delete-btn {
    flex-shrink: 0;
    border: none;
    background: transparent;
    color: #9ca3af;
    font-size: 12px;
    cursor: pointer;
    padding: 2px 5px;
    border-radius: 4px;
    visibility: hidden;
}

.session-item:hover .delete-btn {
    visibility: visible;
}

.delete-btn:hover {
    background: #fee2e2;
    color: #dc2626;
}
</style>