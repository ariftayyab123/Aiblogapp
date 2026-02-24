/**
 * Navigation bar component.
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
  const navItems = [
    ...(isAuthenticated ? [{ name: 'Generate', path: '/' }] : []),
    ...(isAuthenticated ? [{ name: 'Blog Posts', path: '/blogs' }] : []),
    ...(isAuthenticated ? [{ name: 'Analytics', path: '/analytics' }] : []),
  ];

  return (
    <nav className="bg-white/85 dark:bg-gray-800/85 backdrop-blur border-b border-gray-200/80 dark:border-gray-700 sticky top-0 z-40">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <img
              src="/ai-blog-icon.svg"
              alt="AI Blog Generator logo"
              className="w-8 h-8 rounded-lg"
            />
            <span className="font-semibold tracking-tight text-gray-900 dark:text-white">
              Blog Generator
            </span>
          </Link>

          {/* Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400'
                      : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700'
                  }`}
                >
                  {item.name}
                </Link>
              );
            })}
          </div>

          <div className="flex items-center gap-2">
            {isAuthenticated ? (
              <>
                <button
                  onClick={logout}
                  className="px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700 transition-colors"
                >
                  Logout
                </button>
                <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 flex items-center justify-center text-sm font-semibold">
                  {(user?.email || user?.username || 'U').charAt(0).toUpperCase()}
                </div>
              </>
            ) : (
              <>
                {!isLoginPage && (
                  <Link
                    to="/login"
                    className="px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700 transition-colors"
                  >
                    Login
                  </Link>
                )}
                {!isRegisterPage && (
                  <Link
                    to="/register"
                    className="hidden sm:inline-flex px-3 py-2 rounded-lg text-sm font-medium text-primary-700 bg-primary-50 dark:bg-primary-900/20 dark:text-primary-400 transition-colors"
                  >
                    Register
                  </Link>
                )}
              </>
            )}
            <button
              onClick={toggle}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              aria-label="Toggle theme"
            >
              {isDark ? (
                <SunIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              ) : (
                <MoonIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden flex items-center gap-1 py-2 border-t border-gray-200 dark:border-gray-700">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex-1 text-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400'
                    : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700'
                }`}
              >
                {item.name}
              </Link>
            );
          })}
        </div>
        <div className="md:hidden flex items-center gap-2 pb-3">
          {isAuthenticated ? (
            <button
              onClick={logout}
              className="flex-1 px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700 transition-colors"
            >
              Logout
            </button>
          ) : (
            <>
              {!isLoginPage && (
                <Link
                  to="/login"
                  className="flex-1 text-center px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700 transition-colors"
                >
                  Login
                </Link>
              )}
              {!isRegisterPage && (
                <Link
                  to="/register"
                  className="flex-1 text-center px-3 py-2 rounded-lg text-sm font-medium text-primary-700 bg-primary-50 dark:bg-primary-900/20 dark:text-primary-400 transition-colors"
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
