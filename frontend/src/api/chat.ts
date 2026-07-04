import http from './http'

export type Intent = 'order_issue' | 'account_issue' | 'refund_request' | 'general_inquiry' | 'other'

export interface UserMessage {
    role: 'user',
    content: string
}

export interface AssistantMessage {
    role: 'assistant',
    intent: Intent,
    answer: string,
    confidence: number
    needHuman: boolean
    suggestedActions: string[]
}

export type ChatMessage = UserMessage | AssistantMessage

export interface ChatResponseDto {
    intent: Intent,
    answer: string,
    confidence: number
    need_human: boolean
    suggested_actions: string[]
}

// 发给后端的历史消息里，AI 消息只需要还原成一段文本，后端目前只有 content 字段拼接对话上下文。不关心当时判断出的 intent 和置信度这些衍生字段
function toApiMessage(message: ChatMessage): {
    role: 'user' | 'assistant'; content: string
} {
    if (message.role === 'user') {
        return { role: 'user', content: message.content }
    } else {
        return { role: 'assistant', content: message.answer }
    }
}


export async function sendChatMessage(history: ChatMessage[]): Promise<AssistantMessage> {
    const paylaod ={
        messages: history.map(toApiMessage)
    }
    const {data} = await http.post<ChatResponseDto>('/chat', paylaod)
    return {
        role: 'assistant',
        intent: data.intent,
        answer: data.answer,
        confidence: data.confidence,
        needHuman: data.need_human,
        suggestedActions: data.suggested_actions
    }
}