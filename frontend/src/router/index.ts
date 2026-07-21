import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', redirect: '/chat' },
        { path: '/chat', component: () => import('../views/ChatView.vue') },
        { path: '/documents', component: () => import('../views/DocumentsView.vue') },
        {path:'/rag-debug',component:()=> import ('../views/RagDebugView.vue')}
    ],
})

export default router