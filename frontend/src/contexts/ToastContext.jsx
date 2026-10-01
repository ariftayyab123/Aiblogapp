/**
 * Toast Context for displaying notifications.
 */
import { createContext, useContext, useState, useCallback } from 'react';
import Toast from '../components/ui/Toast';

const ToastContext = createContext();

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const addToast = useCallback((message, type = 'info', duration = 5000) => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }

    return id;
  }, [removeToast]);

  const success = useCallback((message, duration) =>
    addToast(message, 'success', duration), [addToast]);

  const error = useCallback((message, duration) =>
    addToast(message, 'error', duration), [addToast]);

  const info = useCallback((message, duration) =>
    addToast(message, 'info', duration), [addToast]);

  const warning = useCallback((message, duration) =>
    addToast(message, 'warning', duration), [addToast]);

  return (
    <ToastContext.Provider value={{ addToast, removeToast, success, error, info, warning }}>
      {children}
      {/* Live region so screen readers announce toasts; pointer-events are off
          on the container so it never swallows clicks on the page beneath. */}
      <div
        aria-live="polite"
        aria-atomic="false"
        className="fixed top-4 left-1/2 z-toast flex w-full max-w-md -translate-x-1/2 flex-col gap-2 px-4 pointer-events-none"
      >
        {toasts.map(toast => (
          <div key={toast.id} className="pointer-events-auto">
            <Toast
              message={toast.message}
              type={toast.type}
              onClose={() => removeToast(toast.id)}
            />
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
}
