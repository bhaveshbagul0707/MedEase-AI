import { useEffect, useState } from 'react'
import { listNotes, createNote, updateNote, deleteNote, type Note } from './api'
import { PageHeader } from '@/components/layout/PageHeader'
import { Card, Button, Input } from '@/components/ui'
import { toast } from '@/store/toast'

export default function NotesPage() {
  const [notes, setNotes] = useState<Note[]>([])
  const [loading, setLoading] = useState(false)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [editingId, setEditingId] = useState<number | null>(null)

  async function load() {
    setLoading(true)
    try {
      const data = await listNotes()
      setNotes(data.items)
    } catch (err) {
      toast.error('Failed to load notes')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  async function handleCreate() {
    if (!title.trim() || !content.trim()) {
      toast.error('Title and content are required')
      return
    }
    try {
      if (editingId) {
        const updated = await updateNote(editingId, { title, content })
        setNotes((items) => items.map((item) => (item.id === editingId ? updated : item)))
        setEditingId(null)
        toast.success('Note updated')
      } else {
        const n = await createNote({ title, content })
        setNotes((s) => [n, ...s])
        toast.success('Note created')
      }
      setTitle('')
      setContent('')
    } catch {
      toast.error(editingId ? 'Failed to update note' : 'Failed to create note')
    }
  }

  async function handleDelete(id: number) {
    try {
      await deleteNote(id)
      setNotes((items) => items.filter((item) => item.id !== id))
      toast.success('Note deleted')
    } catch {
      toast.error('Failed to delete note')
    }
  }

  return (
    <div>
      <PageHeader title="Notes" />
      <Card>
        <div className="flex gap-2">
          <Input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
          <Input placeholder="Content" value={content} onChange={(e) => setContent(e.target.value)} />
          <Button onClick={() => void handleCreate()}>{editingId ? 'Save changes' : 'Create'}</Button>
          {editingId && <Button variant="ghost" onClick={() => { setEditingId(null); setTitle(''); setContent('') }}>Cancel</Button>}
        </div>
      </Card>

      <div className="mt-4 grid gap-4">
        {loading && <div>Loading notes...</div>}
        {!loading && notes.length === 0 && <div>No notes yet</div>}
        {notes.map((n) => (
          <Card key={n.id}>
            <div className="flex items-start justify-between gap-3">
              <h3 className="font-semibold">{n.title}</h3>
              <div className="flex gap-2">
                <Button size="sm" variant="ghost" onClick={() => { setEditingId(n.id); setTitle(n.title); setContent(n.content) }}>Edit</Button>
                <Button size="sm" variant="danger" onClick={() => void handleDelete(n.id)}>Delete</Button>
              </div>
            </div>
            <p className="text-sm text-slate-600 dark:text-slate-300">{n.content}</p>
          </Card>
        ))}
      </div>
    </div>
  )
}
