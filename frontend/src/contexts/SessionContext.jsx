/**
 * Session Context for anonymous user tracking.
 * Generates and stores a UUID for each user session.
 */
import { createContext, useContext, useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';

const SESSION_KEY = 'ai_blog_session_id';

const SessionContext = createContext();

export function SessionProvider({ children }) {
  const [sessionId, setSessionId] = useState(() => {
    const stored = localStorage.getItem(SESSION_KEY);
    if (stored) return stored;
    const newId = uuidv4();
    localStorage.setItem(SESSION_KEY, newId);
    return newId;
  });

  const [isIdentified, setIsIdentified] = useState(false);

  useEffect(() => {
    // Validate UUID format
    const isValid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(sessionId);
    setIsIdentified(isValid);

    if (!isValid) {
      const newId = uuidv4();
      localStorage.setItem(SESSION_KEY, newId);
      setSessionId(newId);
    }
  }, [sessionId]);

  const resetSession = () => {
    const newId = uuidv4();
    localStorage.setItem(SESSION_KEY, newId);
    setSessionId(newId);
  };

  return (
    <SessionContext.Provider value={{ sessionId, isIdentified, resetSession }}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within SessionProvider');
  }
  return context;
}
