import { Link } from 'react-router-dom'
import {
  BookOpen,
  Bot,
  Calendar,
  FileText,
  Flame,
  HelpCircle,
  NotebookPen,
  Target,
  TrendingUp,
} from 'lucide-react'
import { Badge, Card } from '@/components/ui'
import { PageHeader } from '@/components/layout/PageHeader'
import { useAuthStore } from '@/store'
import { useEffect, useState } from 'react'
import { api, type APIResponse } from '@/lib/api'
import { getGreeting } from '@/lib/formatters'
import { ROUTES } from '@/routes/paths'

const quickActions = [
  { label: 'AI Tutor', path: ROUTES.AI_TUTOR, icon: Bot },
  { label: 'New Note', path: ROUTES.NOTES, icon: NotebookPen },
  { label: 'Take Quiz', path: ROUTES.QUIZ, icon: HelpCircle },
  { label: 'Upload PDF', path: ROUTES.PDF_CHAT, icon: FileText },
]

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user)
  const firstName = user?.full_name?.split(' ')[0] || 'Student'
  const [progress, setProgress] = useState<{ total_flashcards: number; learned_flashcards: number; due_reviews: number; quizzes_taken: number } | null>(null)
  useEffect(() => {
    api.get<APIResponse<typeof progress>>('/analytics/study-progress').then((response) => setProgress(response.data.data)).catch(() => undefined)
  }, [])

  const stats = [
    { label: 'Flashcards', value: progress ? String(progress.total_flashcards) : '—', icon: Flame, color: 'text-orange-500' },
    { label: 'Learned', value: progress ? String(progress.learned_flashcards) : '—', icon: Calendar, color: 'text-green-500' },
    { label: 'Due Reviews', value: progress ? String(progress.due_reviews) : '—', icon: HelpCircle, color: 'text-blue-500' },
    { label: 'Quizzes Taken', value: progress ? String(progress.quizzes_taken) : '—', icon: Target, color: 'text-purple-500' },
  ]

  return (
    <div className="space-y-8">
      <PageHeader
        title={`${getGreeting()}, ${firstName}!`}
        description="Here's your study overview for today."
        actions={
          user && (
            <div className="flex gap-2">
              <Badge variant="primary">{user.program}</Badge>
              <Badge variant="secondary">Year {user.year_of_study}</Badge>
            </div>
          )
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label} className="flex items-center gap-4">
            <div className={`rounded-lg bg-slate-100 p-3 dark:bg-slate-800 ${stat.color}`}>
              <stat.icon className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm text-slate-500 dark:text-slate-400">{stat.label}</p>
              <p className="text-xl font-bold text-slate-900 dark:text-white">{stat.value}</p>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Upcoming Exams" description="Your next scheduled examinations">
          <div className="flex flex-col items-center justify-center py-8 text-slate-400">
            <Calendar className="h-10 w-10" />
            <p className="mt-2 text-sm">No upcoming exams yet.</p>
            <Link to={ROUTES.STUDY_PLANNER} className="mt-3 text-sm font-medium text-primary hover:underline">
              Add exams in Study Planner →
            </Link>
          </div>
        </Card>

        <Card title="Weak Subjects" description="Subjects that need more attention">
          <div className="flex flex-col items-center justify-center py-8 text-slate-400">
            <TrendingUp className="h-10 w-10" />
            <p className="mt-2 text-sm">Complete quizzes to identify weak areas.</p>
            <Link to={ROUTES.QUIZ} className="mt-3 text-sm font-medium text-primary hover:underline">
              Take a quiz →
            </Link>
          </div>
        </Card>

        <Card title="Recent Notes" description="Your latest study notes">
          <div className="flex flex-col items-center justify-center py-8 text-slate-400">
            <BookOpen className="h-10 w-10" />
            <p className="mt-2 text-sm">No notes yet.</p>
            <Link to={ROUTES.NOTES} className="mt-3 text-sm font-medium text-primary hover:underline">
              Create your first note →
            </Link>
          </div>
        </Card>

        <Card title="Quick Actions" description="Jump into your study tools">
          <div className="grid grid-cols-2 gap-3">
            {quickActions.map((action) => (
              <Link
                key={action.label}
                to={action.path}
                className="flex items-center gap-2 rounded-lg border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700 transition-colors hover:border-primary/30 hover:bg-primary/5 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
              >
                <action.icon className="h-4 w-4 text-primary" />
                {action.label}
              </Link>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
