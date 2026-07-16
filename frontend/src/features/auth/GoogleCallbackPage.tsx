import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { getMe } from '@/features/auth/api'
import { useAuthStore } from '@/store'
import { ROUTES } from '@/routes/paths'

export default function GoogleCallbackPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const setUser = useAuthStore((s) => s.setUser)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const accessToken = searchParams.get('access_token')
    const refreshToken = searchParams.get('refresh_token')

    if (!accessToken || !refreshToken) {
      setError('Google authentication failed. Missing tokens.')
      return
    }

    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', refreshToken)

    getMe()
      .then((response) => {
        setUser(response.data)
        navigate(ROUTES.DASHBOARD, { replace: true })
      })
      .catch(() => {
        setError('Failed to load user profile after Google sign-in.')
      })
  }, [searchParams, navigate, setUser])

  if (error) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4">
        <p className="text-red-500">{error}</p>
        <a href={ROUTES.LOGIN} className="btn-primary">
          Back to login
        </a>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
    </div>
  )
}
