import http from './http'

export interface SessionInfo {
  session_id: string
  thread_id: string
  title: string
  ticket_no: string | null
  created_at: string
  updated_at: string
}

export interface SessionToolCall {
  name: string
  args: Record<string, unknown>
  result: Record<string, unknown>
}

export interface SessionMessageItem {
  role: 'user' | 'assistant'
  content: string
  intent?: string | null
  confidence?: number | null
  need_human?: boolean | null
  suggested_actions?: string[]
  tool_calls?: SessionToolCall[]
  sources?: Array<Record<string, unknown>>
  task_intent?: Record<string, unknown> | null
  created_at: string
}

export async function listSessions(): Promise<SessionInfo[]> {
  const { data } = await http.get<SessionInfo[]>('/sessions')
  return data
}

export async function createSession(): Promise<SessionInfo> {
  const { data } = await http.post<SessionInfo>('/sessions')
  return data
}

export async function deleteSession(sessionId: string): Promise<void> {
  await http.delete(`/sessions/${encodeURIComponent(sessionId)}`)
}

export async function fetchMessages(sessionId: string): Promise<SessionMessageItem[]> {
  const { data } = await http.get<SessionMessageItem[]>(
    `/sessions/${encodeURIComponent(sessionId)}/messages`,
  )
  return data
}