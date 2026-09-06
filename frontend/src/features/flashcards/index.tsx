import { useEffect, useState } from 'react'
import { Layers } from 'lucide-react'
import { api, type APIResponse, type PaginatedResponse } from '@/lib/api'
import { Card, Button, Input } from '@/components/ui'
import { PageHeader } from '@/components/layout/PageHeader'
import { toast } from '@/store/toast'

type Flashcard = { id: number; front: string; back: string; is_learned: boolean }
export default function FlashcardsPage() {
  const [cards, setCards] = useState<Flashcard[]>([])
  const [index, setIndex] = useState(0)
  const [revealed, setRevealed] = useState(false)
  const [loading, setLoading] = useState(true)
  const [noteId, setNoteId] = useState('')
  const [generating, setGenerating] = useState(false)
  useEffect(() => { api.get<APIResponse<PaginatedResponse<Flashcard>>>('/flashcards/').then((r) => setCards(r.data.data.items)).catch(() => toast.error('Failed to load flashcards')).finally(() => setLoading(false)) }, [])
  const card = cards[index]
  async function generate() {
    const parsedNoteId = Number(noteId)
    if (!Number.isInteger(parsedNoteId) || parsedNoteId <= 0) {
      toast.error('Enter a valid note ID')
      return
    }
    setGenerating(true)
    try {
      const response = await api.post<APIResponse<Flashcard[]>>('/flashcards/generate/from-note', { note_id: parsedNoteId, count: 5 })
      setCards((current) => [...response.data.data, ...current])
      setIndex(0)
      setRevealed(false)
      toast.success('Flashcards generated')
      setNoteId('')
    } catch {
      toast.error('Unable to generate cards. Check that the note exists.')
    } finally {
      setGenerating(false)
    }
  }
  async function review(correct: boolean) {
    if (!card) return
    try { await api.post(`/flashcards/${card.id}/review`, { correct }); setIndex((value) => (value + 1) % cards.length); setRevealed(false) } catch { toast.error('Review could not be saved') }
  }
  return <div className="space-y-6"><PageHeader title="Flashcards" description="Review your cards and build durable recall." /><Card><div className="flex flex-col gap-3 sm:flex-row"><Input value={noteId} onChange={(event) => setNoteId(event.target.value)} placeholder="Note ID" /><Button onClick={() => void generate()} disabled={generating}>{generating ? 'Generating...' : 'Generate from note'}</Button></div><p className="mt-2 text-xs text-slate-500">Create a note first, then enter its ID to generate cards.</p></Card>{loading && <Card>Loading flashcards...</Card>}{!loading && !card && <Card className="text-center"><Layers className="mx-auto mb-3 h-10 w-10 text-slate-400" /><p>No flashcards yet. Generate them from a note or PDF.</p></Card>}{card && <Card className="mx-auto max-w-2xl text-center"><p className="mb-8 text-xs text-slate-500">{index + 1} of {cards.length}</p><h2 className="text-xl font-semibold">{card.front}</h2>{revealed ? <p className="mt-8 rounded-lg bg-slate-50 p-5 dark:bg-slate-800">{card.back}</p> : <Button className="mt-8" onClick={() => setRevealed(true)}>Reveal answer</Button>}{revealed && <div className="mt-6 flex justify-center gap-3"><Button variant="danger" onClick={() => void review(false)}>Need practice</Button><Button onClick={() => void review(true)}>Got it</Button></div>}</Card>}</div>
}
