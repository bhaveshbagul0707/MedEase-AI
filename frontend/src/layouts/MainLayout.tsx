import { useState } from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'
import {
  Activity,
  BarChart3,
  Bot,
  Calendar,
  CalendarCheck,
  FileText,
  HelpCircle,
  Layers,
  LayoutDashboard,
  LogOut,
  Menu,
  Moon,
  NotebookPen,
  Settings,
  Stethoscope,
  Sun,
  Users,
  X,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { getPageTitle } from '@/lib/formatters'
import { MobileNav } from '@/components/layout/MobileNav'
import { UserMenu } from '@/components/layout/UserMenu'
import { ToastContainer } from '@/components/ui'
import { useTheme } from '@/hooks/useTheme'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { NAV_ITEMS, ROUTES } from '@/routes/paths'

const iconMap = {
  LayoutDashboard,
  Bot,
  NotebookPen,
  FileText,
  Layers,
  HelpCircle,
  CalendarCheck,
  Calendar,
  Users,
  Stethoscope,
  BarChart3,
} as const

export function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const { isDark, toggleTheme } = useTheme()
  const { logout } = useAuth()
  const pageTitle = getPageTitle(location.pathname)

  return (
    <div className="flex min-h-screen bg-background dark:bg-slate-950">
      <ToastContainer />

      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-slate-200 bg-white transition-transform duration-200 dark:border-slate-800 dark:bg-slate-900 lg:static lg:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        <div className="flex h-16 items-center justify-between border-b border-slate-200 px-6 dark:border-slate-800">
          <Link to={ROUTES.DASHBOARD} className="flex items-center gap-2">
            <Activity className="h-6 w-6 text-primary" />
            <span className="text-lg font-bold text-slate-900 dark:text-white">MedEase AI</span>
          </Link>
          <button className="lg:hidden" onClick={() => setSidebarOpen(false)} aria-label="Close menu">
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto p-4" aria-label="Main navigation">
          {NAV_ITEMS.map((item) => {
            const Icon = iconMap[item.icon as keyof typeof iconMap]
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary/10 text-primary'
                    : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800',
                )}
              >
                <Icon className="h-5 w-5" />
                {item.label}
              </Link>
            )
          })}
        </nav>

        <div className="border-t border-slate-200 p-4 dark:border-slate-800">
          <Link
            to={ROUTES.SETTINGS}
            onClick={() => setSidebarOpen(false)}
            className={cn(
              'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
              location.pathname === ROUTES.SETTINGS
                ? 'bg-primary/10 text-primary'
                : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800',
            )}
          >
            <Settings className="h-5 w-5" />
            Settings
          </Link>
          <button
            onClick={() => logout()}
            className="mt-1 flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950"
          >
            <LogOut className="h-5 w-5" />
            Logout
          </button>
        </div>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-slate-200 bg-white/80 px-4 backdrop-blur dark:border-slate-800 dark:bg-slate-900/80 lg:px-8">
          <button
            className="lg:hidden"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open menu"
          >
            <Menu className="h-6 w-6" />
          </button>

          <h1 className="text-lg font-semibold text-slate-900 dark:text-white lg:hidden">
            {pageTitle}
          </h1>

          <div className="hidden flex-1 lg:block">
            <p className="text-sm text-slate-500 dark:text-slate-400">{pageTitle}</p>
          </div>

          <div className="ml-auto flex items-center gap-2">
            <button
              onClick={toggleTheme}
              className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"
              aria-label="Toggle theme"
            >
              {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </button>
            <UserMenu />
          </div>
        </header>

        <main className="flex-1 p-4 pb-24 lg:p-8 lg:pb-8">
          <Outlet />
        </main>

        <MobileNav />
      </div>
    </div>
  )
}
