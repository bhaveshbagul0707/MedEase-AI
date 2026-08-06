import { api } from '../../lib/api'

export type StudyMode =
    | 'Learn'
    | 'Exam'
    | 'Clinical'
    | 'Revision'
    | 'Viva'

export type MessageRole =
    | 'user'
    | 'assistant'
    | 'system'

export interface Chat {
    id: number
    title: string
    study_mode: StudyMode
    subject: string | null
    is_pinned: boolean
    is_archived: boolean
    created_at: string
    updated_at: string
}

export interface ChatMessage {
    id: number
    role: MessageRole
    content: string
    created_at: string
}

export interface ChatPagination {
    total: number
    limit: number
    offset: number
    has_more: boolean
}

export interface ChatHistory {
    session: Chat
    messages: ChatMessage[]
    pagination: ChatPagination
}

export interface CreateChatData {
    title?: string
    study_mode?: StudyMode
    subject?: string | null
}

export interface UpdateChatData {
    title?: string
    study_mode?: StudyMode
    subject?: string
    is_pinned?: boolean
    is_archived?: boolean
}

export async function getChats(): Promise<Chat[]> {
    const response = await api.get<Chat[]>('/chat')
    return response.data
}

export async function getChat(
    chatId: number,
    limit = 20,
    offset = 0,
): Promise<ChatHistory> {
    const response = await api.get<ChatHistory>(
        `/chat/${chatId}`,
        {
            params: {
                limit,
                offset,
            },
        },
    )

    return response.data
}

export async function createChat(
    data: CreateChatData = {},
): Promise<Chat> {
    const response = await api.post<Chat>('/chat', {
        title: data.title ?? 'New Chat',
        study_mode: data.study_mode ?? 'Learn',
        subject: data.subject ?? null,
    })

    return response.data
}

export async function sendMessage(
    chatId: number,
    content: string,
): Promise<ChatMessage> {
    const response = await api.post<ChatMessage>(
        `/chat/${chatId}/messages`,
        {
            content,
        },
    )

    return response.data
}

export async function updateChat(
    chatId: number,
    data: UpdateChatData,
): Promise<Chat> {
    const response = await api.patch<Chat>(
        `/chat/${chatId}`,
        data,
    )

    return response.data
}

export async function deleteChat(
    chatId: number,
): Promise<void> {
    await api.delete(`/chat/${chatId}`)
}