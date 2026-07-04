import axios from 'axios'

const http = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api/v1',
    timeout: 30_000,// 大模型响应偶尔会慢，超时时间给宽松一点，避免正常请求被误判成失败
})

http.interceptors.response.use(
    (response) => response,
    (error) => {
        // 统一在这里把 axios 的错误对象转换成组件更容易处理的纯文本信息，
        // 前端不需要知道错误到底是网络问题还是后端返回的业务错误。
        const message = error.response?.data?.detail ?? '网络异常，请稍后重试'
        return Promise.reject(new Error(message))
    },
)

export default http