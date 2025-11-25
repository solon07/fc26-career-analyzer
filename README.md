# FC26 Career Analyzer

## ✨ Features

- 🔍 **Extração completa de dados** do save binário do FC 26
- 🤖 **Análise via IA (Gemini 3 Pro)** - Perguntas em português sobre sua carreira
- 📊 **18+ tabelas mapeadas** - Jogadores, contratos, partidas, evolução, etc.
- 📈 **22k+ registros de evolução** - Histórico completo de crescimento de jogadores
- 👤 **Resolução parcial de nomes** - Jogadores editados/novos com nomes reais ⚠️
- 💾 **100% local** - Seus dados não saem do seu computador
- 🔎 **Vector search (RAG)** - Busca semântica inteligente
- 🚀 **API REST** - FastAPI para integrações futuras
- 🖥️ **CLI interativo** - Interface de linha de comando amigável

> ⚠️ **Nota:** Jogadores da base do jogo aparecem como "Player #ID". 
> [Veja detalhes](#%EF%B8%8F-limitação-conhecida-resolução-parcial-de-nomes)

## 🎮 Uso

### Comandos Básicos

Para iniciar a CLI:
```bash
python -m src.cli.main
```

---

## 🤖 Análise com IA (Sprint 2 - NOVO!)

### Comando `query` - Perguntas em Linguagem Natural

Faça perguntas sobre seu save usando Google Gemini:

**Modo direto:**
```bash
# Pergunta única
fc26-analyzer query "quem é meu melhor jogador?"
fc26-analyzer query "jogadores jovens com alto potencial"
fc26-analyzer query "como melhorar minha defesa?"
```

**Modo interativo:**
```bash
# Inicia conversa contínua
fc26-analyzer query

# Ou forçar modo interativo
fc26-analyzer query "pergunta inicial" --interactive
```

**Opções disponíveis:**
- `--context`, `-c`: Tipo de contexto (summary, top_players, filtered)
- `--limit`, `-l`: Número de jogadores no contexto (padrão: 10)
- `--interactive`, `-i`: Forçar modo interativo

**Exemplos de perguntas:**
- "Qual meu melhor jogador em cada posição?"
- "Jogadores com potencial acima de 85"
- "Sugestões de contratações para melhorar o meio-campo"
- "Comparar Mbappé vs Haaland"
- "Análise tática do meu elenco"

### ⚙️ Configuração da API

**1. Obter API Key do Google Gemini:**
```bash
# Acesse: https://aistudio.google.com/app/apikey
# Crie uma API key gratuita
```

**2. Configurar no .env:**
```bash
GEMINI_API_KEY=sua_api_key_aqui
```

**3. Testar conexão:**
```bash
fc26-analyzer query "teste de conexão"
```

**Limites da API gratuita:**
- 15 requests/minuto
- 1M tokens/minuto
- 1.500 requests/dia

---

## 📊 Features Implementadas

### ✅ Sprint 1: Foundation
- Parser Node.js validado com FC26
- SQLAlchemy models (Player, PlayerInfo)
- Import pipeline funcionando
- CLI commands: `import`, `info`
- Name resolution system (parcial)

### ✅ Sprint 2: IA Integration (NOVO!)
- Google Gemini API integration
- Query command (direto + interativo)
- Context building adaptativo
- Rich formatting com Markdown
- [OPCIONAL] Query router (SQL vs Gemini)

### 🔮 Sprint 3: Planejado
- Team models e análise de times
- Contract tracking
- Player growth analysis
- Transfer recommendations
- Formation optimizer

---

## 🧪 Testes
```bash
# Rodar todos os testes
pytest

# Testes específicos
pytest tests/test_llm_integration.py

# Com coverage
pytest --cov=src tests/

# Apenas testes de integração
pytest -m integration
```

**Coverage atual:** ~75% (target: >70% ✅)

## 📊 Dados Disponíveis

O sistema extrai e analisa diversas tabelas do save file, incluindo:
- **players**: Informações detalhadas dos jogadores (atributos, posições, etc.)
- **career_users**: Dados do treinador e do clube
- **team_player_links**: Vínculos entre jogadores e times
- **teams**: Informações dos clubes
- **player_growth_user**: Histórico de evolução dos jogadores
- E muito mais...

---

## ⚠️ Limitação Conhecida: Resolução Parcial de Nomes

### O Que Funciona ✅

O sistema resolve nomes para:
- **Jogadores editados/customizados** (~800 jogadores)
- **Jogadores novos/atualizações** (~4.900 jogadores)
- **Jogadores da base** (youth academy)

**Exemplo de output:**
```bash
✅ Eduardo Sasha (OVR 78, LW)
✅ Adson (OVR 75, RW)
✅ Custom Player 123 (OVR 82, ST)
```

### Limitação Atual ⚠️

**Jogadores da database base do jogo** aparecem como `Player #[ID]`:
```bash
⚠️ Player #71055 (OVR 85, ST)
⚠️ Player #158023 (OVR 89, RW)
```

**Por que isso acontece?**

O arquivo de save do FC26 armazena apenas **modificações** feitas durante a carreira:
- Nomes originais (Cristiano Ronaldo, Messi, etc.) estão na **database interna do jogo**
- O parser comunitário não acessa esses arquivos internos
- Save file contém apenas IDs de referência

### Impacto no Sistema 📊

**O sistema ainda é totalmente funcional!**

✅ **Análises estatísticas funcionam perfeitamente:**
- "Top 10 jogadores por OVR" → Funciona
- "Jogadores com potencial >85" → Funciona
- "Compare 4-3-3 vs 3-5-2" → Funciona

✅ **Gemini pode interpretar IDs:**
User: "Quem é o Player #71055?"
Gemini: "Player #71055 é um atacante (ST) com OVR 85, 
         age 28, joga no seu time..."

⚠️ Apenas queries que precisam de nomes específicos são afetadas:
User: "Quem é o melhor atacante?"
Response: "Player #71055 (OVR 85)" ← Não mostra nome real

### Roadmap de Melhoria 🛣️

#### Fase 1: MVP (Atual - Sprint 1-2) ✅
- Sistema funcional com fallback inteligente
- Foco em análises estatísticas
- UX aceitável com IDs formatados

#### Fase 2: Enhancement (Sprint 4-5) 🔄
- Integração com API externa (FUTDB/SOFIFA)
- Resolução em background de nomes faltantes
- Cache local de nomes resolvidos
- Melhoria significativa de UX

#### Fase 3: Solução Definitiva (v2.0) 🎯
- Extração da database interna do FC26
- 100% de nomes resolvidos
- Solução totalmente local

### Alternativa Manual 💡

Se você precisa de nomes específicos agora:

1. **Use SOFIFA para lookup manual:**
   https://sofifa.com/player/[ID]
   Ex: https://sofifa.com/player/71055

2. **Exporte do FIFA Live Editor:**
   - Abra sua carreira no Live Editor
   - Exporte lista de jogadores com nomes
   - Importe manualmente no analyzer

### Perguntas Frequentes ❓

**P: Isso afeta as análises com IA?**
R: Não! Gemini trabalha perfeitamente com IDs e estatísticas.

**P: Posso adicionar nomes manualmente?**
R: Sim, futuramente teremos uma feature de "name override" manual.

**P: Quando teremos resolução completa?**
R: Sprint 4-5 (integração com API) ou v2.0 (solução definitiva).

**P: O sistema ainda vale a pena?**
R: Absolutamente! Análises estatísticas são o core value, nomes são enhancement.
