import { ROUTES } from '@/routes/paths'

export const PAGE_TITLES: Record<string, string> = {
  [ROUTES.DASHBOARD]: 'Dashboard',
  [ROUTES.AI_TUTOR]: 'AI Tutor',
  [ROUTES.NOTES]: 'Notes',
  [ROUTES.PDF_CHAT]: 'PDF Chat',
  [ROUTES.FLASHCARDS]: 'Flashcards',
  [ROUTES.QUIZ]: 'Quiz',
  [ROUTES.ATTENDANCE]: 'Attendance',
  [ROUTES.STUDY_PLANNER]: 'Study Planner',
  [ROUTES.COMMUNITY]: 'Community',
  [ROUTES.CLINICAL_CASES]: 'Clinical Cases',
  [ROUTES.ANALYTICS]: 'Analytics',
  [ROUTES.PROFILE]: 'Profile',
  [ROUTES.SETTINGS]: 'Settings',
}

export function getPageTitle(pathname: string): string {
  return PAGE_TITLES[pathname] || 'MedEase AI'
}

export function getGreeting(): string {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 17) return 'Good afternoon'
  return 'Good evening'
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}
