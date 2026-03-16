import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { 
  Database, 
  ArrowRightLeft, 
  BookOpen,
  Play,
  Check,
  ExternalLink,
  Download,
  Upload,
  AlertTriangle,
  Key,
  Save,
  Trash2,
  Loader2,
  Activity
} from 'lucide-react';
import type { 
  EngineType, 
  TabType, 
  DatabaseConfig, 
  EngineInfo, 
  ConnectionTestResult, 
  ConnectionHistoryEntry, 
  DocLink, 
  MaintenanceTool 
} from '../../types';
import { 
  API_URL, 
  TABS, 
  DEFAULT_CONFIGS,
  SUCCESS_MESSAGES,
  ERROR_MESSAGES,
  FETCH_TIMEOUT,
  VALIDATION_LIMITS
} from '../../constants';
import { useMessage } from '../../hooks/useMessage';

// Interfaces para dados da API
interface ApiEngine {
  id: EngineType;
  name: string;
  icon: string;
  port: number | null;
  description: string;
}

// Componente para ícone de check
const CheckIcon: React.FC = () => (
  <div className="absolute top-3 right-3 w-5 h-5 rounded-full bg-cyan-400 flex items-center justify-center">
    <Check className="w-3 h-3 text-black" />
  </div>
);

// Componente para empty state do histórico
const EmptyHistoryIcon: React.FC = () => (
  <div className="w-12 h-12 mx-auto mb-4 text-gray-600">
    <Activity viewBox="0 0 24 24" />
  </div>
);

// Sanitiza ID da ferramenta
const sanitizeToolId = (name: string): string => {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9_-]/g, '_')
    .replace(/_+/g, '_')
    .substring(0, 64);
};

