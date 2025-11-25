
# RELATORIO DE INVESTIGACAO: NOMES DOS JOGADORES

## Resumo da Analise

**Total de tabelas analisadas:** 41
**Tabelas relacionadas a nomes:** 2
**Tabelas relacionadas a players:** 13

---

## CENARIO IDENTIFICADO


### CENARIO A: Lookup Table Encontrada

**Status:** Tabela de mapeamento ID -> String identificada

**Tabelas encontradas:**

- `editedplayernames` (5 colunas)
  - Colunas: firstname, commonname, playerjerseyname, surname, playerid
  - Sample: {'firstname': 'Eduardo', 'commonname': 'Eduardo Sasha', 'playerjerseyname': 'Sasha', 'surname': 'Colcenti Antunes', 'playerid': 201434}

- `dcplayernames` (2 colunas)
  - Colunas: name, nameid
  - Sample: {'name': 'Isaac Romero', 'nameid': 44000}

**Proximos passos:**
1. Implementar JOIN entre `players` e lookup table
2. Mapear firstnameid/lastnameid -> strings
3. Atualizar Player model com computed property
4. Re-importar dados

**Tempo estimado:** 15 minutos

---

## Dados Coletados

### Step 1: Tabelas Escaneadas
- `career_managerinfo` (1 rows)
- `career_managerpref` (1 rows)
- `career_users` (1 rows)
- `career_youthplayers` (15 rows)
- `career_competitionprogress` (7 rows)
- `career_playergrowthuserseason` (49 rows)
- `career_presignedcontract` (101 rows)
- `career_playercontract` (49 rows)
- `career_squadranking` (31 rows)
- `career_playermatchratinghistory` (283 rows)
- `career_scoutmission` (3 rows)
- `career_playerlastmatchhistory` (3723 rows)
- `career_managerhistory` (1 rows)
- `career_scouts` (3 rows)
- `persistent_events` (1 rows)
- `career_managerawards` (1 rows)
- `career_playerlastgrowth` (22230 rows)
- `career_calendar` (1 rows)
- `teams` (846 rows)
- `formations` (875 rows)

### Step 4: Career Tables Relevantes
- `career_playerlastgrowth`: playerid
- `career_playerlastmatchhistory`: playerfact, playeroverall, playerid
- `career_playermatchratinghistory`: playerid
- `career_presignedcontract`: isexchangedplayer, playerid, secondaryplayerid

---

## Conclusao

Execute os proximos passos recomendados acima para resolver o bloqueador de nomes.
