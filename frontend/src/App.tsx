import React, { useState, Suspense, lazy, ErrorInfo } from 'react';
import { Database, HardDrive, Menu, X } from 'lucide-react';

// Lazy loading dos componentes para melhor performance
const DatabaseSettings = lazy(() => import('./components/settings/DatabaseSettings'));
const LocalBackup = lazy(() => import('./components/settings/LocalBackup'));

// Error Boundary Component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 text-center">
          <h2 className="text-xl font-bold text-red-600 mb-4">
            Algo deu errado
          </h2>
          <p className="text-gray-600 mb-4">
            {this.state.error?.message || 'Erro desconhecido'}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-cyan-600 text-white rounded hover:bg-cyan-700"
          >
            Recarregar página
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Loading fallback
const LoadingFallback = () => (
  <div className="flex items-center justify-center p-8">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-600"></div>
    <span className="ml-3 text-gray-600">Carregando...</span>
  </div>
);

// Tipos de seção disponíveis
type SectionType = 'settings' | 'backup' | 'monitoring' | 'logs';

// Configuração das seções
const SECTIONS = [
  { id: 'settings' as SectionType, label: 'Configurações', icon: Database },
  { id: 'backup' as SectionType, label: 'Backup Local', icon: HardDrive },
] as const;

function App() {
  const [activeSection, setActiveSection] = useState<SectionType>('settings');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const renderSection = () => {
    switch (activeSection) {
      case 'settings':
        return <DatabaseSettings />;
      case 'backup':
        return <LocalBackup />;
      default:
        return <DatabaseSettings />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-cyan-900">
      {/* Header */}
      <header className="bg-slate-900/80 backdrop-blur-sm border-b border-slate-700/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-cyan-600 
                            flex items-center justify-center shadow-lg shadow-cyan-500/20">
                <Database className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Database</h1>
                <p className="text-xs text-slate-400">v2.0.2 - Ubuntu Server LTS</p>
              </div>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-2">
              {SECTIONS.map((section) => {
                const Icon = section.icon;
                return (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                      activeSection === section.id
                        ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/20'
                        : 'text-slate-300 hover:text-white hover:bg-slate-800'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-sm font-medium">{section.label}</span>
                  </button>
                );
              })}
            </nav>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-slate-300 hover:text-white"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="md:hidden border-t border-slate-700/50 bg-slate-900/95">
            {SECTIONS.map((section) => {
              const Icon = section.icon;
              return (
                <button
                  key={section.id}
                  onClick={() => {
                    setActiveSection(section.id);
                    setMobileMenuOpen(false);
                  }}
                  className={`w-full flex items-center gap-3 px-4 py-3 transition-colors ${
                    activeSection === section.id
                      ? 'bg-cyan-600/20 text-cyan-400'
                      : 'text-slate-300 hover:bg-slate-800'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{section.label}</span>
                </button>
              );
            })}
          </nav>
        )}
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ErrorBoundary>
          <Suspense fallback={<LoadingFallback />}>
            {renderSection()}
          </Suspense>
        </ErrorBoundary>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-700/50 bg-slate-900/50 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-slate-400 text-sm">
              Database v2.0.2 - Otimizado para Ubuntu Server LTS
            </p>
            <div className="flex items-center gap-4 text-sm text-slate-500">
              <span>Backend: Python/FastAPI</span>
              <span>•</span>
              <span>Frontend: React/TypeScript</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
