import { useEffect, useState } from 'react'
import { FileText, Send } from 'lucide-react'
import { api, type APIResponse } from '@/lib/api'
import { Card, Button, Input } from '@/components/ui'
import { PageHeader } from '@/components/layout/PageHeader'
import { toast } from '@/store/toast'
type UploadedFile = { id: number; filename: string; status: string; file_size?: number; download_url: string }
export default function PdfChatPage() {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [fileId, setFileId] = useState('')
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [uploading, setUploading] = useState(false)
  const [asking, setAsking] = useState(false)
  useEffect(() => {
    api.get<APIResponse<{ items: UploadedFile[] }>>('/files/').then((response) => setFiles(response.data.data.items)).catch(() => toast.error('Unable to load your PDF library'))
  }, [])
  async function upload(file?: File) { if (!file) return; setUploading(true); const form = new FormData(); form.append('file', file); try { await api.post('/files/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } }); toast.success('PDF uploaded and processing started') } catch { toast.error('PDF upload failed') } finally { setUploading(false) } }
  async function ask() { if (!fileId || !question.trim()) return; setAsking(true); try { const response = await api.post<APIResponse<{ answer: string }>>(`/knowledge/files/${fileId}/chat`, { question }); setAnswer(response.data.data.answer) } catch { toast.error('Unable to query this PDF') } finally { setAsking(false) } }
  return <div className="space-y-6"><PageHeader title="PDF Library & AI Chat" description="Upload study PDFs and ask questions about their content." /><Card><div className="flex items-center gap-3"><FileText className="h-6 w-6 text-primary" /><input type="file" accept="application/pdf" onChange={(event) => void upload(event.target.files?.[0])} disabled={uploading} />{uploading && <span className="text-sm text-slate-500">Uploading...</span>}</div></Card><Card title="Your PDFs"><div className="space-y-2">{files.length === 0 ? <p className="text-sm text-slate-500">No PDFs uploaded yet.</p> : files.map((file) => <button type="button" key={file.id} onClick={() => setFileId(String(file.id))} className={`flex w-full items-center justify-between rounded-lg border p-3 text-left ${fileId === String(file.id) ? 'border-primary bg-primary/5' : 'border-slate-200 dark:border-slate-700'}`}><span><span className="block font-medium">{file.filename}</span><span className="text-xs text-slate-500">ID {file.id} · {file.status}</span></span><a href={file.download_url} onClick={(event) => event.stopPropagation()} className="text-sm text-primary hover:underline">Download</a></button>)}</div></Card><Card title="Ask about a processed PDF"><div className="grid gap-3 sm:grid-cols-[10rem_1fr_auto]"><Input value={fileId} onChange={(event) => setFileId(event.target.value)} placeholder="File ID" /><Input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="What would you like to know?" /><Button onClick={() => void ask()} disabled={asking}><Send className="mr-2 h-4 w-4" />{asking ? 'Searching...' : 'Ask'}</Button></div>{answer && <div className="mt-5 rounded-lg bg-slate-50 p-4 text-sm leading-6 dark:bg-slate-800">{answer}</div>}</Card></div>
}
