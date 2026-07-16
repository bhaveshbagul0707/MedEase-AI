import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store'
import { toast } from '@/store/toast'
import { ROUTES } from '@/routes/paths'
import * as authApi from '../api'

function persistAuth(data: authApi.TokenData) {
  localStorage.setItem('access_token', data.access_token)
  localStorage.setItem('refresh_token', data.refresh_token)
  useAuthStore.getState().setUser(data.user)
}

export function useAuth() {
  const navigate = useNavigate()
  const logoutStore = useAuthStore((s) => s.logout)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleError = (err: unknown) => {
    const message =
      (err as { response?: { data?: { message?: string } } })?.response?.data?.message ||
      'Something went wrong. Please try again.'
    setError(message)
    return message
  }

  const register = async (data: Parameters<typeof authApi.register>[0]) => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await authApi.register(data)
      persistAuth(result.data)
      toast.success('Account created successfully')
      navigate(ROUTES.DASHBOARD)
    } catch (err) {
      handleError(err)
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (data: Parameters<typeof authApi.login>[0]) => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await authApi.login(data)
      persistAuth(result.data)
      toast.success('Welcome back!')
      navigate(ROUTES.DASHBOARD)
    } catch (err) {
      handleError(err)
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } catch {
      // Client-side logout even if API fails
    } finally {
      logoutStore()
      navigate(ROUTES.LOGIN)
    }
  }

  const forgotPassword = async (email: string) => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await authApi.forgotPassword(email)
      return result.data
    } catch (err) {
      handleError(err)
      return null
    } finally {
      setIsLoading(false)
    }
  }

  const resetPassword = async (data: Parameters<typeof authApi.resetPassword>[0]) => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await authApi.resetPassword(data)
      persistAuth(result.data)
      toast.success('Password reset successfully')
      navigate(ROUTES.DASHBOARD)
    } catch (err) {
      handleError(err)
    } finally {
      setIsLoading(false)
    }
  }

  const loginWithGoogle = () => {
    window.location.href = authApi.getGoogleAuthUrl()
  }

  const completeGoogleAuth = (accessToken: string, refreshToken: string) => {
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', refreshToken)
  }

  return {
    isLoading,
    error,
    register,
    login,
    logout,
    forgotPassword,
    resetPassword,
    loginWithGoogle,
    completeGoogleAuth,
    clearError: () => setError(null),
  }
}
