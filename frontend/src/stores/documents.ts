import { defineStore } from 'pinia'
import axios from 'axios'

export interface DocumentInfo {
    id: string,
    filename: string,
    file_type: string,
    status: '处理中' | '已完成' | '失败'
    size: number
    uploaded_at: string
    summary: string | null
    error: string | null
}

export const useDocumentsStore = defineStore
    ('documents', {
        state: () => ({
            documents: [] as DocumentInfo[],
            loading: false,
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
                // 上传接口本身已经返回了这份文档的最终状态，直接刷新一次列表，保证和后端解析完成后的数据保持一致，不需要自己拼接返回值插入本地数组。
                await this.fetchDocuments()
                return data
            }
        }
    })