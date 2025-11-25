# 🎮 FC26 Career Analyzer - Documento de Planejamento Completo

**Versão:** 1.0

**Data:** 19/11/2025

**Autor:** Mateus

**Status:** ✅ APROVADO - Pronto para Iniciar

---

# 📋 ÍNDICE

1. Visão Geral do Projeto
2. Objetivos e Escopo
3. Requisitos do Sistema
4. Arquitetura Técnica
5. Stack Tecnológica Definitiva
6. Modelo de Dados
7. Fluxos de Trabalho
8. Plano de Desenvolvimento
9. Testes e Validação
10. Deployment e Operação
11. Orçamento e Recursos
12. Riscos e Mitigações
13. ✅ Decisões Aprovadas

---

# 1️⃣ VISÃO GERAL DO PROJETO

## 1.1 Problema

Atualmente, jogadores de EA FC 26 Career Mode têm **dados valiosos** trancados dentro de arquivos binários sem forma fácil de:

- Analisar progressão de jogadores ao longo do tempo
- Responder perguntas complexas sobre estatísticas
- Visualizar tendências e padrões
- Tomar decisões estratégicas informadas

## 1.2 Solução Proposta

Um sistema completo que:

1. **Extrai** dados do arquivo de save do EA FC 26
2. **Processa** e estrutura esses dados em formato analisável
3. **Integra** com LLM (OpenAI ChatGPT) para permitir análise em linguagem natural
4. **Visualiza** métricas e estatísticas via CLI e API REST

## 1.3 Valor Entregue

✅ Respostas instantâneas sobre qualquer aspecto da carreira

✅ Insights que não são visíveis no jogo

✅ Histórico completo de evolução e decisões

✅ Tomada de decisão baseada em dados

✅ Sistema 100% local (privacidade garantida)

---

# 2️⃣ OBJETIVOS E ESCOPO

## 2.1 Objetivos Primários (MUST HAVE)

**O1:** Extrair dados de saves do FC 26

- Critério: Parser funciona com saves atuais e futuros updates

**O2:** Armazenar dados estruturados

- Critério: Banco de dados relacional com queries <100ms

**O3:** Integrar com OpenAI API (ChatGPT)

- Critério: Responde perguntas com 95%+ de precisão

**O4:** Análises básicas disponíveis

- Critério: Mínimo 10 tipos de queries funcionando

## 2.2 Objetivos Secundários (SHOULD HAVE)

**O5:** CLI para consultas

- Critério: Interface funcional via terminal

**O6:** API REST

- Critério: Endpoints acessíveis para futuras integrações

**O7:** Comparação temporal de saves

- Critério: Pode comparar 2+ momentos da carreira

**O8:** Busca semântica avançada

- Critério: Vector search com embeddings

## 2.3 Objetivos Futuros (NICE TO HAVE)

- Interface web (Dashboard)
- Exportar relatórios em PDF
- Sistema de notificações
- Análise preditiva (ML)

## 2.4 O Que NÃO Está no Escopo

❌ **Não vamos fazer:**

- Editor de save (modificar dados do jogo)
- Multiplayer/compartilhamento online
- App mobile nativo
- Integração com console (só PC)
- Suporte a FIFA/FC 17-25 (foco em FC 26)

---

# 3️⃣ REQUISITOS DO SISTEMA

## 3.1 Requisitos Funcionais

### RF-01: Extração de Dados

**Descrição:** Sistema deve extrair dados completos do arquivo de save

**Entrada:** Arquivo binário de save do EA FC 26

**Saída:** JSON estruturado com todas as tabelas

**Regras:**

- Processar saves de até 100MB
- Detectar versão automaticamente
- Validar integridade dos dados

### RF-02: Armazenamento Estruturado

**Descrição:** Dados extraídos em banco relacional

**Tabelas Principais:**

- players (jogadores)
- teams (times)
- matches (partidas)
- transfers (transferências)
- finances (finanças)
- tactics (táticas)

**Regras:**

- Normalização 3NF
- Índices em campos de busca frequente
- Constraints de integridade referencial

