import { Link, useLocation } from 'react-router-dom'
import { Bot, FileText, HelpCircle, LayoutDashboard, NotebookPen } from 'lucide-react'
import { cn } from '@/lib/utils'
import { ROUTES } from '@/routes/paths'

const mobileNavItems = [
  { label: 'Home', path: ROUTES.DASHBOARD, icon: LayoutDashboard },
  { label: 'Notes', path: ROUTES.NOTES, icon: NotebookPen },
  { label: 'AI Tutor', path: ROUTES.AI_TUTOR, icon: Bot },
  { label: 'Quiz', path: ROUTES.QUIZ, icon: HelpCircle },
  { label: 'PDF', path: ROUTES.PDF_CHAT, icon: FileText },
]

export function MobileNav() {
  const location = useLocation()

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 border-t border-slate-200 bg-white/95 backdrop-blur dark:border-slate-800 dark:bg-slate-900/95 lg:hidden">
      <div className="flex items-center justify-around px-2 py-2">
        {mobileNavItems.map((item) => {
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                'flex flex-col items-center gap-0.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors',
                isActive
                  ? 'text-primary'
                  : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200',
              )}
            >
              <item.icon className={cn('h-5 w-5', isActive && 'text-primary')} />
              {item.label}
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
