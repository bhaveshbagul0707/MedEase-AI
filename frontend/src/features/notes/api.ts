import { api, type APIResponse, type PaginatedResponse } from '@/lib/api'

export interface Note {
  id: number
  title: string
  content: string
  created_at?: string
  updated_at?: string
}

export async function listNotes() {
  const res = await api.get<APIResponse<PaginatedResponse<Note>>>('/notes/')
  return res.data.data
}

export async function createNote(payload: { title: string; content: string }) {
  const res = await api.post<APIResponse<Note>>('/notes/', payload)
  return res.data.data
}

export async function updateNote(id: number, payload: { title: string; content: string }) {
  const res = await api.put<APIResponse<Note>>(`/notes/${id}`, payload)
  return res.data.data
}

export async function deleteNote(id: number) {
  await api.delete(`/notes/${id}`)
}
