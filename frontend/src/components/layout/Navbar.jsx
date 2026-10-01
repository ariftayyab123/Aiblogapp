/**
 * Navigation bar component - editorial masthead.
 */
import { Link, useLocation } from 'react-router-dom';
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline';
import { useTheme } from '../../contexts/ThemeContext';
import { useAuth } from '../../contexts/AuthContext';

export default function Navbar() {
  const { isDark, toggle } = useTheme();
  const { isAuthenticated, logout, user } = useAuth();
  const location = useLocation();
  const isLoginPage = location.pathname === '/login';
  const isRegisterPage = location.pathname === '/register';
  const navItems = isAuthenticated
    ? [
        { name: 'Generate', path: '/' },
        { name: 'Blog Posts', path: '/blogs' },
        { name: 'Analytics', path: '/analytics' },
      ]
    : [];

  const quietLink =
    'rounded-lg px-3 py-2 text-sm font-medium text-ink-600 transition-colors duration-200 ' +
    'hover:bg-ink-100 hover:text-ink-950 dark:text-ink-400 dark:hover:bg-ink-800 dark:hover:text-ink-50';

  return (
    <nav className="sticky top-0 z-nav border-b border-ink-200 bg-paper dark:border-ink-800 dark:bg-ink-950">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Wordmark */}
          <Link
            to="/"
            className="group flex items-center gap-2.5 rounded-lg transition-opacity duration-200 hover:opacity-70"
          >
            <img
              src="/ai-blog-icon.svg"
              alt=""
              aria-hidden="true"
              className="h-8 w-8 rounded-md ring-1 ring-ink-900/10 dark:ring-ink-50/10"
            />
            <span className="font-display text-lg font-semibold tracking-tight text-ink-950 dark:text-ink-50">
              Blog Generator
            </span>
          </Link>

          {/* Navigation */}
          <div className="hidden items-center gap-1 md:flex">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  aria-current={isActive ? 'page' : undefined}
                  className={`relative rounded-lg px-4 py-2 text-sm font-medium transition-colors duration-200 ${
                    isActive
                      ? 'text-ink-950 dark:text-ink-50'
                      : 'text-ink-600 hover:text-ink-950 dark:text-ink-400 dark:hover:text-ink-50'
                  }`}
                >
                  {item.name}
                  {isActive && (
                    <span className="absolute inset-x-3 bottom-1 h-0.5 bg-accent-500" />
                  )}
                </Link>
              );
            })}
          </div>

          <div className="flex items-center gap-2">
            {isAuthenticated ? (
              <>
                <button onClick={logout} className={`hidden cursor-pointer md:inline-flex ${quietLink}`}>
                  Logout
                </button>
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-ink-900 text-sm font-semibold text-white dark:bg-ink-50 dark:text-ink-950">
                  {(user?.email || user?.username || 'U').charAt(0).toUpperCase()}
                </div>
              </>
            ) : (
              <>
                {!isLoginPage && (
                  <Link to="/login" className={quietLink}>
                    Login
                  </Link>
                )}
                {!isRegisterPage && (
                  <Link
                    to="/register"
                    className="hidden rounded-lg bg-ink-900 px-3 py-2 text-sm font-medium text-white transition-colors duration-200 hover:bg-ink-700 sm:inline-flex dark:bg-ink-50 dark:text-ink-950 dark:hover:bg-white"
                  >
                    Register
                  </Link>
                )}
              </>
            )}
            <button
              onClick={toggle}
              className="cursor-pointer rounded-lg p-2 transition-colors duration-200 hover:bg-ink-100 dark:hover:bg-ink-800"
              aria-label={isDark ? 'Switch to light theme' : 'Switch to dark theme'}
            >
              {isDark ? (
                <SunIcon className="h-5 w-5 text-ink-400" />
              ) : (
                <MoonIcon className="h-5 w-5 text-ink-600" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {navItems.length > 0 && (
          <div className="flex items-center gap-1 border-t border-ink-200 py-2 md:hidden dark:border-ink-800">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  aria-current={isActive ? 'page' : undefined}
                  className={`flex-1 rounded-lg px-3 py-2 text-center text-sm font-medium transition-colors duration-200 ${
                    isActive
                      ? 'bg-ink-100 text-ink-950 dark:bg-ink-800 dark:text-ink-50'
                      : 'text-ink-600 hover:bg-ink-100 dark:text-ink-400 dark:hover:bg-ink-800'
                  }`}
                >
                  {item.name}
                </Link>
              );
            })}
          </div>
        )}
        <div className="flex items-center gap-2 pb-3 md:hidden">
          {isAuthenticated ? (
            <button onClick={logout} className={`flex-1 cursor-pointer ${quietLink}`}>
              Logout
            </button>
          ) : (
            <>
              {!isLoginPage && (
                <Link to="/login" className={`flex-1 text-center ${quietLink}`}>
                  Login
                </Link>
              )}
              {!isRegisterPage && (
                <Link
                  to="/register"
                  className="flex-1 rounded-lg bg-ink-900 px-3 py-2 text-center text-sm font-medium text-white transition-colors duration-200 hover:bg-ink-700 dark:bg-ink-50 dark:text-ink-950"
                >
                  Register
                </Link>
              )}
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
