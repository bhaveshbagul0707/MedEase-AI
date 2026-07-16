import { api, type APIResponse } from '@/lib/api'
import type { AuthTokens, User } from '@/types'

export interface TokenData extends AuthTokens {
  user: User
}

export async function register(data: {
  email: string
  password: string
  confirm_password: string
  full_name: string
  program: string
  year_of_study: number
}) {
  const response = await api.post<APIResponse<TokenData>>('/auth/register', data)
  return response.data
}

export async function login(data: { email: string; password: string }) {
  const response = await api.post<APIResponse<TokenData>>('/auth/login', data)
  return response.data
}

export async function logout() {
  const response = await api.post<APIResponse<{ message: string }>>('/auth/logout')
  return response.data
}

export async function refreshToken(refresh_token: string) {
  const response = await api.post<APIResponse<TokenData>>('/auth/refresh', { refresh_token })
  return response.data
}

export async function getMe() {
  const response = await api.get<APIResponse<User>>('/auth/me')
  return response.data
}

export async function updateProfile(data: Partial<{
  full_name: string
  program: string
  year_of_study: number
  avatar_url: string
}>) {
  const response = await api.patch<APIResponse<User>>('/auth/me', data)
  return response.data
}

export async function changePassword(data: {
  current_password: string
  new_password: string
  confirm_password: string
}) {
  const response = await api.post<APIResponse<{ message: string }>>('/auth/change-password', data)
  return response.data
}

export async function forgotPassword(email: string) {
  const response = await api.post<APIResponse<{ message: string; reset_token?: string }>>(
    '/auth/forgot-password',
    { email },
  )
  return response.data
}

export async function resetPassword(data: {
  token: string
  password: string
  confirm_password: string
}) {
  const response = await api.post<APIResponse<TokenData>>('/auth/reset-password', data)
  return response.data
}

export function getGoogleAuthUrl() {
  const base = import.meta.env.VITE_API_BASE_URL || '/api/v1'
  return `${base}/auth/google`
}
