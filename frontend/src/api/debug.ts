import http from './http'

export interface DebugRetrievalRequest {
    query: string
    top_k: number
    strategies: string[]
    enable_rerank: boolean
}

export interface DebugSnippet {
    content: string
    score: number
    filename: string
    chunk_index: number
    strategy: string
}

export interface StrategyResult {
    strategy: string
    snippets: DebugSnippet[]
    context_preview: string
    elapsed_ms: number
}

export interface DebugRetrievalResponse {
    query: string
    results: StrategyResult[]
}

export async function debugRetrieval(params: DebugRetrievalRequest): Promise<DebugRetrievalResponse> {
    const { data } = await http.post<DebugRetrievalResponse>('/rag/debug', params)
    return data
}