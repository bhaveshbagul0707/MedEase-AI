import { useEffect, useState } from 'react'
import { api, type APIResponse } from '@/lib/api'
import { Card, Button, Input } from '@/components/ui'
import { PageHeader } from '@/components/layout/PageHeader'
import { toast } from '@/store/toast'
type Plan = { id: number; title: string; start_date: string; end_date: string; daily_study_hours: number }
export default function StudyPlannerPage() {
  const [plans, setPlans] = useState<Plan[]>([])
  const [title, setTitle] = useState('')
  const [start, setStart] = useState('')
  const [end, setEnd] = useState('')
  const load = () => api.get<APIResponse<Plan[]>>('/study-plans/').then((r) => setPlans(r.data.data)).catch(() => toast.error('Unable to load study plans'))
  useEffect(() => { void load() }, [])
  async function create() { try { await api.post('/study-plans/', { title, start_date: start, end_date: end }); toast.success('Study plan created'); setTitle(''); load() } catch { toast.error('Could not create study plan') } }
  return <div className="space-y-6"><PageHeader title="Study Planner" description="Plan focused study periods." /><Card title="Create a plan"><div className="grid gap-3 sm:grid-cols-4"><Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Plan title" /><Input value={start} onChange={(e) => setStart(e.target.value)} type="date" /><Input value={end} onChange={(e) => setEnd(e.target.value)} type="date" /><Button onClick={() => void create()}>Create</Button></div></Card><Card title="Your plans">{plans.length === 0 ? <p className="text-sm text-slate-500">No study plans yet.</p> : <div className="space-y-3">{plans.map((plan) => <div key={plan.id} className="rounded-lg border p-3 dark:border-slate-700"><p className="font-medium">{plan.title}</p><p className="text-sm text-slate-500">{plan.start_date} to {plan.end_date}</p></div>)}</div>}</Card></div>
}
