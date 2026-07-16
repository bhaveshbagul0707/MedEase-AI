import { useEffect } from 'react'
import { useThemeStore } from '@/store'

export function useTheme() {
  const { isDark, toggleTheme, setDark } = useThemeStore()

  useEffect(() => {
    const stored = localStorage.getItem('medease-theme')
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        setDark(parsed.state?.isDark ?? false)
      } catch {
        setDark(false)
      }
    }
  }, [setDark])

  return { isDark, toggleTheme }
}
