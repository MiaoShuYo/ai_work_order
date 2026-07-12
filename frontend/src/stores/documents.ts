import { defineStore } from 'pinia'
import axios from 'axios'

export interface DocumentInfo {
    id: string
    filename: string
    file_type: string
    status: '解析中' | '切片完成' | '向量化中' | '可检索' | '失败' | '已完成'
    size: number
    chunk_count: number
    uploaded_at: string
    summary: string | null
    error: string | null
}

export interface DocumentLogEntry {
    id: number
    step: string
    message: string
    created_at: string
}

// 只有落到这两种状态之一才算处理完毕，轮询要一直持续到列表里所有文档都落到终态。
const TERMINAL_STATUSES = ['可检索', '失败']

export const useDocumentsStore = defineStore
    ('documents', {
        state: () => ({
            documents: [] as DocumentInfo[],
            loading: false,
            pollTimer: null as ReturnType<typeof setInterval> | null,
        }),
        actions: {
            async fetchDocuments() {
                this.loading = true
                try {
                    const { data } = await axios.get<DocumentInfo[]>('/api/v1/documents')
                    this.documents = data
                }
                finally {
                    this.loading = false
                }
            },
            async fetchDocumentLogs(documentId: string) {
                const { data } = await axios.get<DocumentLogEntry[]>(`/api/v1/documents/${documentId}/logs`)
                return data
            },
            async uploadDocument(file: File, onProgress: (percent: number) => void) {
                const formData = new FormData()
                formData.append('file', file)
                const { data } = await axios.post<DocumentInfo>('/api/v1/documents', formData, {
                    onUploadProgress: (event) => {
                        if (event.total) {
                            onProgress(Math.round((event.loaded / event.total) * 100))
                        }
                    },
                })
                // 上传接口现在只返回解析中这个初始状态，真正的处理进度要靠轮询去追，这里先刷新一次列表让新记录露出来，再开始轮询。
                await this.fetchDocuments()
                this.startPolling()
                return data
            },
            startPolling() {
                if (this.pollTimer) return
                this.pollTimer = setInterval(async () => {
                    await this.fetchDocuments()
                    const allDone = this.documents.every((doc) => TERMINAL_STATUSES.includes(doc.status))
                    if (allDone) this.stopPolling()
                }, 2000)
            },
            stopPolling() {
                if (this.pollTimer) {
                    clearInterval(this.pollTimer)
                    this.pollTimer = null
                }
            },
        },
    })