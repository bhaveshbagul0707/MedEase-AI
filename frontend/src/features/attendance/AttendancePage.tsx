import { useEffect, useState } from 'react'
import { api, type APIResponse } from '@/lib/api'
import { Card, Button, Input } from '@/components/ui'
import { PageHeader } from '@/components/layout/PageHeader'
import { toast } from '@/store/toast'

type RecordItem = { id: number; subject_id: number; date: string; status: string; notes?: string }
export default function AttendancePage() {
  const [items, setItems] = useState<RecordItem[]>([])
  const [subjectId, setSubjectId] = useState('')
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10))
  const [status, setStatus] = useState('Present')
  const load = () => api.get<APIResponse<RecordItem[]>>('/attendance/').then((r) => setItems(r.data.data)).catch(() => toast.error('Unable to load attendance'))
  useEffect(() => { void load() }, [])
  async function save() {
    try { await api.post('/attendance/', { subject_id: Number(subjectId), date, status }); toast.success('Attendance recorded'); setSubjectId(''); load() } catch { toast.error('Could not record attendance') }
  }
  return <div className="space-y-6"><PageHeader title="Attendance" description="Track attendance by subject." /><Card title="Record attendance"><div className="grid gap-3 sm:grid-cols-4"><Input value={subjectId} onChange={(e) => setSubjectId(e.target.value)} placeholder="Subject ID" type="number" /><Input value={date} onChange={(e) => setDate(e.target.value)} type="date" /><select className="input" value={status} onChange={(e) => setStatus(e.target.value)}><option>Present</option><option>Absent</option><option>Excused</option></select><Button onClick={() => void save()}>Save</Button></div></Card><Card title="Attendance history">{items.length === 0 ? <p className="text-sm text-slate-500">No attendance records yet.</p> : <div className="space-y-2">{items.map((item) => <div className="flex justify-between border-b py-2 text-sm dark:border-slate-700" key={item.id}><span>{item.date} · Subject {item.subject_id}</span><span>{item.status}</span></div>)}</div>}</Card></div>
}
