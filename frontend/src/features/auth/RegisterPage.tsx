import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Button, Input } from '@/components/ui'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { ROUTES } from '@/routes/paths'
import type { StudentProgram } from '@/types'

const programs: StudentProgram[] = [
  'MBBS',
  'BDS',
  'Nursing',
  'Pharmacy',
  'Physiotherapy',
  'BAMS',
  'BHMS',
]

export default function RegisterPage() {
  const { register, isLoading, error, clearError } = useAuth()
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    program: '' as StudentProgram | '',
    year_of_study: 1,
    password: '',
    confirm_password: '',
  })

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    clearError()
    if (!form.program) return
    await register({
      ...form,
      program: form.program,
    })
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Create your account</h1>
      <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
        Join MedEase AI and start your personalized learning journey.
      </p>

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600 dark:border-red-800 dark:bg-red-950 dark:text-red-400">
          {error}
        </div>
      )}

      <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
        <Input
          label="Full Name"
          type="text"
          placeholder="Dr. Jane Smith"
          value={form.full_name}
          onChange={(e) => setForm({ ...form, full_name: e.target.value })}
          required
        />
        <Input
          label="Email"
          type="email"
          placeholder="you@university.edu"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
          required
        />

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Program</label>
            <select
              className="input"
              required
              value={form.program}
              onChange={(e) => setForm({ ...form, program: e.target.value as StudentProgram })}
            >
              <option value="" disabled>
                Select program
              </option>
              {programs.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>
          <Input
            label="Year of Study"
            type="number"
            min={1}
            max={6}
            value={form.year_of_study}
            onChange={(e) => setForm({ ...form, year_of_study: Number(e.target.value) })}
            required
          />
        </div>

        <Input
          label="Password"
          type="password"
          placeholder="••••••••"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
          required
        />
        <Input
          label="Confirm Password"
          type="password"
          placeholder="••••••••"
          value={form.confirm_password}
          onChange={(e) => setForm({ ...form, confirm_password: e.target.value })}
          required
        />

        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? 'Creating account...' : 'Create Account'}
        </Button>
      </form>

      <p className="mt-8 text-center text-sm text-slate-500">
        Already have an account?{' '}
        <Link to={ROUTES.LOGIN} className="font-medium text-primary hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  )
}
