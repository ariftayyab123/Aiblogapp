import { Routes, Route, useLocation } from 'react-router-dom'
import Navbar from './components/layout/Navbar'
import HomePage from './pages/HomePage'
import BlogListPage from './pages/BlogListPage'
import BlogDetailPage from './pages/BlogDetailPage'
import AnalyticsPage from './pages/AnalyticsPage'
import SharedBlogPage from './pages/SharedBlogPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProtectedRoute from './components/layout/ProtectedRoute'

function App() {
  const location = useLocation()
  const isSharePage = location.pathname.startsWith('/share/')
  const isAuthPage =
    location.pathname === '/login' || location.pathname === '/register'
  const hideNavbar = isSharePage || isAuthPage

  return (
    <div className="min-h-screen relative overflow-x-hidden">
      {!isAuthPage && (
        <div className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute -top-20 -left-10 w-72 h-72 bg-primary-200/40 dark:bg-primary-900/20 blur-3xl rounded-full" />
          <div className="absolute top-8 -right-10 w-80 h-80 bg-sky-200/40 dark:bg-sky-900/20 blur-3xl rounded-full" />
        </div>
      )}
      {!hideNavbar && <Navbar />}
      <main className={isAuthPage ? '' : 'container mx-auto px-4 py-8'}>
        <Routes>
          <Route path="/" element={<ProtectedRoute><HomePage /></ProtectedRoute>} />
          <Route path="/blogs" element={<ProtectedRoute><BlogListPage /></ProtectedRoute>} />
          <Route path="/blog/:id" element={<ProtectedRoute><BlogDetailPage /></ProtectedRoute>} />
          <Route path="/share/:slug" element={<SharedBlogPage />} />
          <Route path="/analytics" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
