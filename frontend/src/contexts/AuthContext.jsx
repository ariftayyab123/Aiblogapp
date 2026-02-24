import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { AUTH_TOKEN_STORAGE_KEY, authApi } from '../services/api';

const AUTH_USER_STORAGE_KEY = 'auth_user';
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem(AUTH_TOKEN_STORAGE_KEY) || '');
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem(AUTH_USER_STORAGE_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  });

  const persistAuth = (newToken, userData) => {
    if (!newToken) return;
    localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, newToken);
    setToken(newToken);
    if (userData) {
      localStorage.setItem(AUTH_USER_STORAGE_KEY, JSON.stringify(userData));
      setUser(userData);
    }
  };

  const login = async (email, password) => {
    const response = await authApi.login({ email, password });
    persistAuth(response.data?.token || '', response.data?.user || null);
    return response.data;
  };

  const register = async (email, password, confirmPassword) => {
    const response = await authApi.register({
      email,
      password,
      confirm_password: confirmPassword,
    });
    persistAuth(response.data?.token || '', response.data?.user || null);
    return response.data;
  };

  const logout = () => {
    localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
    localStorage.removeItem(AUTH_USER_STORAGE_KEY);
    setToken('');
    setUser(null);
  };

  useEffect(() => {
    const sync = () => {
      setToken(localStorage.getItem(AUTH_TOKEN_STORAGE_KEY) || '');
      const raw = localStorage.getItem(AUTH_USER_STORAGE_KEY);
      if (!raw) {
        setUser(null);
        return;
      }
      try {
        setUser(JSON.parse(raw));
      } catch {
        setUser(null);
      }
    };
    window.addEventListener('storage', sync);
    window.addEventListener('auth-cleared', sync);
    return () => {
      window.removeEventListener('storage', sync);
      window.removeEventListener('auth-cleared', sync);
    };
  }, []);

  const value = useMemo(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token),
      login,
      register,
      logout,
    }),
    [token, user]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
