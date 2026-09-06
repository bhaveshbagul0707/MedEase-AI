import { useEffect, useState } from 'react'
import { api, type APIResponse } from '@/lib/api'
import { Card, Button, Input } from '@/components/ui'
import { PageHeader } from '@/components/layout/PageHeader'
import { toast } from '@/store/toast'
type Case = { id: number; title: string; description: string; specialty?: string; difficulty: string }
export default function ClinicalCasesPage() {
  const [cases, setCases] = useState<Case[]>([])
  const [selected, setSelected] = useState<Case | null>(null)
  const [diagnosis, setDiagnosis] = useState('')
  const [feedback, setFeedback] = useState('')
  useEffect(() => { api.get<APIResponse<Case[]>>('/clinical-cases/').then((r) => setCases(r.data.data)).catch(() => toast.error('Unable to load clinical cases')) }, [])
  async function submit() { if (!selected) return; try { const r = await api.post<APIResponse<{ feedback: string; score: number }>>(`/clinical-cases/${selected.id}/attempt`, { diagnosis }); setFeedback(`${r.data.data.feedback} (Score: ${r.data.data.score})`) } catch { toast.error('Could not submit attempt') } }
  return <div className="space-y-6"><PageHeader title="Clinical Cases" description="Practice clinical reasoning with case-based learning." />{selected ? <Card title={selected.title}><p className="text-sm leading-6">{selected.description}</p><div className="mt-4 flex gap-2"><Input value={diagnosis} onChange={(e) => setDiagnosis(e.target.value)} placeholder="Your diagnosis" /><Button onClick={() => void submit()}>Submit</Button></div>{feedback && <p className="mt-4 rounded-lg bg-slate-50 p-3 text-sm dark:bg-slate-800">{feedback}</p>}<Button className="mt-4" variant="ghost" onClick={() => setSelected(null)}>Back to cases</Button></Card> : <div className="grid gap-4 md:grid-cols-2">{cases.length === 0 ? <Card><p className="text-sm text-slate-500">No clinical cases available.</p></Card> : cases.map((item) => <Card key={item.id}><h2 className="font-semibold">{item.title}</h2><p className="mt-2 text-sm text-slate-500">{item.specialty || 'General'} · {item.difficulty}</p><Button className="mt-4" onClick={() => setSelected(item)}>Open case</Button></Card>)}</div>}</div>
}
