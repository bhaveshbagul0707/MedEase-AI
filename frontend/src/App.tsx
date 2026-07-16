import { AppRoutes } from '@/routes'
import { useSessionRestore } from '@/hooks/useSessionRestore'

function App() {
  useSessionRestore()
  return <AppRoutes />
}

export default App
