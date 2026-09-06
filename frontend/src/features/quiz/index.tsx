import { useState } from 'react'
import { api, type APIResponse } from '@/lib/api'
import { Card, Button } from '@/components/ui'
import { PageHeader } from '@/components/layout/PageHeader'
import { toast } from '@/store/toast'
type Question = { id: number; prompt: string; answer: string }
export default function QuizPage() {
  const [questions, setQuestions] = useState<Question[]>([])
  const [quizId, setQuizId] = useState<number | null>(null)
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [result, setResult] = useState<number | null>(null)
  async function start() { try { const generated = await api.post<APIResponse<{ quiz_id: number }>>('/quizzes/generate/from-flashcards'); const quiz = await api.get<APIResponse<{ questions: Question[] }>>(`/quizzes/${generated.data.data.quiz_id}`); setQuizId(generated.data.data.quiz_id); setQuestions(quiz.data.data.questions); setResult(null) } catch { toast.error('Create some flashcards before starting a quiz') } }
  async function submit() { if (!quizId) return; try { const response = await api.post<APIResponse<{ score: number }>>(`/quizzes/${quizId}/submit`, { answers: Object.entries(answers).map(([question_id, answer]) => ({ question_id: Number(question_id), answer })) }); setResult(response.data.data.score) } catch { toast.error('Quiz submission failed') } }
  return <div className="space-y-6"><PageHeader title="Quiz" description="Test yourself using your flashcard library." actions={<Button onClick={() => void start()}>Start quiz</Button>} />{!questions.length && <Card className="text-center text-slate-500">Start a quiz when you are ready.</Card>}{questions.map((question) => <Card key={question.id} title={question.prompt}><input className="input mt-3 w-full" value={answers[question.id] || ''} onChange={(event) => setAnswers((value) => ({ ...value, [question.id]: event.target.value }))} placeholder="Your answer" /></Card>)}{questions.length > 0 && <Button onClick={() => void submit()}>Submit quiz</Button>}{result !== null && <Card><p className="font-semibold">Score: {result}</p></Card>}</div>
}
