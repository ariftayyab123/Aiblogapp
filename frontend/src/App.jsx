import { Suspense, lazy } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
import Navbar from './components/layout/Navbar'
import ProtectedRoute from './components/layout/ProtectedRoute'

const HomePage = lazy(() => import('./pages/HomePage'))
const BlogListPage = lazy(() => import('./pages/BlogListPage'))
const BlogDetailPage = lazy(() => import('./pages/BlogDetailPage'))
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'))
const SharedBlogPage = lazy(() => import('./pages/SharedBlogPage'))
const LoginPage = lazy(() => import('./pages/LoginPage'))
const RegisterPage = lazy(() => import('./pages/RegisterPage'))

function App() {
  const location = useLocation()
  const isSharePage = location.pathname.startsWith('/share/')
  const isAuthPage =
    location.pathname === '/login' || location.pathname === '/register'
  const hideNavbar = isSharePage || isAuthPage

  return (
    <div className="min-h-screen relative overflow-x-hidden">
      {!hideNavbar && <Navbar />}
      <main className={isAuthPage ? '' : 'container mx-auto px-4 py-8'}>
        <Suspense fallback={<PageLoader isAuthPage={isAuthPage} />}>
          <Routes>
            <Route path="/" element={<ProtectedRoute><HomePage /></ProtectedRoute>} />
            <Route path="/blogs" element={<ProtectedRoute><BlogListPage /></ProtectedRoute>} />
            <Route path="/blog/:id" element={<ProtectedRoute><BlogDetailPage /></ProtectedRoute>} />
            <Route path="/share/:slug" element={<SharedBlogPage />} />
            <Route path="/analytics" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Routes>
        </Suspense>
      </main>
    </div>
  )
}

function PageLoader({ isAuthPage }) {
  return (
    <div className={isAuthPage ? 'min-h-screen flex items-center justify-center px-4' : 'py-12'}>
      <div className="mx-auto max-w-md rounded-xl border border-ink-200 bg-white px-6 py-8 text-center shadow-e-sm dark:border-ink-800 dark:bg-ink-900">
        <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-ink-200 border-t-ink-900 dark:border-ink-800 dark:border-t-ink-100" />
        <p className="mt-4 text-sm font-medium text-ink-700 dark:text-ink-300">Loading page...</p>
      </div>
    </div>
  )
}

export default App
