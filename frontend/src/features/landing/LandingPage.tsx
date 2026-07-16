import { Link } from 'react-router-dom'
import {
  Activity,
  BarChart3,
  BookOpen,
  Bot,
  Calendar,
  FileText,
  Layers,
  Stethoscope,
  Users,
} from 'lucide-react'
import { Button } from '@/components/ui'
import { ROUTES } from '@/routes/paths'

const features = [
  { icon: Bot, title: 'AI Tutor', description: 'Get explanations, mnemonics, and viva questions powered by Gemini AI.' },
  { icon: FileText, title: 'PDF Chat', description: 'Upload textbooks and chat with your study materials using RAG.' },
  { icon: BookOpen, title: 'Smart Notes', description: 'Create, organize, and share rich-text notes by subject.' },
  { icon: Layers, title: 'Flashcards', description: 'Auto-generate flashcards from notes and PDFs for spaced repetition.' },
  { icon: Calendar, title: 'Study Planner', description: 'AI-generated schedules based on your exams and study hours.' },
  { icon: Stethoscope, title: 'Clinical Cases', description: 'Practice diagnosis with AI-evaluated patient case simulations.' },
  { icon: Users, title: 'Community', description: 'Connect with peers, share notes, and discuss medical topics.' },
  { icon: BarChart3, title: 'Analytics', description: 'Track study hours, quiz scores, and attendance trends.' },
]

const programs = ['MBBS', 'BDS', 'Nursing', 'Pharmacy', 'Physiotherapy', 'BAMS', 'BHMS']

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-slate-950">
      {/* Header */}
      <header className="border-b border-slate-200 dark:border-slate-800">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <Activity className="h-7 w-7 text-primary" />
            <span className="text-xl font-bold text-slate-900 dark:text-white">MedEase AI</span>
          </div>
          <div className="flex items-center gap-3">
            <Link to={ROUTES.LOGIN}>
              <Button variant="ghost">Sign In</Button>
            </Link>
            <Link to={ROUTES.REGISTER}>
              <Button>Get Started</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-b from-primary-50 to-white py-20 dark:from-slate-900 dark:to-slate-950 sm:py-32">
        <div className="mx-auto max-w-7xl px-4 text-center sm:px-6 lg:px-8">
          <div className="inline-flex items-center rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary">
            AI-Powered Medical Education
          </div>
          <h1 className="mt-6 text-4xl font-bold tracking-tight text-slate-900 dark:text-white sm:text-6xl">
            One platform for every
            <span className="text-primary"> medical student&apos;s </span>
            journey.
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-600 dark:text-slate-400">
            MedEase AI combines AI tutoring, PDF chat, smart notes, quizzes, flashcards, and clinical
            case simulations — built for MBBS, BDS, Nursing, Pharmacy, and allied health students.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link to={ROUTES.REGISTER}>
              <Button size="lg">Start Learning Free</Button>
            </Link>
            <Link to={ROUTES.LOGIN}>
              <Button variant="secondary" size="lg">
                Sign In
              </Button>
            </Link>
          </div>

          <div className="mt-12 flex flex-wrap items-center justify-center gap-3">
            {programs.map((program) => (
              <span
                key={program}
                className="rounded-full border border-slate-200 bg-white px-4 py-1.5 text-sm font-medium text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
              >
                {program}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 sm:py-28">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white sm:text-4xl">
              Everything you need to excel
            </h2>
            <p className="mt-4 text-lg text-slate-600 dark:text-slate-400">
              A complete toolkit designed for the modern medical student.
            </p>
          </div>

          <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="rounded-xl border border-slate-200 bg-white p-6 transition-shadow hover:shadow-lg dark:border-slate-800 dark:bg-slate-900"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="mt-4 text-lg font-semibold text-slate-900 dark:text-white">
                  {feature.title}
                </h3>
                <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-primary py-16">
        <div className="mx-auto max-w-4xl px-4 text-center sm:px-6">
          <h2 className="text-3xl font-bold text-white">Ready to transform your studies?</h2>
          <p className="mt-4 text-lg text-primary-100">
            Join thousands of medical students using AI to study smarter, not harder.
          </p>
          <Link to={ROUTES.REGISTER} className="mt-8 inline-block">
            <Button
              size="lg"
              className="bg-white text-primary hover:bg-primary-50"
            >
              Create Free Account
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 py-8 dark:border-slate-800">
        <div className="mx-auto max-w-7xl px-4 text-center text-sm text-slate-500 sm:px-6">
          © 2026 MedEase AI. All rights reserved.
        </div>
      </footer>
    </div>
  )
}
