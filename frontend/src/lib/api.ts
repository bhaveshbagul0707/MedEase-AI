import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token')

  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

let isRefreshing = false

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean
    }

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/auth/login') &&
      !originalRequest.url?.includes('/auth/register') &&
      !originalRequest.url?.includes('/auth/refresh')
    ) {
      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken) {
        if (isRefreshing) {
          return Promise.reject(error)
        }

        originalRequest._retry = true
        isRefreshing = true

        try {
          const response = await axios.post(
            `${API_BASE_URL}/auth/refresh`,
            {
              refresh_token: refreshToken,
            },
          )

          const newAccessToken = response.data.data.access_token
          const newRefreshToken = response.data.data.refresh_token

          localStorage.setItem('access_token', newAccessToken)
          localStorage.setItem('refresh_token', newRefreshToken)

          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
          }

          return api(originalRequest)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')

          if (!window.location.pathname.startsWith('/login')) {
            window.location.href = '/login'
          }
        } finally {
          isRefreshing = false
        }
      } else if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  },
)

export interface APIResponse<T> {
  success: boolean
  message: string
  data: T
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}