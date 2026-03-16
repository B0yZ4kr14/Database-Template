"""
Engine Data
===========
Dados dos motores de banco de dados
"""

from app.core.constants import EngineType
from app.models import EngineDetails, EngineInfo, MaintenanceTool, DocLink


# Documentação por motor
DOCS = {
    EngineType.SQLITE: [
        DocLink(
            name="SQLite Documentation",
            url="https://www.sqlite.org/docs.html",
            description="Documentação oficial do SQLite"
        ),
        DocLink(
            name="SQLite FAQ",
            url="https://www.sqlite.org/faq.html",
            description="Perguntas frequentes"
        ),
        DocLink(
            name="SQLite Query Language",
            url="https://www.sqlite.org/lang.html",
            description="Referência da linguagem SQL"
        ),
    ],
    EngineType.POSTGRESQL: [
        DocLink(
            name="PostgreSQL Docs",
            url="https://www.postgresql.org/docs/",
            description="Documentação oficial do PostgreSQL"
        ),
        DocLink(
            name="Tutorial Iniciante",
            url="https://www.postgresql.org/docs/current/tutorial.html",
            description="Tutorial para iniciantes"
        ),
        DocLink(
            name="PostgreSQL Wiki",
            url="https://wiki.postgresql.org/",
            description="Wiki da comunidade"
        ),
    ],
    EngineType.MARIADB: [
        DocLink(
            name="MariaDB Documentation",
            url="https://mariadb.com/kb/en/documentation/",
            description="Documentação oficial do MariaDB"
        ),
        DocLink(
            name="MariaDB Tutorial",
            url="https://mariadb.com/kb/en/getting-started/",
            description="Tutorial para iniciantes"
        ),
        DocLink(
            name="MariaDB Wiki",
            url="https://mariadb.com/kb/en/mariadb-wiki/",
            description="Wiki da comunidade"
        ),
    ],
    EngineType.FIREBIRD: [
        DocLink(
            name="Firebird Documentation",
            url="https://firebirdsql.org/en/documentation/",
            description="Documentação oficial do Firebird"
        ),
        DocLink(
            name="Firebird FAQ",
            url="https://firebirdsql.org/en/faq/",
            description="Perguntas frequentes"
        ),
        DocLink(
            name="Firebird Wiki",
            url="https://wiki.firebirdsql.org/",
            description="Wiki da comunidade"
        ),
    ],
}

