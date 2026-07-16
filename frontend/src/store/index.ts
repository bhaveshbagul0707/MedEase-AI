import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  setUser: (user: User | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        set({ user: null, isAuthenticated: false })
      },
    }),
    {
      name: 'medease-auth',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    },
  ),
)

interface ThemeState {
  isDark: boolean
  toggleTheme: () => void
  setDark: (value: boolean) => void
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      isDark: false,
      toggleTheme: () =>
        set((state) => {
          const next = !state.isDark
          document.documentElement.classList.toggle('dark', next)
          return { isDark: next }
        }),
      setDark: (value) => {
        document.documentElement.classList.toggle('dark', value)
        set({ isDark: value })
      },
    }),
    { name: 'medease-theme' },
  ),
)
