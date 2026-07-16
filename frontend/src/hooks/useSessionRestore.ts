import { useEffect } from 'react'
import { getMe } from '@/features/auth/api'
import { useAuthStore } from '@/store'

export function useSessionRestore() {
  const setUser = useAuthStore((s) => s.setUser)
  const logout = useAuthStore((s) => s.logout)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) return

    getMe()
      .then((response) => setUser(response.data))
      .catch(() => logout())
  }, [setUser, logout])
}