# Detalhes completos dos motores
ENGINE_DETAILS = {
    EngineType.SQLITE: EngineDetails(
        id=EngineType.SQLITE,
        name="SQLite",
        icon="🗃️",
        port=None,
        description="Banco de dados leve em arquivo único, ideal para instalações single-node",
        when_to_use=[
            "Instalações single-node (1 terminal)",
            "Ambientes offline sem rede",
            "Backup fácil (apenas copiar arquivo)",
            "Desenvolvimento e testes"
        ],
        limitations=[
            "Limite de conexões simultâneas",
            "Não recomendado para múltiplos clientes",
            "Sem replicação nativa"
        ],
        features=[
            "Zero configuração",
            "Arquivo único portátil",
            "Sem servidor externo",
            "Transações ACID",
            "Full-text search"
        ],
        install_ubuntu="SQLite já vem embutido no Python - não requer instalação adicional.",
        install_arch="SQLite já vem embutido - não requer instalação adicional.",
        maintenance_tools=[
            MaintenanceTool(
                id="vacuum",
                name="VACUUM",
                description="Compacta o banco e recupera espaço",
                sql="VACUUM;"
            ),
            MaintenanceTool(
                id="integrity_check",
                name="Integrity Check",
                description="Verifica integridade dos dados",
                sql="PRAGMA integrity_check;"
            ),
            MaintenanceTool(
                id="reindex",
                name="Reindex",
                description="Reconstrói todos os índices",
                sql="REINDEX;"
            ),
            MaintenanceTool(
                id="analyze",
                name="Analyze",
                description="Atualiza estatísticas das tabelas",
                sql="ANALYZE;"
            ),
        ],
        docs=DOCS[EngineType.SQLITE]
    ),
    EngineType.POSTGRESQL: EngineDetails(
        id=EngineType.POSTGRESQL,
        name="PostgreSQL",
        icon="🐘",
        port=5432,
        description="Banco de dados robusto e escalável para ambientes corporativos",
        when_to_use=[
            "Múltiplos terminais (rede)",
            "Ambientes corporativos",
            "Alta disponibilidade (replicação)",
            "Integração com outras aplicações"
        ],
        limitations=[
            "Requer instalação separada",
            "Mais complexo de administrar",
            "Consumo maior de recursos"
        ],
        features=[
            "JSON/JSONB nativo",
            "Full-text search avançado",
            "Replicação síncrona/assíncrona",
            "Extensões (PostGIS, etc)",
            "MVCC robusto"
        ],
        install_ubuntu="sudo apt update && sudo apt install postgresql postgresql-contrib",
        install_arch="sudo pacman -S postgresql",
        maintenance_tools=[
            MaintenanceTool(
                id="vacuum_full",
                name="VACUUM FULL",
                description="Compacta e recupera espaço",
                sql="VACUUM FULL;",
                warning="Bloqueia tabelas durante a execução"
            ),
            MaintenanceTool(
                id="analyze",
                name="ANALYZE",
                description="Atualiza estatísticas",
                sql="ANALYZE;"
            ),
            MaintenanceTool(
                id="reindex_database",
                name="REINDEX DATABASE",
                description="Reconstrói índices",
                sql="REINDEX DATABASE {database};"
            ),
            MaintenanceTool(
                id="pg_checksums",
                name="pg_checksums",
                description="Verifica checksums das páginas",
                sql="pg_checksums --check"
            ),
        ],
        docs=DOCS[EngineType.POSTGRESQL]
    ),
    EngineType.MARIADB: EngineDetails(
        id=EngineType.MARIADB,
        name="MariaDB",
        icon="🐬",
        port=3306,
        description="Fork do MySQL com melhor performance e compatibilidade",
        when_to_use=[
            "Ambientes com múltiplos sistemas",
            "Migração de sistemas MySQL existentes",
            "Compatibilidade com scripts MySQL",
            "Alto volume de leituras"
        ],
        limitations=[
            "Algumas funções PostgreSQL não disponíveis",
            "Menor comunidade que PostgreSQL",
            "JSON menos robusto"
        ],
        features=[
            "Compatível com MySQL",
            "Storage engines diversos",
            "Galera Cluster nativo",
            "Thread pool",
            "Aria engine"
        ],
        install_ubuntu="sudo apt update && sudo apt install mariadb-server mariadb-client",
        install_arch="sudo pacman -S mariadb",
        maintenance_tools=[
            MaintenanceTool(
                id="optimize_table",
                name="OPTIMIZE TABLE",
                description="Otimiza tabelas",
                sql="OPTIMIZE TABLE {table};"
            ),
            MaintenanceTool(
                id="analyze_table",
                name="ANALYZE TABLE",
                description="Atualiza estatísticas",
                sql="ANALYZE TABLE {table};"
            ),
            MaintenanceTool(
                id="check_table",
                name="CHECK TABLE",
                description="Verifica integridade",
                sql="CHECK TABLE {table};"
            ),
            MaintenanceTool(
                id="repair_table",
                name="REPAIR TABLE",
                description="Repara tabelas corrompidas",
                sql="REPAIR TABLE {table};"
            ),
        ],
        docs=DOCS[EngineType.MARIADB]
    ),
    EngineType.FIREBIRD: EngineDetails(
        id=EngineType.FIREBIRD,
        name="Firebird",
        icon="🔥",
        port=3050,
        description="Banco de dados legado multiplataforma com modo embedded",
        when_to_use=[
            "Aplicações legadas",
            "Modo embedded necessário",
            "Baixo consumo de recursos",
            "Deploy simplificado"
        ],
        limitations=[
            "Comunidade menor",
            "Menos recursos modernos",
            "Documentação limitada"
        ],
        features=[
            "Embedded mode",
            "Multiplataforma",
            "Baixo footprint",
            "Transações ACID",
            "Triggers e stored procedures"
        ],
        install_ubuntu="sudo apt update && sudo apt install firebird3.0-server",
        install_arch="sudo pacman -S firebird",
        maintenance_tools=[
            MaintenanceTool(
                id="gfix_v",
                name="gfix -v",
                description="Verifica integridade",
                sql="gfix -v -full {database}"
            ),
            MaintenanceTool(
                id="gfix_sweep",
                name="gfix -sweep",
                description="Limpa versões antigas",
                sql="gfix -sweep {database}"
            ),
            MaintenanceTool(
                id="gbak",
                name="gbak",
                description="Backup/Restore",
                sql="gbak -b {database} {backup}"
            ),
            MaintenanceTool(
                id="gstat",
                name="gstat",
                description="Estatísticas",
                sql="gstat -h {database}"
            ),
        ],
        docs=DOCS[EngineType.FIREBIRD]
    ),
}

# Lista simplificada de motores
ENGINES_LIST = [
    EngineInfo(
        id=EngineType.SQLITE,
        name="SQLite",
        icon="🗃️",
        port=None,
        description="Banco de dados leve em arquivo único, ideal para instalações single-node"
    ),
    EngineInfo(
        id=EngineType.POSTGRESQL,
        name="PostgreSQL",
        icon="🐘",
        port=5432,
        description="Banco de dados robusto e escalável para ambientes corporativos"
    ),
    EngineInfo(
        id=EngineType.MARIADB,
        name="MariaDB",
        icon="🐬",
        port=3306,
        description="Fork do MySQL com melhor performance e compatibilidade"
    ),
    EngineInfo(
        id=EngineType.FIREBIRD,
        name="Firebird",
        icon="🔥",
        port=3050,
        description="Banco de dados legado multiplataforma com modo embedded"
    ),
]
