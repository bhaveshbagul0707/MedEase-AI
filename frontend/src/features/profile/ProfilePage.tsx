import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Calendar, GraduationCap, Mail, Settings, Shield } from 'lucide-react'
import { Avatar, Badge, Card, ErrorState, PageLoader } from '@/components/ui'
import { PageHeader } from '@/components/layout/PageHeader'
import { getMe } from '@/features/auth/api'
import { useAuthStore } from '@/store'
import { formatDate } from '@/lib/formatters'
import { ROUTES } from '@/routes/paths'

export default function ProfilePage() {
  const cachedUser = useAuthStore((s) => s.user)
  const setUser = useAuthStore((s) => s.setUser)

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      const response = await getMe()
      setUser(response.data)
      return response.data
    },
    initialData: cachedUser ?? undefined,
  })

  if (isLoading && !data) return <PageLoader />
  if (isError || !data) {
    return <ErrorState onRetry={() => refetch()} />
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <PageHeader
        title="Profile"
        description="Your account information and academic details"
        actions={
          <Link to={ROUTES.SETTINGS} className="btn-secondary text-sm">
            <Settings className="mr-2 h-4 w-4" />
            Edit Settings
          </Link>
        }
      />

      <Card>
        <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start">
          <Avatar name={data.full_name} src={data.avatar_url} size="lg" />
          <div className="flex-1 text-center sm:text-left">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">{data.full_name}</h2>
            <p className="mt-1 text-slate-500">{data.email}</p>
            <div className="mt-3 flex flex-wrap justify-center gap-2 sm:justify-start">
              <Badge variant="primary">{data.program}</Badge>
              <Badge variant="secondary">Year {data.year_of_study}</Badge>
              {data.is_verified && <Badge variant="success">Verified</Badge>}
            </div>
          </div>
        </div>
      </Card>

      <div className="grid gap-4 sm:grid-cols-2">
        <Card title="Account Details">
          <dl className="space-y-4">
            <div className="flex items-center gap-3">
              <Mail className="h-5 w-5 text-slate-400" />
              <div>
                <dt className="text-xs text-slate-500">Email</dt>
                <dd className="text-sm font-medium text-slate-900 dark:text-white">{data.email}</dd>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Calendar className="h-5 w-5 text-slate-400" />
              <div>
                <dt className="text-xs text-slate-500">Member since</dt>
                <dd className="text-sm font-medium text-slate-900 dark:text-white">
                  {formatDate(data.created_at)}
                </dd>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Shield className="h-5 w-5 text-slate-400" />
              <div>
                <dt className="text-xs text-slate-500">Account status</dt>
                <dd className="text-sm font-medium text-slate-900 dark:text-white">
                  {data.is_active ? 'Active' : 'Inactive'}
                </dd>
              </div>
            </div>
          </dl>
        </Card>

        <Card title="Academic Info">
          <dl className="space-y-4">
            <div className="flex items-center gap-3">
              <GraduationCap className="h-5 w-5 text-slate-400" />
              <div>
                <dt className="text-xs text-slate-500">Program</dt>
                <dd className="text-sm font-medium text-slate-900 dark:text-white">{data.program}</dd>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <GraduationCap className="h-5 w-5 text-slate-400" />
              <div>
                <dt className="text-xs text-slate-500">Year of Study</dt>
                <dd className="text-sm font-medium text-slate-900 dark:text-white">
                  Year {data.year_of_study}
                </dd>
              </div>
            </div>
          </dl>
        </Card>
      </div>
    </div>
  )
}
