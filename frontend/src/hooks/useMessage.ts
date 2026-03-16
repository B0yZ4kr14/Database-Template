/**
 * useMessage Hook
 * ===============
 * Hook para exibir mensagens temporárias com cleanup automático
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { MESSAGE_TIMEOUT } from '../constants';

interface Message {
  type: 'success' | 'error' | 'warning' | 'info';
  text: string;
}

export function useMessage(defaultTimeout: number = MESSAGE_TIMEOUT) {
  const [message, setMessage] = useState<Message | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Cleanup ao desmontar
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const showMessage = useCallback((
    type: Message['type'],
    text: string,
    customTimeout?: number
  ) => {
    // Limpar timeout anterior
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    setMessage({ type, text });

    // Configurar novo timeout
    timeoutRef.current = setTimeout(() => {
      setMessage(null);
      timeoutRef.current = null;
    }, customTimeout ?? defaultTimeout);
  }, [defaultTimeout]);

  const clearMessage = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    setMessage(null);
  }, []);

  const showSuccess = useCallback((text: string, timeout?: number) => {
    showMessage('success', text, timeout);
  }, [showMessage]);

  const showError = useCallback((text: string, timeout?: number) => {
    showMessage('error', text, timeout);
  }, [showMessage]);

  const showWarning = useCallback((text: string, timeout?: number) => {
    showMessage('warning', text, timeout);
  }, [showMessage]);

  const showInfo = useCallback((text: string, timeout?: number) => {
    showMessage('info', text, timeout);
  }, [showMessage]);

  return {
    message,
    showMessage,
    clearMessage,
    showSuccess,
    showError,
    showWarning,
    showInfo,
  };
}
