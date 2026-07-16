import { Outlet } from 'react-router-dom'
import { Activity } from 'lucide-react'

export function AuthLayout() {
  return (
    <div className="flex min-h-screen">
      <div className="hidden w-1/2 bg-gradient-to-br from-primary-600 to-secondary-500 lg:flex lg:flex-col lg:justify-between lg:p-12">
        <div className="flex items-center gap-3 text-white">
          <Activity className="h-8 w-8" />
          <span className="text-2xl font-bold">MedEase AI</span>
        </div>
        <div className="text-white">
          <h2 className="text-3xl font-bold leading-tight">
            One platform for every medical student&apos;s journey.
          </h2>
          <p className="mt-4 text-lg text-white/80">
            AI-powered learning for MBBS, BDS, Nursing, Pharmacy, and more.
          </p>
        </div>
        <p className="text-sm text-white/60">© 2026 MedEase AI. All rights reserved.</p>
      </div>

      <div className="flex w-full flex-col justify-center px-6 py-12 lg:w-1/2 lg:px-16">
        <div className="mx-auto w-full max-w-md">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
