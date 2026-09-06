import { useState } from 'react'
import { Bot, Send } from 'lucide-react'
import { api, type APIResponse } from '@/lib/api'
import { Card, Button, Input } from '@/components/ui'
import { PageHeader } from '@/components/layout/PageHeader'
import { toast } from '@/store/toast'

export default function AITutorPage() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)

  async function ask() {
    if (!question.trim()) return
    setLoading(true)
    try {
      const response = await api.post<APIResponse<{ answer: string; suggestions?: string[] }>>('/tutor/ask', {
        question,
      })
      setAnswer(response.data.data.answer)
    } catch {
      toast.error('Unable to reach the AI tutor')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader title="AI Tutor" description="Ask questions grounded in your learning materials." />
      <Card className="mx-auto max-w-3xl">
        <div className="mb-6 flex items-center gap-3">
          <Bot className="h-8 w-8 text-primary" />
          <p className="text-sm text-slate-500 dark:text-slate-400">Your tutor uses the knowledge pipeline when relevant.</p>
        </div>
        <div className="flex gap-2">
          <Input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask a medical question..." onKeyDown={(event) => event.key === 'Enter' && void ask()} />
          <Button onClick={() => void ask()} disabled={loading}><Send className="mr-2 h-4 w-4" />{loading ? 'Thinking...' : 'Ask'}</Button>
        </div>
        {answer && <div className="mt-6 rounded-lg bg-slate-50 p-4 text-sm leading-6 dark:bg-slate-800">{answer}</div>}
        {!answer && !loading && <p className="mt-6 text-center text-sm text-slate-400">Your answer will appear here.</p>}
      </Card>
    </div>
  )
}
