import { useLocation } from 'react-router-dom'
import { Construction } from 'lucide-react'
import { Card } from '@/components/ui'

export default function PlaceholderPage() {
  const location = useLocation()
  const pageName = location.pathname
    .split('/')
    .filter(Boolean)
    .map((s) => s.replace(/-/g, ' '))
    .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
    .join(' ')

  return (
    <div className="mx-auto max-w-2xl py-12">
      <Card className="text-center">
        <Construction className="mx-auto h-12 w-12 text-secondary" />
        <h1 className="mt-4 text-2xl font-bold text-slate-900 dark:text-white">{pageName}</h1>
        <p className="mt-2 text-slate-500 dark:text-slate-400">
          This module is under development and will be available in an upcoming phase.
        </p>
      </Card>
    </div>
  )
}
