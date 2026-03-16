/**
 * Frontend Constants
 * ==================
 * Constantes centralizadas para o frontend
 */

import type { EngineType, TabType } from '../types';
import {
  Database,
  Settings,
  Wrench,
  ArrowRightLeft,
  FileText,
  BookOpen,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

// URL da API
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Configurações de timeout
export const FETCH_TIMEOUT = 10000; // 10 segundos
export const MESSAGE_TIMEOUT = 3000; // 3 segundos

// Tabs disponíveis
export interface TabConfig {
  id: TabType;
  label: string;
  icon: LucideIcon;
}

export const TABS: TabConfig[] = [
  { id: 'motor', label: 'Motor', icon: Database },
  { id: 'config', label: 'Config', icon: Settings },
  { id: 'reparo', label: 'Reparo', icon: Wrench },
  { id: 'migracao', label: 'Migração', icon: ArrowRightLeft },
  { id: 'templates', label: 'Templates', icon: FileText },
  { id: 'docs', label: 'Docs', icon: BookOpen },
];

// Configurações padrão por motor
export const DEFAULT_CONFIGS: Record<EngineType, {
  host: string;
  port: number;
  database: string;
  username: string;
  ssl_mode?: string;
  charset?: string;
  file_path?: string;
}> = {
  postgresql: {
    host: 'localhost',
    port: 5432,
    database: 'my_database',
    username: 'postgres',
    ssl_mode: 'prefer',
    charset: 'utf8mb4',
  },
  sqlite: {
    host: 'localhost',
    port: 0,
    database: 'database',
    username: '',
    file_path: '/var/lib/myapp/database.db',
  },
  mariadb: {
    host: 'localhost',
    port: 3306,
    database: 'my_database',
    username: 'root',
    charset: 'utf8mb4',
  },
  firebird: {
    host: 'localhost',
    port: 3050,
    database: 'database.fdb',
    username: 'SYSDBA',
  },
};

// Portas padrão por motor
export const DEFAULT_PORTS: Record<EngineType, number | null> = {
  sqlite: null,
  postgresql: 5432,
  mariadb: 3306,
  firebird: 3050,
};

// Limites de validação
export const VALIDATION_LIMITS = {
  PORT_MIN: 1,
  PORT_MAX: 65535,
  HOST_MAX_LENGTH: 253,
  DATABASE_MAX_LENGTH: 64,
  USERNAME_MAX_LENGTH: 32,
  PASSWORD_MAX_LENGTH: 128,
  FILE_PATH_MAX_LENGTH: 4096,
};

// Chaves de storage local
export const STORAGE_KEYS = {
  CONFIG: 'database_config',
  HISTORY: 'connection_history',
  THEME: 'theme',
};

// Intervalos de backup
export const BACKUP_INTERVALS = [
  { value: 'hourly', label: 'A cada hora' },
  { value: 'daily', label: 'Diário' },
  { value: 'weekly', label: 'Semanal' },
  { value: 'monthly', label: 'Mensal' },
] as const;

// Retenção em dias
export const RETENTION_OPTIONS = [
  { value: 3, label: '3 dias' },
  { value: 7, label: '7 dias' },
  { value: 14, label: '14 dias' },
  { value: 30, label: '30 dias' },
  { value: 90, label: '90 dias' },
] as const;

// Mensagens de erro comuns
export const ERROR_MESSAGES = {
  CONNECTION_ERROR: 'Erro ao conectar com o servidor',
  VALIDATION_ERROR: 'Dados inválidos',
  NOT_FOUND: 'Recurso não encontrado',
  SERVER_ERROR: 'Erro interno do servidor',
  TIMEOUT_ERROR: 'Tempo de conexão esgotado',
  UNKNOWN_ERROR: 'Erro desconhecido',
};

// Mensagens de sucesso
export const SUCCESS_MESSAGES = {
  CONFIG_SAVED: 'Configuração salva com sucesso!',
  BACKUP_CREATED: 'Backup criado com sucesso!',
  RESTORE_COMPLETED: 'Restauração concluída!',
  HISTORY_CLEARED: 'Histórico limpo com sucesso!',
  TEST_SUCCESS: 'Conexão estabelecida com sucesso!',
};
