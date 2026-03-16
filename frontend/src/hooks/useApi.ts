/**
 * useApi Hook
 * ===========
 * Hook customizado para chamadas à API com timeout e cleanup
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { API_URL, FETCH_TIMEOUT, ERROR_MESSAGES } from '../constants';

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface FetchOptions extends RequestInit {
  timeout?: number;
}

export function useApi<T = unknown>() {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const abortControllerRef = useRef<AbortController | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Cleanup ao desmontar
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const fetchData = useCallback(async (
    endpoint: string,
    options: FetchOptions = {}
  ): Promise<T | null> => {
    const { timeout = FETCH_TIMEOUT, ...fetchOptions } = options;

    // Cancelar requisição anterior se existir
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Criar novo AbortController
    abortControllerRef.current = new AbortController();

    setState({ data: null, loading: true, error: null });

    try {
      // Configurar timeout
      const timeoutPromise = new Promise<never>((_, reject) => {
        timeoutRef.current = setTimeout(() => {
          abortControllerRef.current?.abort();
          reject(new Error(ERROR_MESSAGES.TIMEOUT_ERROR));
        }, timeout);
      });

      const fetchPromise = fetch(`${API_URL}${endpoint}`, {
        ...fetchOptions,
        signal: abortControllerRef.current.signal,
        headers: {
          'Content-Type': 'application/json',
          ...fetchOptions.headers,
        },
      });

      const response = await Promise.race([fetchPromise, timeoutPromise]);

      // Limpar timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.message || `HTTP ${response.status}: ${response.statusText}`
        );
      }

      const data = await response.json();
      setState({ data, loading: false, error: null });
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : ERROR_MESSAGES.UNKNOWN_ERROR;
      
      // Não tratar erro de abort como erro
      if (err instanceof Error && err.name === 'AbortError') {
        setState({ data: null, loading: false, error: null });
        return null;
      }

      setState({ data: null, loading: false, error: errorMessage });
      return null;
    }
  }, []);

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return {
    ...state,
    fetchData,
    reset,
  };
}

// Hook para POST requests
export function usePost<T = unknown>() {
  const { fetchData, loading, error, reset } = useApi<T>();

  const post = useCallback(async (
    endpoint: string,
    body: unknown,
    options: FetchOptions = {}
  ): Promise<T | null> => {
    return fetchData(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(body),
    });
  }, [fetchData]);

  return { post, loading, error, reset };
}

// Hook para GET requests
export function useGet<T = unknown>() {
  const { data, loading, error, fetchData, reset } = useApi<T>();

  const get = useCallback(async (
    endpoint: string,
    options: FetchOptions = {}
  ): Promise<T | null> => {
    return fetchData(endpoint, {
      ...options,
      method: 'GET',
    });
  }, [fetchData]);

  return { data, loading, error, get, reset };
}
