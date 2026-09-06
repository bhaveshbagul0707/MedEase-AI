import { useEffect, useState } from 'react'
import { api, type APIResponse } from '@/lib/api'
import { Card, Button, Input } from '@/components/ui'
import { PageHeader } from '@/components/layout/PageHeader'
import { toast } from '@/store/toast'
type Post = { id: number; title: string; content: string; upvote_count: number }
export default function CommunityPage() {
  const [posts, setPosts] = useState<Post[]>([])
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const load = () => api.get<APIResponse<Post[]>>('/community/posts').then((r) => setPosts(r.data.data)).catch(() => toast.error('Unable to load community posts'))
  useEffect(() => { void load() }, [])
  async function create() { try { await api.post('/community/posts', { title, content }); toast.success('Post published'); setTitle(''); setContent(''); load() } catch { toast.error('Could not publish post') } }
  return <div className="space-y-6"><PageHeader title="Community" description="Share learning insights with fellow students." /><Card title="Create a post"><div className="space-y-3"><Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" /><textarea className="input min-h-24 w-full" value={content} onChange={(e) => setContent(e.target.value)} placeholder="Share something useful..." /><Button onClick={() => void create()}>Publish</Button></div></Card><div className="space-y-4">{posts.length === 0 ? <Card><p className="text-sm text-slate-500">No posts yet.</p></Card> : posts.map((post) => <Card key={post.id}><h2 className="font-semibold">{post.title}</h2><p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{post.content}</p></Card>)}</div></div>
}
