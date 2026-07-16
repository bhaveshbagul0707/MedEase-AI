import { useState, type FormEvent } from 'react'
import { Moon, Sun } from 'lucide-react'
import { Button, Card, Input } from '@/components/ui'
import { PageHeader } from '@/components/layout/PageHeader'
import { changePassword, updateProfile } from '@/features/auth/api'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useTheme } from '@/hooks/useTheme'
import { useAuthStore } from '@/store'
import { toast } from '@/store/toast'
import type { StudentProgram } from '@/types'

const programs: StudentProgram[] = [
  'MBBS', 'BDS', 'Nursing', 'Pharmacy', 'Physiotherapy', 'BAMS', 'BHMS',
]

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user)
  const setUser = useAuthStore((s) => s.setUser)
  const { logout } = useAuth()
  const { isDark, toggleTheme } = useTheme()

  const [profile, setProfile] = useState({
    full_name: user?.full_name || '',
    program: (user?.program || 'MBBS') as StudentProgram,
    year_of_study: user?.year_of_study || 1,
  })
  const [passwords, setPasswords] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })
  const [savingProfile, setSavingProfile] = useState(false)
  const [savingPassword, setSavingPassword] = useState(false)

  const handleProfileSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setSavingProfile(true)
    try {
      const result = await updateProfile(profile)
      setUser(result.data)
      toast.success('Profile updated successfully')
    } catch {
      toast.error('Failed to update profile')
    } finally {
      setSavingProfile(false)
    }
  }

  const handlePasswordSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setSavingPassword(true)
    try {
      await changePassword(passwords)
      toast.success('Password changed successfully')
      setPasswords({ current_password: '', new_password: '', confirm_password: '' })
    } catch {
      toast.error('Failed to change password. Check your current password.')
    } finally {
      setSavingPassword(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <PageHeader
        title="Settings"
        description="Manage your account, appearance, and security"
      />

      <Card title="Profile" description="Update your personal and academic information">
        <form onSubmit={handleProfileSubmit} className="space-y-4">
          <Input
            label="Full Name"
            value={profile.full_name}
            onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
            required
          />
          <Input label="Email" value={user?.email || ''} disabled />
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Program</label>
              <select
                className="input"
                value={profile.program}
                onChange={(e) => setProfile({ ...profile, program: e.target.value as StudentProgram })}
              >
                {programs.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
            <Input
              label="Year of Study"
              type="number"
              min={1}
              max={6}
              value={profile.year_of_study}
              onChange={(e) => setProfile({ ...profile, year_of_study: Number(e.target.value) })}
              required
            />
          </div>
          <Button type="submit" disabled={savingProfile}>
            {savingProfile ? 'Saving...' : 'Save Changes'}
          </Button>
        </form>
      </Card>

      <Card title="Appearance" description="Customize how MedEase AI looks">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {isDark ? <Moon className="h-5 w-5 text-slate-400" /> : <Sun className="h-5 w-5 text-slate-400" />}
            <div>
              <p className="text-sm font-medium text-slate-900 dark:text-white">Dark Mode</p>
              <p className="text-xs text-slate-500">Toggle between light and dark themes</p>
            </div>
          </div>
          <button
            onClick={toggleTheme}
            className={`relative h-6 w-11 rounded-full transition-colors ${isDark ? 'bg-primary' : 'bg-slate-300'}`}
            role="switch"
            aria-checked={isDark}
          >
            <span
              className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${isDark ? 'translate-x-5' : 'translate-x-0.5'}`}
            />
          </button>
        </div>
      </Card>

      <Card title="Security" description="Change your password">
        <form onSubmit={handlePasswordSubmit} className="space-y-4">
          <Input
            label="Current Password"
            type="password"
            value={passwords.current_password}
            onChange={(e) => setPasswords({ ...passwords, current_password: e.target.value })}
            required
          />
          <Input
            label="New Password"
            type="password"
            value={passwords.new_password}
            onChange={(e) => setPasswords({ ...passwords, new_password: e.target.value })}
            required
          />
          <Input
            label="Confirm New Password"
            type="password"
            value={passwords.confirm_password}
            onChange={(e) => setPasswords({ ...passwords, confirm_password: e.target.value })}
            required
          />
          <Button type="submit" disabled={savingPassword}>
            {savingPassword ? 'Updating...' : 'Change Password'}
          </Button>
        </form>
      </Card>

      <Card title="Danger Zone" description="Irreversible account actions">
        <Button variant="danger" onClick={() => logout()}>
          Log out of all devices
        </Button>
      </Card>
    </div>
  )
}