### RF-03: Query via Linguagem Natural

**Descrição:** Usuário pode fazer perguntas em português sobre a carreira

**Exemplos:**

- "Quais os 10 melhores jogadores do meu elenco?"
- "Qual foi minha sequência de vitórias mais longa?"
- "Compare meu desempenho com 4-3-3 vs 3-5-2"

**Regras:**

- Resposta em <10 segundos
- Citar dados usados (rastreabilidade)
- Indicar quando não há dados suficientes

### RF-04: Comparação Temporal

**Funcionalidades:**

- Importar save antigo e novo
- Calcular diferenças (evolução OVR, transferências)
- Gerar relatório de mudanças

### RF-05: Visualizações

**Tipos:**

- Distribuição de idades do elenco
- Evolução de overall ao longo das temporadas
- Scatter plot potencial vs idade
- Histórico de resultados
- Gráfico de finanças

## 3.2 Requisitos Não-Funcionais

**RNF-01: Performance**

- Extração: máximo 30 segundos
- Query SQL: máximo 100ms
- Resposta LLM: máximo 10 segundos

**RNF-02: Confiabilidade**

- Taxa de sucesso na extração: >95%
- Zero perda de dados após importação

**RNF-03: Usabilidade**

- Interface em português brasileiro
- Máximo 3 passos para qualquer funcionalidade
- Mensagens de erro claras

**RNF-04: Segurança**

- Dados 100% locais (privacidade)
- API key armazenada de forma segura

**RNF-05: Manutenibilidade**

- Código documentado (docstrings)
- Cobertura de testes >70%
- Logs estruturados
- Versionamento Git

---

# 4️⃣ ARQUITETURA TÉCNICA

## 4.1 Visão Geral

```
CAMADA DE APRESENTAÇÃO
├── CLI Tool (Python - Click/Typer)
└── API REST (FastAPI)

CAMADA DE API
└── FastAPI REST API
    ├── Query Router (SQL/Vector/Hybrid)
    ├── Auth Handler
    └── Rate Limiter

CAMADA DE LÓGICA DE NEGÓCIO
├── CareerAnalyzer (parse_save, extract_players, stats)
├── DataProcessor (normalize, validate, transform)
├── LLMIntegration (build_context, query_gpt)
└── VectorSearch (embeddings, similarity_search)

CAMADA DE DADOS
├── SQLite Database (Relational)
│   ├── players
│   ├── teams
│   ├── matches
│   ├── transfers
│   └── finances
└── ChromaDB (Vector)
    ├── embeddings
    └── metadata

CAMADA EXTERNA
├── EA FC 26 Save Files (Binary)
└── OpenAI API (ChatGPT)
```

## 4.2 Padrões Arquiteturais

**Pattern 1: Repository Pattern**

```python
class PlayerRepository:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_by_id(self, player_id: int) -> Player:
        pass
    
    def get_all(self, filters: dict = None) -> List[Player]:
        pass
```

**Pattern 2: Service Layer**

```python
class CareerAnalysisService:
    def __init__(self, player_repo, match_repo, llm_client):
        self.players = player_repo
        self.matches = match_repo
        self.llm = llm_client
```

**Pattern 3: Strategy Pattern (Query Router)**

```python
class QueryStrategy(ABC):
    @abstractmethod
    def execute(self, query: str) -> QueryResult:
        pass

class SQLQueryStrategy(QueryStrategy):
    def execute(self, query: str) -> QueryResult:
        # Roteamento para SQL
        pass
```

## 4.3 Decisões Arquiteturais

### DA-01: Por que SQLite?

**Decisão:** Usar SQLite como banco principal

**Razões:**

✅ Zero configuração (arquivo único)

✅ Performance excelente para <100k registros

✅ Portabilidade total

✅ Python tem suporte nativo

✅ Backup trivial

**Consequências:**

⚠️ Não suporta queries concorrentes (mas não é necessário)

### DA-02: Por que ChromaDB?

**Decisão:** Usar ChromaDB para vector search

**Razões:**

✅ Totalmente local (privacidade)

✅ API simples e pythônica

✅ Persistência em disco

