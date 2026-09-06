import { lazy, Suspense } from 'react'
import { Routes, Route } from 'react-router-dom'
import { ProtectedRoute, PublicRoute } from './guards'
import { ROUTES } from './paths'
import { MainLayout } from '@/layouts/MainLayout'
import { AuthLayout } from '@/layouts/AuthLayout'

const LandingPage = lazy(() => import('@/features/landing/LandingPage'))
const LoginPage = lazy(() => import('@/features/auth/LoginPage'))
const RegisterPage = lazy(() => import('@/features/auth/RegisterPage'))
const ForgotPasswordPage = lazy(() => import('@/features/auth/ForgotPasswordPage'))
const ResetPasswordPage = lazy(() => import('@/features/auth/ResetPasswordPage'))
const GoogleCallbackPage = lazy(() => import('@/features/auth/GoogleCallbackPage'))
const DashboardPage = lazy(() => import('@/features/dashboard/DashboardPage'))
const ProfilePage = lazy(() => import('@/features/profile/ProfilePage'))
const SettingsPage = lazy(() => import('@/features/settings/SettingsPage'))
const AITutorPage = lazy(() => import('@/features/ai-tutor'))
const NotesPage = lazy(() => import('@/features/notes/NotesPage'))
const PdfChatPage = lazy(() => import('@/features/pdf-chat'))
const FlashcardsPage = lazy(() => import('@/features/flashcards'))
const QuizPage = lazy(() => import('@/features/quiz'))
const AnalyticsPage = lazy(() => import('@/features/analytics'))
const AttendancePage = lazy(() => import('@/features/attendance/AttendancePage'))
const StudyPlannerPage = lazy(() => import('@/features/study-planner/StudyPlannerPage'))
const CommunityPage = lazy(() => import('@/features/community/CommunityPage'))
const ClinicalCasesPage = lazy(() => import('@/features/clinical-cases/ClinicalCasesPage'))

import { PageLoader } from '@/components/ui'

function withSuspense(Component: React.ComponentType) {
  return (
    <Suspense fallback={<PageLoader />}>
      <Component />
    </Suspense>
  )
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path={ROUTES.HOME} element={withSuspense(LandingPage)} />
      <Route path={ROUTES.GOOGLE_CALLBACK} element={withSuspense(GoogleCallbackPage)} />

      <Route element={<PublicRoute />}>
        <Route element={<AuthLayout />}>
          <Route path={ROUTES.LOGIN} element={withSuspense(LoginPage)} />
          <Route path={ROUTES.REGISTER} element={withSuspense(RegisterPage)} />
          <Route path={ROUTES.FORGOT_PASSWORD} element={withSuspense(ForgotPasswordPage)} />
          <Route path={ROUTES.RESET_PASSWORD} element={withSuspense(ResetPasswordPage)} />
        </Route>
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route element={<MainLayout />}>
          <Route path={ROUTES.DASHBOARD} element={withSuspense(DashboardPage)} />
          <Route path={ROUTES.AI_TUTOR} element={withSuspense(AITutorPage)} />
          <Route path={ROUTES.NOTES} element={withSuspense(NotesPage)} />
          <Route path={ROUTES.PDF_CHAT} element={withSuspense(PdfChatPage)} />
          <Route path={ROUTES.PDF_LIBRARY} element={withSuspense(PdfChatPage)} />
          <Route path={ROUTES.PDF_VIEWER} element={withSuspense(PdfChatPage)} />
          <Route path={ROUTES.FLASHCARDS} element={withSuspense(FlashcardsPage)} />
          <Route path={ROUTES.QUIZ} element={withSuspense(QuizPage)} />
          <Route path={ROUTES.ATTENDANCE} element={withSuspense(AttendancePage)} />
          <Route path={ROUTES.STUDY_PLANNER} element={withSuspense(StudyPlannerPage)} />
          <Route path={ROUTES.COMMUNITY} element={withSuspense(CommunityPage)} />
          <Route path={ROUTES.CLINICAL_CASES} element={withSuspense(ClinicalCasesPage)} />
          <Route path={ROUTES.ANALYTICS} element={withSuspense(AnalyticsPage)} />
          <Route path={ROUTES.STUDY_HISTORY} element={withSuspense(AnalyticsPage)} />
          <Route path={ROUTES.PROFILE} element={withSuspense(ProfilePage)} />
          <Route path={ROUTES.SETTINGS} element={withSuspense(SettingsPage)} />
        </Route>
      </Route>

      <Route path="*" element={<NavigateToHome />} />
    </Routes>
  )
}

function NavigateToHome() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-2xl font-bold">404 - Page Not Found</h1>
      <a href="/" className="btn-primary">
        Go Home
      </a>
    </div>
  )
}
