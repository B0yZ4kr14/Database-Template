import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  Save, 
  Clock, 
  Download,
  RotateCcw,
  FolderOpen,
  CheckCircle,
  Loader2,
  AlertTriangle,
  Trash2,
  X,
  Lightbulb,
  Database
} from 'lucide-react';
import type { BackupConfig, BackupEntry } from '../../types';
import { 
  API_URL, 
  BACKUP_INTERVALS,
  RETENTION_OPTIONS,
  SUCCESS_MESSAGES,
  ERROR_MESSAGES,
  FETCH_TIMEOUT 
} from '../../constants';
import { useMessage } from '../../hooks/useMessage';

type BackupTab = 'local' | 'cloud' | 'distributed';

export const LocalBackup: React.FC = () => {
  const [activeTab, setActiveTab] = useState<BackupTab>('local');
  const [isLoading, setIsLoading] = useState(false);
  
  const [config, setConfig] = useState<BackupConfig>({
    auto_backup: false,
    interval: 'daily',
    retention_days: 7,
    compression: true,
    encryption: false,
    destination: '/opt/database/backups',
    backup_type: 'full'
  });

  const [history, setHistory] = useState<BackupEntry[]>([]);
  const [selectedBackup] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const { message, showSuccess, showError, clearMessage } = useMessage();

  // Refs para cleanup
  const abortControllerRef = useRef<AbortController | null>(null);

  // Cleanup ao desmontar
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  // Carregar dados iniciais
  useEffect(() => {
    loadBackupData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Função auxiliar para fetch com timeout
  const fetchWithTimeout = useCallback(async (
    url: string,
    options: RequestInit = {},
    timeout: number = FETCH_TIMEOUT
  ): Promise<Response> => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();

    const timeoutId = setTimeout(() => {
      abortControllerRef.current?.abort();
    }, timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: abortControllerRef.current.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }, []);

  const loadBackupData = async () => {
    try {
      const [configResponse, historyResponse] = await Promise.all([
        fetchWithTimeout(`${API_URL}/backup/config`),
        fetchWithTimeout(`${API_URL}/backup/history`)
      ]);

      if (configResponse.ok) {
        const configData = await configResponse.json();
        setConfig(prev => ({ ...prev, ...configData }));
      }

      if (historyResponse.ok) {
        const historyData = await historyResponse.json();
        setHistory(historyData.backups || []);
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        console.error('Erro ao carregar dados de backup:', error);
      }
    }
  };

  const saveConfig = async () => {
    setIsLoading(true);
    clearMessage();

    try {
      const response = await fetchWithTimeout(`${API_URL}/backup/config`, {
        method: 'POST',
        body: JSON.stringify(config)
      });
      
      if (response.ok) {
        showSuccess('Configurações de backup salvas com sucesso!');
      } else {
        const error = await response.json().catch(() => ({ message: 'Falha ao salvar' }));
        showError(error.message || 'Falha ao salvar configurações');
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        showError(ERROR_MESSAGES.CONNECTION_ERROR);
      }
    }

    setIsLoading(false);
  };

  const executeBackup = async (type: 'full' | 'incremental' = 'full') => {
    setIsLoading(true);
    clearMessage();

    try {
      const response = await fetchWithTimeout(`${API_URL}/backup/execute`, {
        method: 'POST',
        body: JSON.stringify({
          type,
          config
        })
      }, 300000); // 5 minutos timeout para backup

      const data = await response.json();

      if (data.success) {
        showSuccess(data.message || SUCCESS_MESSAGES.BACKUP_CREATED);
        loadBackupData();
      } else {
        showError(data.message || 'Erro ao executar backup');
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        showError('Erro ao executar backup');
      }
    }

    setIsLoading(false);
  };

  const restoreBackup = async (backupId: string) => {
    if (!confirm('ATENÇÃO: Isso substituirá os dados atuais. Deseja continuar?')) {
      return;
    }

    setIsLoading(true);
    clearMessage();

    try {
      const response = await fetchWithTimeout(`${API_URL}/backup/restore`, {
        method: 'POST',
        body: JSON.stringify({ backup_id: backupId })
      }, 300000);

      const data = await response.json();

      if (data.success) {
        showSuccess(data.message || SUCCESS_MESSAGES.RESTORE_COMPLETED);
      } else {
        showError(data.message || 'Erro na restauração');
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        showError('Erro na restauração');
      }
    }

    setIsLoading(false);
  };

  const deleteBackup = async (backupId: string) => {
    if (!confirm('Deseja excluir este backup?')) return;

    try {
      const response = await fetchWithTimeout(`${API_URL}/backup/${backupId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setHistory(prev => prev.filter(b => b.id !== backupId));
        showSuccess('Backup excluído!');
      } else {
        showError('Erro ao excluir backup');
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        showError('Erro ao excluir backup');
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      showSuccess(`Arquivo selecionado: ${file.name}`);
    }
  };

  const uploadAndRestore = async () => {
    if (!selectedFile) {
      showError('Selecione um arquivo primeiro');
      return;
    }

    if (!confirm('ATENÇÃO: Isso substituirá os dados atuais. Deseja continuar?')) {
      return;
    }

    setIsLoading(true);
    clearMessage();

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${API_URL}/backup/upload-restore`, {
        method: 'POST',
        body: formData,
        signal: abortControllerRef.current?.signal,
      });

      const data = await response.json();

      if (data.success) {
        showSuccess(data.message || SUCCESS_MESSAGES.RESTORE_COMPLETED);
        setSelectedFile(null);
      } else {
        showError(data.message || 'Erro na restauração');
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        showError('Erro na restauração');
      }
    }

    setIsLoading(false);
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('pt-BR');
  };

  const formatSize = (size: string) => {
    return size;
  };

  // Renderiza a seção de info sobre backups
  const renderBackupInfo = () => (
    <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-5 mb-5">
      <h3 className="text-yellow-400 font-semibold mb-4 flex items-center gap-2 text-sm">
        <Lightbulb className="w-4 h-4" />
        O que são Backups?
      </h3>
      
      <div className="space-y-3">
        <div className="flex gap-3 text-sm text-gray-400">
          <span className="w-5 h-5 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center text-xs font-semibold flex-shrink-0">1</span>
          <span>Backup é uma <span className="text-cyan-400">cópia de segurança</span> dos seus dados - como tirar uma foto do sistema.</span>
        </div>
        <div className="flex gap-3 text-sm text-gray-400">
          <span className="w-5 h-5 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center text-xs font-semibold flex-shrink-0">2</span>
          <span>Se algo der errado (computador quebrar, vírus, etc.), você pode restaurar tudo usando essa cópia.</span>
        </div>
        <div className="flex gap-3 text-sm text-gray-400">
          <span className="w-5 h-5 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center text-xs font-semibold flex-shrink-0">3</span>
          <span><span className="text-yellow-400 font-semibold">BACKUP COMPLETO:</span> Copia TUDO. Leva mais tempo, mas é a forma mais segura.</span>
        </div>
        <div className="flex gap-3 text-sm text-gray-400">
          <span className="w-5 h-5 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center text-xs font-semibold flex-shrink-0">4</span>
          <span><span className="text-yellow-400 font-semibold">BACKUP INCREMENTAL:</span> Copia apenas o que mudou desde o último backup. É mais rápido!</span>
        </div>
      </div>

      {/* Dicas */}
      <div className="mt-4 space-y-2">
        <div className="flex items-center gap-2 text-yellow-200 text-xs bg-yellow-500/10 rounded-lg px-3 py-2">
          <Lightbulb className="w-3 h-3" />
          Faça backup completo toda semana
        </div>
        <div className="flex items-center gap-2 text-yellow-200 text-xs bg-yellow-500/10 rounded-lg px-3 py-2">
          <Lightbulb className="w-3 h-3" />
          Faça backup incremental todo dia
        </div>
        <div className="flex items-center gap-2 text-yellow-200 text-xs bg-yellow-500/10 rounded-lg px-3 py-2">
          <Lightbulb className="w-3 h-3" />
          Guarde cópias em lugares diferentes (pen drive, nuvem)
        </div>
      </div>

      {/* Alerta */}
      <div className="mt-3 flex items-start gap-2 text-red-300 text-xs bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
        <AlertTriangle className="w-3 h-3 flex-shrink-0 mt-0.5" />
        <span>Sem backup, se o computador quebrar, você perde TUDO! Não arrisque.</span>
      </div>
    </div>
  );

  const renderLocalTab = () => (
    <div className="space-y-5">
      {renderBackupInfo()}

      {/* Tabs Local/Nuvem/Distribuído */}
      <div className="flex gap-2">
        {[
          { id: 'local' as BackupTab, label: 'Local' },
          { id: 'cloud' as BackupTab, label: 'Nuvem' },
          { id: 'distributed' as BackupTab, label: 'Distribuído' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-gradient-to-r from-cyan-600 to-cyan-700 text-white'
                : 'bg-gray-800/50 text-gray-400 border border-gray-700 hover:border-cyan-500/30'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Botões de Backup */}
      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={() => executeBackup('full')}
          disabled={isLoading}
          className="flex items-center justify-center gap-2 py-3 px-4 bg-cyan-600/20 border border-cyan-500/40 rounded-lg text-cyan-400 text-sm font-medium hover:bg-cyan-600/30 transition-colors disabled:opacity-50"
        >
          {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
          Backup Completo
        </button>
        <button
          onClick={() => executeBackup('incremental')}
          disabled={isLoading}
          className="flex items-center justify-center gap-2 py-3 px-4 bg-gray-800/50 border border-gray-700 rounded-lg text-gray-400 text-sm font-medium hover:border-cyan-500/30 transition-colors disabled:opacity-50"
        >
          <Download className="w-4 h-4" />
          Incremental
        </button>
      </div>

      {/* Estado Vazio */}
      <div className="bg-gray-900/30 border border-gray-800 rounded-xl p-10 text-center">
        <p className="text-gray-500 text-sm">Nenhum backup encontrado</p>
      </div>

      {/* Agendamento */}
      <div className="flex items-center justify-between p-4 bg-gray-800/50 border border-gray-700 rounded-xl">
        <div className="flex items-center gap-3">
          <Database className="w-5 h-5 text-cyan-400" />
          <span className="text-white text-sm font-medium">Agendamento Automático</span>
        </div>
        <button
          onClick={() => setConfig(prev => ({ ...prev, auto_backup: !prev.auto_backup }))}
          className={`relative w-12 h-6 rounded-full transition-colors ${
            config.auto_backup ? 'bg-cyan-600' : 'bg-gray-700'
          }`}
        >
          <span
            className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
              config.auto_backup ? 'left-7' : 'left-1'
            }`}
          />
        </button>
      </div>
    </div>
  );

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-500 rounded-lg flex items-center justify-center">
            <Save className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Backup Local</h2>
            <p className="text-gray-400 text-sm">Criar e restaurar backups do banco de dados</p>
          </div>
        </div>
      </div>

      {/* Message */}
      {message && (
        <div className={`mb-4 p-4 rounded-lg flex items-center gap-3 ${
          message.type === 'success' 
            ? 'bg-green-500/20 border border-green-500/50' 
            : message.type === 'error'
            ? 'bg-red-500/20 border border-red-500/50'
            : 'bg-yellow-500/20 border border-yellow-500/50'
        }`}>
          {message.type === 'success' ? (
            <CheckCircle className="w-5 h-5 text-green-400" />
          ) : message.type === 'error' ? (
            <AlertTriangle className="w-5 h-5 text-red-400" />
          ) : (
            <AlertTriangle className="w-5 h-5 text-yellow-400" />
          )}
          <span className={message.type === 'success' ? 'text-green-200' : message.type === 'error' ? 'text-red-200' : 'text-yellow-200'}>
            {message.text}
          </span>
          <button onClick={clearMessage} className="ml-auto">
            <X className="w-4 h-4 text-gray-400 hover:text-white" />
          </button>
        </div>
      )}

      {/* Content */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        {renderLocalTab()}
      </div>
    </div>
  );
};

export default LocalBackup;