✅ Integração fácil com sentence-transformers

✅ Gratuito e open-source

### DA-03: Por que FastAPI?

**Decisão:** Usar FastAPI para API REST

**Razões:**

✅ Type hints nativos

✅ Auto-documentação (Swagger UI)

✅ Assíncrono por padrão

✅ Validação automática (Pydantic)

✅ Comunidade ativa

### DA-04: Por que OpenAI (ChatGPT)?

**Decisão:** Usar OpenAI API como LLM principal

**Razões:**

✅ API madura e estável

✅ Excelente em análise de dados estruturados

✅ Pricing competitivo

✅ Documentação completa

✅ SDKs oficiais bem mantidos

✅ Suporte a function calling nativo

**Modelo Escolhido:** GPT-4o (melhor custo-benefício)

- Input: $2.50 por 1M tokens
- Output: $10.00 por 1M tokens
- Context window: 128k tokens

---

# 5️⃣ STACK TECNOLÓGICA DEFINITIVA

## 5.1 Backend

**Linguagem:** Python 3.10+

- Justificativa: Ecossistema ML/Data, bibliotecas ricas

**Parser:** Node.js 18+ + fifa-career-save-parser

- Justificativa: Parser já existente e funcional

**API Framework:** FastAPI 0.104+

- Justificativa: Moderno, rápido, type-safe

**DB Relacional:** SQLite 3.40+

- Justificativa: Local, zero config, portável

**Vector DB:** ChromaDB 0.4.18+

- Justificativa: Local, open-source, fácil

**ORM:** SQLAlchemy 2.0+

- Justificativa: ORM maduro, suporte SQLite

**Validação:** Pydantic 2.0+

- Justificativa: Type validation, integra FastAPI

**LLM SDK:** OpenAI Python SDK 1.3+

- Justificativa: SDK oficial, bem documentado

**Embeddings:** sentence-transformers 2.2+

- Justificativa: Modelos pré-treinados de qualidade

## 5.2 Ferramentas de Desenvolvimento

**Version Control:** Git + GitHub

**Environment:** venv + pip

**Linting:** Ruff

**Formatting:** Black

**Testing:** pytest

**Documentation:** MkDocs

**Task Runner:** Make

## 5.3 Infraestrutura

**Fase 1 (MVP) - 100% Local:**

```
Windows 11
└── WSL2 (Ubuntu 24.04)
    ├── Python 3.10
    ├── Node.js 18
    ├── SQLite
    └── ChromaDB
```

---

# 6️⃣ MODELO DE DADOS

## 6.1 Schema do Banco de Dados

### Tabela: players

```sql
CREATE TABLE players (
    player_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    common_name TEXT,
    
    -- Atributos principais
    overall_rating INTEGER CHECK(overall_rating BETWEEN 40 AND 99),
    potential INTEGER CHECK(potential BETWEEN 40 AND 99),
    age INTEGER CHECK(age BETWEEN 16 AND 50),
    
    -- Física e posição
    height INTEGER,
    weight INTEGER,
    preferred_position TEXT,
    secondary_positions TEXT,
    
    -- Habilidades
    weak_foot INTEGER CHECK(weak_foot BETWEEN 1 AND 5),
    skill_moves INTEGER CHECK(skill_moves BETWEEN 1 AND 5),
    
    -- Contrato e time
    team_id INTEGER,
    contract_end_date TEXT,
    wage INTEGER,
    value INTEGER,
    
    -- Status
    loan_status TEXT,
    morale INTEGER CHECK(morale BETWEEN 0 AND 100),
    
    -- Metadados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

CREATE INDEX idx_players_overall ON players(overall_rating);
CREATE INDEX idx_players_team ON players(team_id);
```

### Tabela: teams

