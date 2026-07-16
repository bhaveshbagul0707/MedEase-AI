import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button, Input } from '@/components/ui'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { ROUTES } from '@/routes/paths'

export default function ForgotPasswordPage() {
  const { forgotPassword, isLoading, error, clearError } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    clearError()
    const result = await forgotPassword(email)
    if (result) {
      setSuccess(true)
      if (result.reset_token) {
        navigate(`${ROUTES.RESET_PASSWORD}?token=${result.reset_token}`)
      }
    }
  }

  return (
    <div>
      <Link
        to={ROUTES.LOGIN}
        className="mb-6 inline-flex items-center gap-1 text-sm text-slate-500 hover:text-primary"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to sign in
      </Link>

      <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Forgot password?</h1>
      <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
        Enter your email and we&apos;ll send you a link to reset your password.
      </p>

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600 dark:border-red-800 dark:bg-red-950 dark:text-red-400">
          {error}
        </div>
      )}

      {success ? (
        <div className="mt-8 rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700 dark:border-green-800 dark:bg-green-950 dark:text-green-400">
          If the email exists, a password reset link has been sent. Check your inbox.
        </div>
      ) : (
        <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
          <Input
            label="Email"
            type="email"
            placeholder="you@university.edu"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? 'Sending...' : 'Send Reset Link'}
          </Button>
        </form>
      )}
    </div>
  )
}
