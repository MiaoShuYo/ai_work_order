import { computed, reactive } from 'vue'
import {
    createSession as apiCreateSession,
    deleteSession as apiDeleteSession,
    listSessions,
    type SessionInfo,
} from '../api/sessions'

const STORAGE_KEY = 'chat.current_session_id'

interface SessionStoreState {
    sessions: SessionInfo[]
    currentSessionId: string
    loading: boolean
    initialized: boolean
}

// 模块级单例，所有组件 useSessionStore() 拿到的都是这同一份状态
const state = reactive<SessionStoreState>({
    sessions: [],
    currentSessionId: '',
    loading: false,
    initialized: false,
})

const currentSession = computed(
    () => state.sessions.find((item) => item.session_id === state.currentSessionId) ?? null,
)

function setCurrent(sessionId: string) {
    state.currentSessionId = sessionId
    localStorage.setItem(STORAGE_KEY, sessionId)
}

async function initSessions(): Promise<void> {
    // 初始化只执行一次，ChatView 重复挂载不会把列表重新拉一遍
    if (state.initialized || state.loading) return
    state.loading = true
    try {
        state.sessions = await listSessions()
        if (state.sessions.length === 0) {
            const created = await apiCreateSession()
            state.sessions = [created]
        }
        const savedId = localStorage.getItem(STORAGE_KEY)
        const target =
            state.sessions.find((item) => item.session_id === savedId) ?? state.sessions[0]
        setCurrent(target.session_id)
        state.initialized = true
    } finally {
        state.loading = false
    }
}

async function createNewSession(): Promise<SessionInfo> {
    const session = await apiCreateSession()
    state.sessions.unshift(session)
    setCurrent(session.session_id)
    return session
}

function selectSession(sessionId: string) {
    if (sessionId !== state.currentSessionId) {
        setCurrent(sessionId)
    }
}

async function removeSession(sessionId: string) {
    await apiDeleteSession(sessionId)
    state.sessions = state.sessions.filter((item) => item.session_id !== sessionId)
    if (state.currentSessionId !== sessionId) return
    // 删掉的是当前会话，优先切到剩下的第一条，一个都不剩就补建一个空会话
    if (state.sessions.length > 0) {
        setCurrent(state.sessions[0].session_id)
    } else {
        const created = await apiCreateSession()
        state.sessions = [created]
        setCurrent(created.session_id)
    }
}

function patchSessionMeta(
    sessionId: string,
    patch: Partial<Pick<SessionInfo, 'title' | 'ticket_no'>>,
) {
    const target = state.sessions.find((item) => item.session_id === sessionId)
    if (target) {
        Object.assign(target, patch)
        // 首轮对话后会话应浮到列表顶部，和后端 updated_at 倒序的口径保持一致
        state.sessions = [target, ...state.sessions.filter((item) => item !== target)]
    }
}

export function useSessionStore() {
    return {
        state,
        currentSession,
        initSessions,
        createNewSession,
        selectSession,
        removeSession,
        patchSessionMeta,
    }
}