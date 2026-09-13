import http from './http'

export interface TicketListItem {
    ticket_no: string
    title: string
    status: string
    priority: string
    assignee: string
    user_id: string | null
    user_name: string | null
    order_no: string | null
}

export interface TicketInfo {
    ticket_no: string
    title: string
    status: string
    priority: string
    assignee: string
    user_id: string | null
    order_no: string | null
}

export interface UserInfo {
    user_id: string
    name: string
    level: string
    phone: string
}

export interface OrderInfo {
    order_no: string
    status: string
    pay_status: string
    logistics_status: string
}

export interface PaymentInfo {
    order_no: string
    pay_no: string
    pay_type: string
    amount: string
    pay_time: string
}

export interface LogisticsStep {
    time: string
    location: string
    description: string
}

export interface LogisticsInfo {
    order_no: string
    steps: LogisticsStep[]
}

export interface TicketDetail {
    ticket: TicketInfo
    user: UserInfo | null
    order: OrderInfo | null
    payments: PaymentInfo[]
    logistics: LogisticsInfo | null
    history: TicketInfo[]
}

export async function listTickets(): Promise<TicketListItem[]> {
    const { data } = await http.get<TicketListItem[]>('/tickets')
    return data
}

export async function fetchTicketDetail(ticketNo: string): Promise<TicketDetail> {
    // 工单号是路径参数，编码一下避免特殊字符破坏路由
    const { data } = await http.get<TicketDetail>(`/tickets/${encodeURIComponent(ticketNo)}`)
    return data
}