```sql
CREATE TABLE teams (
    team_id INTEGER PRIMARY KEY,
    team_name TEXT NOT NULL,
    short_name TEXT,
    
    -- Classificações
    overall_rating INTEGER,
    attack_rating INTEGER,
    midfield_rating INTEGER,
    defense_rating INTEGER,
    
    -- Finanças
    transfer_budget INTEGER,
    wage_budget INTEGER,
    club_worth INTEGER,
    
    -- Atributos do clube
    domestic_prestige INTEGER,
    international_prestige INTEGER,
    
    -- Liga
    league_id INTEGER,
    country TEXT,
    
    -- Tática
    formation TEXT,
    tactical_style TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela: matches

```sql
CREATE TABLE matches (
    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    
    home_score INTEGER NOT NULL,
    away_score INTEGER NOT NULL,
    result TEXT CHECK(result IN ('win', 'draw', 'loss')),
    
    competition_name TEXT,
    competition_round TEXT,
    match_date TEXT,
    season TEXT,
    
    possession_home INTEGER,
    possession_away INTEGER,
    shots_home INTEGER,
    shots_away INTEGER,
    
    is_home_match BOOLEAN,
    user_team_id INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id)
);

CREATE INDEX idx_matches_date ON matches(match_date);
```

### Tabela: transfers

```sql
CREATE TABLE transfers (
    transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    player_id INTEGER NOT NULL,
    player_name TEXT NOT NULL,
    
    from_team_id INTEGER,
    to_team_id INTEGER NOT NULL,
    
    transfer_fee INTEGER,
    transfer_type TEXT CHECK(transfer_type IN ('permanent', 'loan', 'free')),
    loan_duration_months INTEGER,
    
    transfer_date TEXT,
    season TEXT,
    transfer_window TEXT,
    
    rating_at_signing INTEGER,
    rating_after_1_year INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);
