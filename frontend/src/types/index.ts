/**
 * Database Types
 * =======================
 * Tipos TypeScript para o frontend
 */

export type EngineType = 'sqlite' | 'postgresql' | 'mariadb' | 'firebird';

export type TabType = 'motor' | 'config' | 'reparo' | 'migracao' | 'templates' | 'docs';

export interface DatabaseConfig {
  engine: EngineType;
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  file_path?: string;
  ssl_mode?: string;
  charset?: string;
}

export interface EngineInfo {
  id: EngineType;
  name: string;
  icon: string;
  port: number | null;
  description: string;
  when_to_use: string[];
  limitations: string[];
  features: string[];
  install_ubuntu: string;
  maintenance_tools: MaintenanceTool[];
}

export interface MaintenanceTool {
  id?: string;
  name: string;
  description: string;
  sql: string;
  warning?: string;
}

export interface ConnectionTestResult {
  success: boolean;
  message: string;
  details?: {
    version?: string;
    size_bytes?: number;
    size_mb?: number;
    path?: string;
  };
  timestamp: string;
}

export interface ConnectionHistoryEntry {
  id: string;
  timestamp: string;
  engine: string;
  host: string;
  database: string;
  status: string;
  message: string;
}

export interface DocLink {
  name: string;
  url: string;
}

export interface BackupConfig {
  auto_backup: boolean;
  interval: 'hourly' | 'daily' | 'weekly' | 'monthly';
  retention_days: number;
  compression: boolean;
  encryption: boolean;
  destination: string;
  backup_type: 'full' | 'incremental';
}

export interface BackupEntry {
  id: string;
  timestamp: string;
  engine: string;
  type: string;
  size: string;
  size_bytes?: number;
  status: string;
  path: string;
  checksum?: string;
}

export interface MigrationRequest {
  source_engine: EngineType;
  target_engine: EngineType;
  source_config: DatabaseConfig;
  target_config: DatabaseConfig;
  tables?: string[];
}

export interface MaintenanceResult {
  success: boolean;
  action: string;
  message: string;
  sql_executed?: string;
  duration_ms?: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}
