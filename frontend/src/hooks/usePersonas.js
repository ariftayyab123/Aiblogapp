/**
 * Hook for fetching and managing personas.
 */
import { useState, useEffect, useCallback } from 'react';
import { personaApi } from '../services/api';
import { useToast } from '../contexts/ToastContext';

export function usePersonas() {
  const { error } = useToast();
  const [state, setState] = useState({
    personas: [],
    isLoading: true,
    error: null,
  });

  const fetchPersonas = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true }));

    try {
      const response = await personaApi.list();
      const payload = response.data;
      const personas = Array.isArray(payload?.results)
        ? payload.results
        : Array.isArray(payload)
          ? payload
          : null;

      if (!personas) {
        throw new Error('Invalid personas response shape. Check VITE_API_URL and backend /api/personas/ endpoint.');
      }

      setState({
        personas,
        isLoading: false,
        error: null,
      });
    } catch (err) {
      setState({
        personas: [],
        isLoading: false,
        error: err.message,
      });
      error('Failed to load personas');
    }
  }, [error]);

  useEffect(() => {
    fetchPersonas();
  }, [fetchPersonas]);

  const getPersonaBySlug = useCallback((slug) => {
    if (!Array.isArray(state.personas)) return null;
    return state.personas.find(p => p.slug === slug);
  }, [state.personas]);

  return {
    ...state,
    fetchPersonas,
    getPersonaBySlug,
  };
}
