import { reactive } from 'vue'

export interface ToolCallRecord {
    id: number
    name: string
    args: Record<string, unknown>
    result: Record<string, unknown>
    timestamp: number
}

interface TaskContextState {
    user: Record<string, unknown> | null
    order: Record<string, unknown> | null
    ticket: Record<string, unknown> | null
    history: ToolCallRecord[]
}

// 用一个模块级别的 reactive 对象充当轻量状态管理，聊天页面和右侧的上下文面板各自从这里读写，仅仅为了这一点跨组件共享的状态引入 Pinia 没有必要。
const state = reactive<TaskContextState>({
    user: null,
    order: null,
    ticket: null,
    history: [],
})

// 只有代表一段时间内持续有效的业务实体的工具才占用固定槽位，知识库检索是针对当次问题的即时结果，不适合固定展示，所以不出现在这张表里。
const CONTEXT_SLOT: Partial<Record<string, 'user' | 'order' | 'ticket'>> = {
    query_user: 'user',
    query_order: 'order',
    query_ticket: 'ticket',
}

let nextId = 0

export function useTaskContext() {
    function recordToolCall(name: string, args: Record<string, unknown>, result: Record<string, unknown>) {
        state.history.push({ id: nextId++, name, args, result, timestamp: Date.now() })

        const slot = CONTEXT_SLOT[name]
        // 结果里带 error 字段说明这次查询没查到东西，不能用一个空结果把之前已经展示的有效上下文覆盖掉。
        if (slot && !result.error) {
            state[slot] = result
        }
    }

    return { state, recordToolCall }
}