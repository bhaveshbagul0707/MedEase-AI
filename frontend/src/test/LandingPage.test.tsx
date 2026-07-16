import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import LandingPage from '@/features/landing/LandingPage'

describe('LandingPage', () => {
  it('renders the tagline', () => {
    render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>,
    )
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(/medical student's journey/i)
  })

  it('renders get started button', () => {
    render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>,
    )
    expect(screen.getByText('Get Started')).toBeInTheDocument()
  })
})
