import { useEffect, useState } from 'react'
import { BarChart3 } from 'lucide-react'
import { api, type APIResponse } from '@/lib/api'
import { Card } from '@/components/ui'
import { PageHeader } from '@/components/layout/PageHeader'

type Progress = { total_flashcards: number; learned_flashcards: number; due_reviews: number; quizzes_taken: number }

export default function AnalyticsPage() {
  const [data, setData] = useState<Progress | null>(null)
  const [error, setError] = useState('')
  useEffect(() => {
    api.get<APIResponse<Progress>>('/analytics/study-progress').then((response) => setData(response.data.data)).catch(() => setError('Analytics are unavailable right now.'))
  }, [])
  return (
    <div className="space-y-6">
      <PageHeader title="Study Progress" description="Track your learning activity and review workload." />
      {error && <Card><p className="text-sm text-red-600">{error}</p></Card>}
      {!data && !error && <Card><p className="text-sm text-slate-500">Loading analytics...</p></Card>}
      {data && <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Object.entries(data).map(([label, value]) => <Card key={label}><BarChart3 className="mb-3 h-6 w-6 text-primary" /><p className="text-sm capitalize text-slate-500">{label.replaceAll('_', ' ')}</p><p className="text-2xl font-bold">{value}</p></Card>)}
      </div>}
    </div>
  )
}
