import { useState, type FormEvent } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Button, Input } from '@/components/ui'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { ROUTES } from '@/routes/paths'

export default function ResetPasswordPage() {
  const { resetPassword, isLoading, error, clearError } = useAuth()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') || ''
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    clearError()
    if (!token) return
    await resetPassword({
      token,
      password,
      confirm_password: confirmPassword,
    })
  }

  if (!token) {
    return (
      <div className="text-center">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Invalid reset link</h1>
        <p className="mt-2 text-sm text-slate-500">This password reset link is invalid or expired.</p>
        <Link to={ROUTES.FORGOT_PASSWORD} className="btn-primary mt-6 inline-block">
          Request new link
        </Link>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Reset your password</h1>
      <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Enter your new password below.</p>

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600 dark:border-red-800 dark:bg-red-950 dark:text-red-400">
          {error}
        </div>
      )}

      <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
        <Input
          label="New Password"
          type="password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <Input
          label="Confirm Password"
          type="password"
          placeholder="••••••••"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />
        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? 'Resetting...' : 'Reset Password'}
        </Button>
      </form>
    </div>
  )
}