```

### Tabela: career_metadata

```sql
CREATE TABLE career_metadata (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    
    manager_name TEXT,
    current_team_id INTEGER,
    current_season TEXT,
    current_date TEXT,
    
    total_matches_played INTEGER DEFAULT 0,
    total_wins INTEGER DEFAULT 0,
    total_draws INTEGER DEFAULT 0,
    total_losses INTEGER DEFAULT 0,
    
    trophies_won TEXT,
    teams_managed TEXT,
    
    save_file_path TEXT,
    last_import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (current_team_id) REFERENCES teams(team_id)
);
```

### Views Úteis

```sql
-- Melhores jogadores do elenco
CREATE VIEW v_top_squad_players AS
SELECT 
    p.player_id,
    p.first_name || ' ' || p.last_name AS full_name,
    p.overall_rating,
    p.potential,
    p.age,
    p.preferred_position,
    [t.team](http://t.team)_name,
    (p.potential - p.overall_rating) AS growth_potential
FROM players p
JOIN teams t ON [p.team](http://p.team)_id = [t.team](http://t.team)_id
WHERE [p.team](http://p.team)_id = (SELECT current_team_id FROM career_metadata)
ORDER BY p.overall_rating DESC;
```

## 6.2 Modelo Vector Search

```python
# ChromaDB Collection
{
    "collection_name": "player_profiles",
    "embedding_function": "all-MiniLM-L6-v2",
    "documents": [
        {
            "id": "player_12345",
            "text": "João Silva, 23 anos, Atacante (ST), Overall 89...",
            "metadata": {
                "player_id": 12345,
                "overall": 89,
                "position": "ST",
                "team": "Manchester United"
            }
        }
    ]
}
```

---

# 7️⃣ FLUXOS DE TRABALHO

## 7.1 Fluxo: Importação de Save

```
1. Validação Inicial
   ↓
2. Parser Node.js (Extrair JSON)
   ↓
3. Processamento Python (Normalizar)
   ↓
4. Inserção no SQLite + ChromaDB
   ↓
5. Confirmação ("X jogadores, Y partidas")
```

**Tempo:** 20-30 segundos

## 7.2 Fluxo: Query via LLM

```
1. Análise da Query (classificar tipo)
   ↓
2. Query Router (SQL/Vector/Hybrid)
   ↓
3. Buscar Contexto (executar query)
   ↓
4. Montar Prompt para GPT-4o
   ↓
5. OpenAI API (enviar + aguardar)
   ↓
6. Formatar Resposta
```

**Tempo:** 3-8 segundos

## 7.3 Fluxo: Comparação de Saves

```
1. Selecionar Saves A e B
   ↓
2. Importar ambos (temp DB)
   ↓
3. Diff Engine (calcular diferenças)
   ↓
4. Gerar Relatório
   - Jogadores que evoluíram
   - Novas transferências
   - Resultados
   - Mudanças financeiras
```

---

# 8️⃣ PLANO DE DESENVOLVIMENTO

## 8.1 Estrutura do Projeto

```
fc26-career-analyzer/
├── [README.md](http://README.md)
├── requirements.txt
├── package.json
├── Makefile
├── .env.example
│
├── docs/
│   ├── [architecture.md](http://architecture.md)
│   └── [user-guide.md](http://user-guide.md)
│
├── parser/          # Node.js
│   └── index.js
│
├── src/             # Python
│   ├── core/
│   │   ├── [analyzer.py](http://analyzer.py)
│   │   └── [processor.py](http://processor.py)
│   │
│   ├── database/
│   │   ├── [models.py](http://models.py)
│   │   └── [repositories.py](http://repositories.py)
│   │
│   ├── llm/
│   │   ├── openai_[client.py](http://client.py)
│   │   ├── prompt_[builder.py](http://builder.py)
│   │   └── query_[router.py](http://router.py)
│   │
│   ├── vector/
│   │   ├── [embeddings.py](http://embeddings.py)
│   │   └── [search.py](http://search.py)
│   │
│   ├── api/
│   │   ├── [main.py](http://main.py)
│   │   └── routes/
│   │
│   └── utils/
│       ├── [config.py](http://config.py)
│       └── [logger.py](http://logger.py)
│
├── tests/
│   ├── unit/
│   └── integration/
│
└── data/            # Local (gitignored)
    ├── saves/
    ├── career.db
    └── chroma/
```

## 8.2 Sprint Planning

### 🏃 SPRINT 1: Fundação (5 dias)

**Objetivo:** Setup + Parser funcionando

**Tarefas:**

- Setup Git + ambiente Python/Node
- Integrar fifa-career-save-parser
- Criar schema SQLite completo
- Implementar SQLAlchemy models
- Script de importação
- Testar com save real
- Validar integridade

**Entregável:** Sistema importa save → SQLite ✅

---

### 🏃 SPRINT 2: Integração LLM (5 dias)

**Objetivo:** ChatGPT respondendo perguntas

**Tarefas:**

- Configurar OpenAI SDK
- Implementar OpenAIClient wrapper
- Sistema de prompt templates
- Query router básico
- CLI simples (Click)
- Testes de queries

**Entregável:** CLI funcional com GPT-4o ✅

---

### 🏃 SPRINT 3: Vector Search (5 dias)

**Objetivo:** RAG completo

**Tarefas:**

- Integrar ChromaDB
- Gerar embeddings (sentence-transformers)
- Criar índice de jogadores
- Similarity search
- Hybrid search (SQL + Vector)
- Otimizar query router

**Entregável:** Sistema RAG SQL + Vector ✅

---

### 🏃 SPRINT 4: API REST (5 dias)

**Objetivo:** API acessível

**Tarefas:**

- Setup FastAPI
- Rotas principais:
    - POST /saves/import
    - GET /saves/stats
    - POST /query
    - GET /players
    - GET /teams
- Swagger docs
- Testes de API

**Entregável:** API REST em [localhost:8000](http://localhost:8000) ✅

---

### 🏃 SPRINT 5: Features Avançadas (5 dias)

**Objetivo:** Sistema completo

**Tarefas:**

- SaveComparator (diff de saves)
- Módulo de analytics
- 10+ tipos de análises
- Visualizações (matplotlib)
- Documentação completa (MkDocs)
- User guide + troubleshooting

**Entregável:** MVP v1.0 completo e documentado 🚀

---

## 8.3 Definição de Done (DoD)

Para cada feature:

✅ **Código:**

- Implementado conforme spec
- Self-review
- Sem warnings
- Formatado (Black)

✅ **Testes:**

- Testes unitários
- Testes integração
- Cobertura >70%
- Todos passando

✅ **Documentação:**

- Docstrings
- README atualizado
- Changelog
- Exemplos de uso

✅ **Validação:**

- Testado manualmente
- Performance ok
- Error handling
- Logs apropriados

---

# 9️⃣ TESTES E VALIDAÇÃO

## 9.1 Estratégia de Testes

**Pirâmide:**

- 75% Unit Tests (pytest + mocking)
- 20% Integration Tests (pytest + DB)
- 5% E2E Tests

## 9.2 Casos de Teste Principais

### Importação

```python
def test_import_valid_save(sample_save_file):
    result = import_save(sample_save_file)
    assert result.success == True
    assert result.players_imported > 0

def test_import_corrupted_save(corrupted_save):
    with pytest.raises(CorruptedSaveError):
        import_save(corrupted_save)
```

### Queries LLM

```python
def test_simple_query():
    response = query_career("Top 5 jogadores")
    assert response.success == True
    assert len(response.players) == 5

def test_query_without_data():
    clear_database()
    response = query_career("Artilheiros")
    assert "não há dados" in response.text.lower()
```

### Vector Search

```python
def test_semantic_search():
    results = vector_[db.search](http://db.search)("striker jovem potencial")
    assert len(results) > 0
    assert all(r.position == 'ST' for r in results)
```

## 9.3 Performance

```python
def test_import_performance(benchmark, large_save):
    result = benchmark(import_save, large_save)
    assert benchmark.stats['mean'] < 30.0  # segundos

def test_query_latency(benchmark):
    result = benchmark(query_career, "Top players")
    assert benchmark.stats['mean'] < 10.0  # segundos
```

---

# 🔟 DEPLOYMENT E OPERAÇÃO

## 10.1 Setup Inicial

**Script de Instalação:**

```bash
#!/bin/bash
echo "🎮 FC26 Career Analyzer - Setup"

# Verificar dependências
command -v node || sudo apt install nodejs
command -v python3.10 || sudo apt install python3.10

# Setup Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup Node
cd parser && npm install && cd ..

# Configurar .env
cp .env.example .env
echo "EDITE .env e adicione OPENAI_API_KEY"

# Criar DB
python -m src.database.migrations.init_db

echo "✅ Setup completo!"
```

## 10.2 Makefile

```makefile
install:  ## Instala dependências
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt

test:  ## Roda testes
	./venv/bin/pytest tests/ -v --cov=src

run-api:  ## Inicia API
	./venv/bin/uvicorn src.api.main:app --reload

run-cli:  ## CLI interativo
	./venv/bin/python [cli.py](http://cli.py)

import:  ## Importa save
	./venv/bin/python [cli.py](http://cli.py) import $(SAVE)

backup:  ## Backup DB
	cp data/career.db backups/career_$(date +%Y%m%d).db
```

## 10.3 Variáveis de Ambiente

```bash
# .env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

DATABASE_URL=sqlite:///./data/career.db
VECTOR_DB_PATH=./data/chroma

API_HOST=0.0.0.0
API_PORT=8000

LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

ENABLE_VECTOR_SEARCH=true
ENABLE_CACHE=true
CACHE_TTL_SECONDS=3600
```

---

# 💰 ORÇAMENTO E RECURSOS

## 11.1 Custos Estimados

### 100% Local (APROVADO ✅)

**Infraestrutura:** R$0/mês

- PC local (já possui)
- SSD local (já possui)

**Software:** R$0/mês

- Python/Node (open-source)
- SQLite (open-source)
- ChromaDB (open-source)

**API OpenAI:** R$30-100/mês

- Modelo: GPT-4o
- Preço:
    - Input: $2.50 por 1M tokens
    - Output: $10.00 por 1M tokens
- Estimativa:
    - 500-1500 queries/mês
    - ~3k tokens por query
    - Total: ~1.5-4.5M tokens/mês
- Custo: $5-20/mês = **R$25-100/mês**

**TOTAL:** R$30-100/mês ✅

**✅ Aprovado pelo cliente!**

---

## 11.2 Tempo de Desenvolvimento

**Total:** 25 dias úteis (~5 semanas)

- Sprint 1: 5 dias (40h)
- Sprint 2: 5 dias (40h)
- Sprint 3: 5 dias (40h)
- Sprint 4: 5 dias (40h)
- Sprint 5: 5 dias (40h)

**TOTAL:** 200 horas (~40h/semana)

**✅ Tempo aprovado pelo cliente!**

---

# ⚠️ RISCOS E MITIGAÇÕES

## 12.1 Matriz de Riscos

**R1: Parser não funciona com FC 26**

- Probabilidade: Média (50%)
- Impacto: Alto
- Severidade: 🔴 CRÍTICO
- Mitigação: Testar imediatamente, backup com Live Editor

**R2: API OpenAI muito cara**

- Probabilidade: Baixa (20%)
- Impacto: Médio
- Mitigação: Cache agressivo, rate limiting

**R3: Save corrompido**

- Probabilidade: Baixa (15%)
- Impacto: Alto
- Mitigação: Sempre backup antes de importar

**R4: Performance ruim**

- Probabilidade: Média (40%)
- Impacto: Médio
- Mitigação: Otimizar queries, paginação

**R7: Updates do jogo quebram parser**

- Probabilidade: Alta (70%)
- Impacto: Médio
- Mitigação: Monitorar comunidade, atualizar

---

# ✅ DECISÕES APROVADAS

## Confirmação do Cliente (19/11/2025)

### 1. Orçamento

✅ **APROVADO:** R$30-100/mês

- Dentro do orçamento disponível
- Custos previsíveis
- Apenas OpenAI API

### 2. Cronograma

✅ **APROVADO:** 5 semanas (~40h/semana)

- Tempo: 25 dias úteis
- Dedicação: Viável para estagiário
- Flexível se necessário

### 3. Prioridade

✅ **DEFINIDO:** Sistema Completo (Sprints 1-5)

- Não incluir dashboard web (Sprint 6)
- Focar em CLI + API REST
- Funcionalidades essenciais

### 4. Interface Inicial

✅ **DEFINIDO:** CLI + API REST

- CLI para uso rápido
- API REST para flexibilidade futura
- Dashboard web fica para v2.0

### 5. LLM Provider

✅ **DEFINIDO:** OpenAI (ChatGPT)

- Modelo: GPT-4o
- API madura e estável
- Custo-benefício adequado
- Function calling nativo

---

# 🚀 PRÓXIMOS PASSOS IMEDIATOS

## Checkpoint Crítico (FAZER AGORA)

### Validação do Parser (10 minutos)

```bash
# Teste se parser funciona com FC 26
npm install fifa-career-save-parser
node test_parser.js
```

**Se funcionar:** ✅ Iniciar Sprint 1

**Se não funcionar:** ⚠️ Avaliar Plano B (Live Editor)

---

## Sprint 1 - Dia 1 (HOJE)

### Tarefas Imediatas

**1. Setup Repositório (30 min)**

- [ ]  Criar repo GitHub
- [ ]  Clonar localmente
- [ ]  Setup estrutura de pastas
- [ ]  Commit inicial

**2. Setup Ambiente (1h)**

- [ ]  Criar venv Python
- [ ]  Instalar dependências base
- [ ]  Setup Node.js
- [ ]  Testar parser com seu save

**3. Documentação Inicial (30 min)**

- [ ]  README básico
- [ ]  .env.example
- [ ]  .gitignore

**4. Validação (30 min)**

- [ ]  Parser extrai JSON?
- [ ]  Estrutura de dados ok?
- [ ]  Pronto para Sprint 1 completo?

---

## Status: 🟢 PRONTO PARA INICIAR

**Data de Aprovação:** 19/11/2025

**Início Previsto:** 19/11/2025

**Conclusão Prevista:** ~23/12/2025 (Sprint 5)

**Responsável:** Mateus

**Revisão:** Semanal (toda sexta)

---

**Quer que eu ajude a criar os arquivos iniciais do projeto agora? (requirements.txt, .env.example, estrutura de pastas, etc.)**