export const DatabaseSettings: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('motor');
  const [selectedEngine, setSelectedEngine] = useState<EngineType>('postgresql');
  const [engineDetails, setEngineDetails] = useState<EngineInfo | null>(null);
  const [engines, setEngines] = useState<ApiEngine[]>([]);
  const [config, setConfig] = useState<DatabaseConfig>({
    engine: 'postgresql',
    host: 'localhost',
    port: 5432,
    database: 'my_database',
    username: 'postgres',
    password: '',
    file_path: '/var/lib/my_database/database.db',
    ssl_mode: 'prefer',
    charset: 'utf8mb4'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [testResult, setTestResult] = useState<ConnectionTestResult | null>(null);
  const [history, setHistory] = useState<ConnectionHistoryEntry[]>([]);
  const [docs, setDocs] = useState<DocLink[]>([]);
  const [showPassword, setShowPassword] = useState(false);
  const [migrationSource, setMigrationSource] = useState<EngineType>('sqlite');
  const [migrationTarget, setMigrationTarget] = useState<EngineType>('postgresql');
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  const { message, showSuccess, showError, showInfo, clearMessage } = useMessage();

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
    loadEngines();
    loadConfig();
    loadHistory();
  }, []);

  // Carregar detalhes do motor quando selecionado
  useEffect(() => {
    loadEngineDetails(selectedEngine);
    loadDocs(selectedEngine);
  }, [selectedEngine]);

  // Função auxiliar para fetch com timeout e abort
  const fetchWithTimeout = useCallback(async (
    url: string,
    options: RequestInit = {},
    timeout: number = FETCH_TIMEOUT
  ): Promise<Response> => {
    // Cancelar requisição anterior
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    const { signal } = abortControllerRef.current;

    const timeoutId = setTimeout(() => {
      abortControllerRef.current?.abort();
    }, timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal,
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

  const loadEngines = useCallback(async () => {
    try {
      const response = await fetchWithTimeout(`${API_URL}/engines`);
      if (response.ok) {
        const data = await response.json();
        setEngines(data.engines || []);
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        console.error('Erro ao carregar motores:', error);
      }
    }
  }, [fetchWithTimeout]);

  const loadConfig = useCallback(async () => {
    try {
      const response = await fetchWithTimeout(`${API_URL}/config`);
      if (response.ok) {
        const data = await response.json();
        setConfig(prev => {
          const newConfig = { ...prev, ...data };
          // Garantir que valores padrão existam
          if (data.engine && DEFAULT_CONFIGS[data.engine as EngineType]) {
            const defaults = DEFAULT_CONFIGS[data.engine as EngineType];
            return {
              ...defaults,
              ...newConfig,
              engine: data.engine,
            };
          }
          return newConfig;
        });
        if (data.engine) {
          setSelectedEngine(data.engine);
        }
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        console.error('Erro ao carregar configuração:', error);
      }
    }
  }, [fetchWithTimeout]);

  const loadEngineDetails = useCallback(async (engine: EngineType) => {
    try {
      const response = await fetchWithTimeout(`${API_URL}/engines/${engine}`);
      if (response.ok) {
        const data = await response.json();
        setEngineDetails(data);
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        console.error('Erro ao carregar detalhes do motor:', error);
      }
    }
  }, [fetchWithTimeout]);

  const loadHistory = useCallback(async () => {
    try {
      const response = await fetchWithTimeout(`${API_URL}/connection-history`);
      if (response.ok) {
        const data = await response.json();
        setHistory(data.history || []);
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        console.error('Erro ao carregar histórico:', error);
      }
    }
  }, [fetchWithTimeout]);

  const loadDocs = useCallback(async (engine: EngineType) => {
    try {
      const response = await fetchWithTimeout(`${API_URL}/docs/${engine}`);
      if (response.ok) {
        const data = await response.json();
        setDocs(data.docs || []);
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        console.error('Erro ao carregar documentação:', error);
      }
    }
  }, [fetchWithTimeout]);

  const validateConfig = useCallback((): boolean => {
    const errors: Record<string, string> = {};
    
    if (selectedEngine === 'sqlite') {
      if (!config.file_path?.trim()) {
        errors.file_path = 'Caminho do arquivo é obrigatório';
      } else if (config.file_path.length > VALIDATION_LIMITS.FILE_PATH_MAX_LENGTH) {
        errors.file_path = `Caminho muito longo (máx ${VALIDATION_LIMITS.FILE_PATH_MAX_LENGTH} caracteres)`;
      }
    } else {
      if (!config.host?.trim()) {
        errors.host = 'Host é obrigatório';
      } else if (config.host.length > VALIDATION_LIMITS.HOST_MAX_LENGTH) {
        errors.host = `Host muito longo (máx ${VALIDATION_LIMITS.HOST_MAX_LENGTH} caracteres)`;
      }
      
      if (!config.port || config.port < VALIDATION_LIMITS.PORT_MIN || config.port > VALIDATION_LIMITS.PORT_MAX) {
        errors.port = `Porta deve estar entre ${VALIDATION_LIMITS.PORT_MIN} e ${VALIDATION_LIMITS.PORT_MAX}`;
      }
      
      if (!config.database?.trim()) {
        errors.database = 'Nome do banco é obrigatório';
      } else if (config.database.length > VALIDATION_LIMITS.DATABASE_MAX_LENGTH) {
        errors.database = `Nome do banco muito longo (máx ${VALIDATION_LIMITS.DATABASE_MAX_LENGTH} caracteres)`;
      }
      
      if (!config.username?.trim()) {
        errors.username = 'Usuário é obrigatório';
      } else if (config.username.length > VALIDATION_LIMITS.USERNAME_MAX_LENGTH) {
        errors.username = `Nome de usuário muito longo (máx ${VALIDATION_LIMITS.USERNAME_MAX_LENGTH} caracteres)`;
      }
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  }, [config, selectedEngine]);

  const saveConfig = useCallback(async () => {
    if (!validateConfig()) {
      return;
    }
    
    setIsLoading(true);
    clearMessage();
    
    try {
      const response = await fetchWithTimeout(`${API_URL}/config`, {
        method: 'POST',
        body: JSON.stringify({ ...config, engine: selectedEngine })
      });
      
      if (response.ok) {
        showSuccess(SUCCESS_MESSAGES.CONFIG_SAVED);
      } else {
        const errorData = await response.json().catch(() => ({ message: 'Falha ao salvar' }));
        showError(errorData.message || 'Falha ao salvar configuração');
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        showError(ERROR_MESSAGES.CONNECTION_ERROR);
      }
    } finally {
      setIsLoading(false);
    }
  }, [config, selectedEngine, validateConfig, fetchWithTimeout, showSuccess, showError, clearMessage]);

  const testConnection = useCallback(async () => {
    if (!validateConfig()) {
      return;
    }
    
    setIsLoading(true);
    setTestResult(null);
    clearMessage();
    
    try {
      const response = await fetchWithTimeout(`${API_URL}/test-connection`, {
        method: 'POST',
        body: JSON.stringify({ ...config, engine: selectedEngine })
      });
      
      const data = await response.json();
      setTestResult(data);
      
      if (data.success) {
        showSuccess(SUCCESS_MESSAGES.TEST_SUCCESS);
      } else if (data.message) {
        showError(data.message);
      }
      
      loadHistory();
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        showError(ERROR_MESSAGES.CONNECTION_ERROR);
        setTestResult({
          success: false,
          message: ERROR_MESSAGES.CONNECTION_ERROR,
          timestamp: new Date().toISOString()
        });
      }
    } finally {
      setIsLoading(false);
    }
  }, [config, selectedEngine, validateConfig, fetchWithTimeout, showSuccess, showError, clearMessage, loadHistory]);

  const clearHistory = useCallback(async () => {
    if (!confirm('Tem certeza que deseja limpar todo o histórico?')) {
      return;
    }
    
    try {
      const response = await fetchWithTimeout(`${API_URL}/connection-history`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        setHistory([]);
        showSuccess(SUCCESS_MESSAGES.HISTORY_CLEARED);
      } else {
        showError('Erro ao limpar histórico');
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        showError('Erro ao limpar histórico');
      }
    }
  }, [fetchWithTimeout, showSuccess, showError]);

  const executeMaintenance = useCallback(async (tool: MaintenanceTool) => {
    setIsLoading(true);
    clearMessage();
    
    try {
      const actionName = tool.id || sanitizeToolId(tool.name);
      const response = await fetchWithTimeout(`${API_URL}/maintenance/${actionName}`, {
        method: 'POST',
        body: JSON.stringify({ ...config, engine: selectedEngine })
      });
      
      const data = await response.json();
      
      if (data.success) {
        showSuccess(data.message);
      } else {
        showError(data.message || 'Erro ao executar manutenção');
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        showError('Erro ao executar manutenção');
      }
    } finally {
      setIsLoading(false);
    }
  }, [config, selectedEngine, fetchWithTimeout, showSuccess, showError, clearMessage]);

  const exportData = useCallback(async () => {
    setIsLoading(true);
    clearMessage();
    
    try {
      const response = await fetchWithTimeout(`${API_URL}/migration/export?format=sql`, {
        method: 'POST',
        body: JSON.stringify({ ...config, engine: selectedEngine })
      });
      
      const data = await response.json();
      
      if (data.success) {
        showSuccess(data.message);
      } else {
        showError(data.message || 'Erro ao exportar');
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        showError('Erro ao exportar dados');
      }
    } finally {
      setIsLoading(false);
    }
  }, [config, selectedEngine, fetchWithTimeout, showSuccess, showError, clearMessage]);

  const executeMigration = useCallback(async () => {
    if (migrationSource === migrationTarget) {
      showError('Motor de origem e destino devem ser diferentes!');
      return;
    }
    
    setIsLoading(true);
    clearMessage();
    
    // Configurações separadas para source e target
    const sourceConfig = DEFAULT_CONFIGS[migrationSource];
    const targetConfig = DEFAULT_CONFIGS[migrationTarget];
    
    try {
      const response = await fetchWithTimeout(`${API_URL}/migration/execute`, {
        method: 'POST',
        body: JSON.stringify({
          source_engine: migrationSource,
          target_engine: migrationTarget,
          source_config: { ...sourceConfig, engine: migrationSource },
          target_config: { ...targetConfig, engine: migrationTarget }
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        showSuccess(data.message);
      } else {
        showError(data.message || 'Erro na migração');
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        showError('Erro na migração');
      }
    } finally {
      setIsLoading(false);
    }
  }, [migrationSource, migrationTarget, fetchWithTimeout, showSuccess, showError, clearMessage]);

  const applyTemplate = useCallback((engine: EngineType) => {
    const defaultConfig = DEFAULT_CONFIGS[engine];
    if (!defaultConfig) {
      showError(`Template não encontrado para ${engine}`);
      return;
    }
    setConfig(prev => ({
      ...prev,
      engine,
      ...defaultConfig,
    }));
    setSelectedEngine(engine);
    setFormErrors({});
    showSuccess(`Template ${engine} aplicado!`);
  }, [showSuccess, showError]);

  // Memoizar engines disponíveis para templates
  const availableEngines = useMemo(() => 
    engines.filter(e => DEFAULT_CONFIGS[e.id]),
    [engines]
  );

  // Renderizar Tab Motor - memoizado
  const renderMotorTab = useCallback(() => (
    <div className="space-y-6">
      {/* Grid de Motores */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {engines.map((engine) => (
          <button
            key={engine.id}
            onClick={() => {
              setSelectedEngine(engine.id);
              setConfig(prev => ({ 
                ...prev, 
                engine: engine.id,
                port: engine.port ?? prev.port 
              }));
              setFormErrors({});
              setTestResult(null);
            }}
            className={`relative p-5 rounded-xl border-2 text-left transition-all duration-200 ${
              selectedEngine === engine.id
                ? 'border-cyan-400 bg-cyan-500/10'
                : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
            }`}
          >
            {selectedEngine === engine.id && <CheckIcon />}
            <div className="flex items-start gap-4">
              <span className="text-3xl">{engine.icon}</span>
              <div>
                <h3 className="text-lg font-semibold text-white">{engine.name}</h3>
                {engine.port && (
                  <p className="text-sm text-gray-400">Porta: {engine.port}</p>
                )}
                <p className="text-sm text-gray-500 mt-2">{engine.description}</p>
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* Detalhes do Motor Selecionado */}
      {engineDetails && (
        <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-cyan-400 mb-4 flex items-center gap-2">
            <span>{engineDetails.icon}</span>
            {engineDetails.name} - Detalhes
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Quando Usar */}
            <div>
              <h4 className="text-green-400 font-medium mb-2 flex items-center gap-2">
                <Check className="w-4 h-4" />
                Quando usar:
              </h4>
              <ul className="space-y-1">
                {engineDetails.when_to_use?.map((item, i) => (
                  <li key={i} className="text-gray-400 text-sm flex items-start gap-2">
                    <span className="text-cyan-400 mt-1">•</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* Limitações */}
            <div>
              <h4 className="text-yellow-400 font-medium mb-2 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                Limitações:
              </h4>
              <ul className="space-y-1">
                {engineDetails.limitations?.map((item, i) => (
                  <li key={i} className="text-gray-400 text-sm flex items-start gap-2">
                    <span className="text-yellow-400 mt-1">•</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Recursos */}
          {engineDetails.features && (
            <div className="mt-6">
              <h4 className="text-cyan-400 font-medium mb-3 flex items-center gap-2">
                <Key className="w-4 h-4" />
                Recursos:
              </h4>
              <div className="flex flex-wrap gap-2">
                {engineDetails.features.map((feature, i) => (
                  <span 
                    key={i}
                    className="px-3 py-1 bg-cyan-500/20 border border-cyan-500/40 rounded-full text-cyan-300 text-sm"
                  >
                    {feature}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  ), [engines, selectedEngine, engineDetails]);

  // Renderizar Tab Config - memoizado
  const renderConfigTab = useCallback(() => (
    <div className="space-y-5">
      {selectedEngine === 'sqlite' ? (
        // Configuração SQLite
        <div>
          <label className="block text-yellow-400 text-sm font-medium mb-2">
            Caminho do Arquivo
          </label>
          <input
            type="text"
            value={config.file_path || ''}
            onChange={(e) => {
              setConfig({ ...config, file_path: e.target.value });
              setFormErrors(prev => ({ ...prev, file_path: '' }));
            }}
            className={`w-full bg-gray-800 border rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:border-cyan-400 focus:outline-none transition-colors ${
              formErrors.file_path ? 'border-red-500' : 'border-gray-600'
            }`}
            placeholder="/var/lib/my_database/database.db"
          />
          {formErrors.file_path && (
            <p className="text-red-400 text-xs mt-1">{formErrors.file_path}</p>
          )}
        </div>
      ) : (
        // Configuração de servidores (PostgreSQL, MariaDB, Firebird)
        <>
          <div>
            <label className="block text-yellow-400 text-sm font-medium mb-2">Host</label>
            <input
              type="text"
              value={config.host}
              onChange={(e) => {
                setConfig({ ...config, host: e.target.value });
                setFormErrors(prev => ({ ...prev, host: '' }));
              }}
              className={`w-full bg-gray-800 border rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:border-cyan-400 focus:outline-none transition-colors ${
                formErrors.host ? 'border-red-500' : 'border-gray-600'
              }`}
              placeholder="localhost"
            />
            {formErrors.host && (
              <p className="text-red-400 text-xs mt-1">{formErrors.host}</p>
            )}
          </div>

          <div>
            <label className="block text-yellow-400 text-sm font-medium mb-2">Porta</label>
            <input
              type="number"
              value={config.port}
              onChange={(e) => {
                const value = parseInt(e.target.value) || 0;
                setConfig({ ...config, port: value });
                setFormErrors(prev => ({ ...prev, port: '' }));
              }}
              min={VALIDATION_LIMITS.PORT_MIN}
              max={VALIDATION_LIMITS.PORT_MAX}
              className={`w-full bg-gray-800 border rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:border-cyan-400 focus:outline-none transition-colors ${
                formErrors.port ? 'border-red-500' : 'border-gray-600'
              }`}
            />
            {formErrors.port && (
              <p className="text-red-400 text-xs mt-1">{formErrors.port}</p>
            )}
          </div>

          <div>
            <label className="block text-yellow-400 text-sm font-medium mb-2">Banco de Dados</label>
            <input
              type="text"
              value={config.database}
              onChange={(e) => {
                setConfig({ ...config, database: e.target.value });
                setFormErrors(prev => ({ ...prev, database: '' }));
              }}
              className={`w-full bg-gray-800 border rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:border-cyan-400 focus:outline-none transition-colors ${
                formErrors.database ? 'border-red-500' : 'border-gray-600'
              }`}
              placeholder="my_database"
            />
            {formErrors.database && (
              <p className="text-red-400 text-xs mt-1">{formErrors.database}</p>
            )}
          </div>

          <div>
            <label className="block text-yellow-400 text-sm font-medium mb-2">Usuário</label>
            <input
              type="text"
              value={config.username}
              onChange={(e) => {
                setConfig({ ...config, username: e.target.value });
                setFormErrors(prev => ({ ...prev, username: '' }));
              }}
              className={`w-full bg-gray-800 border rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:border-cyan-400 focus:outline-none transition-colors ${
                formErrors.username ? 'border-red-500' : 'border-gray-600'
              }`}
              placeholder={selectedEngine === 'postgresql' ? 'postgres' : 'root'}
            />
            {formErrors.username && (
              <p className="text-red-400 text-xs mt-1">{formErrors.username}</p>
            )}
          </div>

          <div>
            <label className="block text-yellow-400 text-sm font-medium mb-2">Senha</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={config.password}
                onChange={(e) => setConfig({ ...config, password: e.target.value })}
                className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:border-cyan-400 focus:outline-none transition-colors pr-12"
                placeholder="••••••••"
              />
              <button
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-cyan-400 transition-colors"
                type="button"
                aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
              >
                <Key className="w-5 h-5" />
              </button>
            </div>
          </div>
        </>
      )}

      {/* Mensagem de sucesso/erro */}
      {message && (
        <div className={`p-3 rounded-lg text-sm ${
          message.type === 'error'
            ? 'bg-red-500/10 border border-red-500/30 text-red-400'
            : 'bg-green-500/10 border border-green-500/30 text-green-400'
        }`}>
          {message.text}
        </div>
      )}

      {/* Botões de ação */}
      <div className="flex gap-3">
        <button
          onClick={saveConfig}
          disabled={isLoading}
          className="flex-1 bg-gray-700 hover:bg-gray-600 text-white font-semibold py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
        >
          {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5" />}
          Salvar Configuração
        </button>
        <button
          onClick={testConnection}
          disabled={isLoading}
          className="flex-1 bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Play className="w-5 h-5" />
          )}
          Testar Conexão
        </button>
      </div>

      {/* Alerta Modo Demo */}
      <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
        <p className="text-yellow-200 text-sm">
          Modo Demo: Conexão será simulada
        </p>
      </div>

      {/* Resultado do Teste */}
      {testResult && (
        <div className={`p-4 rounded-lg ${
          testResult.success 
            ? 'bg-green-500/10 border border-green-500/30' 
            : 'bg-red-500/10 border border-red-500/30'
        }`}>
          <p className={testResult.success ? 'text-green-400' : 'text-red-400'}>
            {testResult.message}
          </p>
          {testResult.details && (
            <div className="mt-2 text-sm text-gray-400">
              {testResult.details.version && <p>Versão: {testResult.details.version}</p>}
              {testResult.details.size_mb && <p>Tamanho: {testResult.details.size_mb} MB</p>}
              {testResult.details.path && <p>Caminho: {testResult.details.path}</p>}
            </div>
          )}
        </div>
      )}
    </div>
  ), [config, selectedEngine, formErrors, message, isLoading, testResult, showPassword, saveConfig, testConnection]);

  // Renderizar Tab Reparo - memoizado
  const renderReparoTab = useCallback(() => (
    <div className="space-y-6">
      <p className="text-gray-400">
        Ferramentas de manutenção e reparo para {engines.find(e => e.id === selectedEngine)?.name}
      </p>

      {engineDetails?.maintenance_tools && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {engineDetails.maintenance_tools.map((tool, index) => (
            <div key={index} className="bg-gray-800/50 border border-gray-700 rounded-xl p-4">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h4 className="text-yellow-400 font-semibold">{tool.name}</h4>
                  <p className="text-gray-400 text-sm mt-1">{tool.description}</p>
                </div>
                <button
                  onClick={() => executeMaintenance(tool)}
                  disabled={isLoading}
                  className="w-10 h-10 bg-gray-700 hover:bg-cyan-600 rounded-lg flex items-center justify-center transition-colors disabled:opacity-50"
                  aria-label={`Executar ${tool.name}`}
                >
                  {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5" />}
                </button>
              </div>
              <code className="block bg-black/50 rounded px-3 py-2 text-cyan-400 text-sm font-mono overflow-x-auto">
                {tool.sql}
              </code>
            </div>
          ))}
        </div>
      )}

      {/* Histórico */}
      <div className="bg-gray-800/30 border border-gray-700 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-white font-semibold">Histórico de Conexões</h4>
          {history.length > 0 && (
            <button
              onClick={clearHistory}
              className="text-red-400 hover:text-red-300 text-sm flex items-center gap-1"
            >
              <Trash2 className="w-4 h-4" />
              Limpar
            </button>
          )}
        </div>
        
        {history.length === 0 ? (
          <div className="text-center py-8">
            <EmptyHistoryIcon />
            <p className="text-gray-400">Nenhum histórico de conexão disponível</p>
            <p className="text-gray-500 text-sm mt-1">Execute um teste de conexão para começar</p>
          </div>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {history.slice(0, 10).map((entry) => (
              <div
                key={entry.id}
                className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg"
              >
                <div>
                  <p className="text-white text-sm">{new Date(entry.timestamp).toLocaleString()}</p>
                  <p className="text-gray-500 text-xs">{entry.engine} • {entry.database}</p>
                </div>
                <span className={`text-xs px-2 py-1 rounded ${
                  entry.status === 'success' 
                    ? 'bg-green-500/20 text-green-400' 
                    : 'bg-red-500/20 text-red-400'
                }`}>
                  {entry.status === 'success' ? '✓ OK' : '✗ Erro'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  ), [engines, selectedEngine, engineDetails, history, isLoading, executeMaintenance, clearHistory]);

  // Renderizar Tab Migração - memoizado
  const renderMigracaoTab = useCallback(() => (
    <div className="space-y-6">
      <p className="text-gray-400">
        Exporte e importe dados entre diferentes motores de banco
      </p>

      {/* Botões Exportar/Importar */}
      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={exportData}
          disabled={isLoading}
          className="p-6 bg-gray-800/50 border border-gray-700 hover:border-cyan-500/50 rounded-xl text-center transition-colors disabled:opacity-50"
        >
          <Download className="w-8 h-8 mx-auto mb-3 text-cyan-400" />
          <h4 className="text-white font-semibold">Exportar Dados</h4>
          <p className="text-gray-500 text-sm mt-1">JSON/SQL</p>
        </button>

        <button 
          onClick={() => showInfo('Funcionalidade em desenvolvimento')}
          className="p-6 bg-gray-800/50 border border-gray-700 hover:border-cyan-500/50 rounded-xl text-center transition-colors"
        >
          <Upload className="w-8 h-8 mx-auto mb-3 text-cyan-400" />
          <h4 className="text-white font-semibold">Importar Dados</h4>
          <p className="text-gray-500 text-sm mt-1">De outro banco</p>
        </button>
      </div>

      {/* Migração Assistida */}
      <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
        <h4 className="text-yellow-400 font-semibold mb-2">Migração Assistida</h4>
        <p className="text-gray-400 text-sm mb-4">
          Transfira dados automaticamente de um motor para outro mantendo integridade referencial.
        </p>

        <div className="flex items-center gap-4 mb-4">
          <select
            value={migrationSource}
            onChange={(e) => setMigrationSource(e.target.value as EngineType)}
            className="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 text-white focus:border-cyan-400 focus:outline-none"
          >
            {engines.map(e => (
              <option key={e.id} value={e.id}>{e.name}</option>
            ))}
          </select>
          
          <ArrowRightLeft className="w-6 h-6 text-gray-500" />
          
          <select
            value={migrationTarget}
            onChange={(e) => setMigrationTarget(e.target.value as EngineType)}
            className="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 text-white focus:border-cyan-400 focus:outline-none"
          >
            {engines.map(e => (
              <option key={e.id} value={e.id}>{e.name}</option>
            ))}
          </select>
        </div>

        <button
          onClick={executeMigration}
          disabled={isLoading}
          className="w-full bg-gray-700 hover:bg-cyan-600 text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:opacity-50"
        >
          {isLoading ? <Loader2 className="w-5 h-5 animate-spin inline mr-2" /> : null}
          Iniciar Migração
        </button>
      </div>
    </div>
  ), [engines, migrationSource, migrationTarget, isLoading, exportData, executeMigration, showInfo]);

  // Renderizar Tab Templates - memoizado
  const renderTemplatesTab = useCallback(() => (
    <div className="space-y-6">
      <p className="text-gray-400">Templates de configuração pré-definidos</p>
      
      <div className="grid grid-cols-1 gap-4">
        {availableEngines.map((engine) => {
          const defaultConfig = DEFAULT_CONFIGS[engine.id];
          
          return (
            <div key={engine.id} className="bg-gray-800/50 border border-gray-700 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{engine.icon || '🔧'}</span>
                  <div>
                    <h4 className="text-white font-semibold">{engine.name}</h4>
                    <p className="text-gray-500 text-sm">
                      {engine.id === 'sqlite' 
                        ? defaultConfig.file_path 
                        : `${defaultConfig.host}:${defaultConfig.port} / ${defaultConfig.database}`}
                    </p>
                  </div>
                </div>
                <button 
                  onClick={() => applyTemplate(engine.id)}
                  className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-sm transition-colors"
                >
                  Aplicar
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  ), [availableEngines, applyTemplate]);

  // Renderizar Tab Docs - memoizado
  const renderDocsTab = useCallback(() => (
    <div className="space-y-6">
      <p className="text-gray-400">
        Documentação oficial e recursos para {engines.find(e => e.id === selectedEngine)?.name}
      </p>

      {/* Links de Documentação */}
      <div className="space-y-3">
        {docs.map((doc, index) => (
          <a
            key={index}
            href={doc.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-between p-4 bg-gray-800/50 border border-gray-700 hover:border-cyan-500/50 rounded-xl transition-colors group"
          >
            <div className="flex items-center gap-3">
              <BookOpen className="w-5 h-5 text-cyan-400" />
              <span className="text-white group-hover:text-cyan-400 transition-colors">{doc.name}</span>
            </div>
            <ExternalLink className="w-5 h-5 text-gray-500 group-hover:text-cyan-400 transition-colors" />
          </a>
        ))}
      </div>

      {/* Dicas de Instalação */}
      {engineDetails?.install_ubuntu && (
        <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
          <h4 className="text-yellow-400 font-semibold mb-3">💡 Dicas de Instalação</h4>
          <code className="block bg-black/50 rounded-lg px-4 py-3 text-cyan-400 text-sm font-mono whitespace-pre-wrap">
            {engineDetails.install_ubuntu}
          </code>
        </div>
      )}
    </div>
  ), [engines, selectedEngine, docs, engineDetails]);

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-500 rounded-lg flex items-center justify-center">
            <Database className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Banco de Dados Avançado</h2>
            <p className="text-gray-400 text-sm">Configure o motor e conexão do banco de dados</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 mb-6">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Content */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        {activeTab === 'motor' && renderMotorTab()}
        {activeTab === 'config' && renderConfigTab()}
        {activeTab === 'reparo' && renderReparoTab()}
        {activeTab === 'migracao' && renderMigracaoTab()}
        {activeTab === 'templates' && renderTemplatesTab()}
        {activeTab === 'docs' && renderDocsTab()}
      </div>
    </div>
  );
};

export default DatabaseSettings;
