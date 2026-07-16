import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import ProfilePage from '@/features/profile/ProfilePage'
import { useAuthStore } from '@/store'

vi.mock('@/features/auth/api', () => ({
  getMe: vi.fn().mockResolvedValue({
    data: {
      id: 1,
      email: 'test@medease.ai',
      full_name: 'Test Student',
      program: 'MBBS',
      year_of_study: 2,
      is_active: true,
      is_verified: true,
      created_at: '2026-01-01T00:00:00Z',
    },
  }),
}))

function renderProfile() {
  useAuthStore.setState({
    user: {
      id: 1,
      email: 'test@medease.ai',
      full_name: 'Test Student',
      program: 'MBBS',
      year_of_study: 2,
      is_active: true,
      created_at: '2026-01-01T00:00:00Z',
    },
    isAuthenticated: true,
  })

  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ProfilePage />
      </BrowserRouter>
    </QueryClientProvider>,
  )
}

describe('ProfilePage', () => {
  it('renders user profile information', async () => {
    renderProfile()
    expect(await screen.findByText('Test Student')).toBeInTheDocument()
    expect(screen.getAllByText('test@medease.ai').length).toBeGreaterThan(0)
    expect(screen.getAllByText('MBBS').length).toBeGreaterThan(0)
  })
})
