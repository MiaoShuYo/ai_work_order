import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', redirect: '/chat' },
        { path: '/chat', component: () => import('../views/ChatView.vue') },
        { path: '/documents', component: () => import('../views/DocumentsView.vue') },
        { path: '/rag-debug', component: () => import('../views/RagDebugView.vue') },
        { path: '/tickets', component: () => import('../views/TicketListView.vue') },
        { path: '/tickets/:ticket_no', component: () => import('../views/TicketDetailView.vue') },
    ],
})

export default router