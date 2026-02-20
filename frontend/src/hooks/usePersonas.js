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
      setState({
        personas: response.data.results || response.data,
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
    return state.personas.find(p => p.slug === slug);
  }, [state.personas]);

  return {
    ...state,
    fetchPersonas,
    getPersonaBySlug,
  };
}
