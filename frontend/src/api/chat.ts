import http from './http'

export interface ChatMessage {
    role: 'user' | 'assistant'
    content: string
}

export interface ChatRequest {
    reply: string
}

export async function sendChatMessage(messages: ChatMessage[]): Promise<string> {
    const { data } = await http.post<ChatRequest>('/chat', { messages })
    return data.reply
}