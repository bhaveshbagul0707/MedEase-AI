import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '@/store'

function hasStoredToken() {
  return !!localStorage.getItem('access_token')
}

export function ProtectedRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)

  if (!isAuthenticated && !hasStoredToken()) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}

export function PublicRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)

  if (isAuthenticated || hasStoredToken()) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}
