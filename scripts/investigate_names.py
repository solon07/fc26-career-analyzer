#!/usr/bin/env python3
"""
Script de investigação: Encontrar nomes reais no parser output
Objetivo: Descobrir onde firstnameid/lastnameid mapeiam para strings

Output: Relatório markdown com cenário identificado + próximos passos
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


# Cores para output (desativadas para evitar erro de encoding no Windows)
class Colors:
    GREEN = ""
    YELLOW = ""
    RED = ""
    BLUE = ""
    BOLD = ""
    END = ""


def load_parser_output(path: str = "parser/output/test_parse.json") -> List[Dict]:
    """Carrega o JSON do parser e normaliza para lista de tabelas"""
    print("Loading parser output...")
    with open(path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    tables = []
    if isinstance(raw_data, list):
        for db_index, db in enumerate(raw_data):
            for table_name, rows in db.items():
                tables.append(
                    {"tablename": table_name, "rows": rows, "source_db": db_index}
                )
    elif isinstance(raw_data, dict):
        for table_name, rows in raw_data.items():
            tables.append({"tablename": table_name, "rows": rows, "source_db": 0})

    print(
        f"Loaded {len(tables)} tables from {len(raw_data) if isinstance(raw_data, list) else 1} databases\n"
    )
    return tables


def step1_scan_tables(data: List[Dict]) -> Dict[str, Any]:
    """Step 1: Scan completo de tabelas"""
    print("=" * 60)
    print("STEP 1: SCAN DE TABELAS")
    print(f"{'='*60}\n")

    results = {
        "total_tables": len(data),
        "name_related": [],
        "player_related": [],
        "all_tables": [],
    }

    for table in data:
        table_name = table.get("tablename", "unknown")
        row_count = len(table.get("rows", []))
        results["all_tables"].append((table_name, row_count))

        # Buscar tabelas relacionadas a nomes
        name_keywords = ["name", "string", "text", "label"]
        if any(kw in table_name.lower() for kw in name_keywords):
            results["name_related"].append((table_name, row_count))

        # Buscar tabelas relacionadas a players
        if "player" in table_name.lower():
            results["player_related"].append((table_name, row_count))

    # Output
    print(f"Total tables: {results['total_tables']}")
    print(f"\nName-related tables found: {len(results['name_related'])}")
    for name, count in results["name_related"]:
        print(f"  - {name} ({count} rows)")

    print(f"\nPlayer-related tables: {len(results['player_related'])}")
    for name, count in sorted(
        results["player_related"], key=lambda x: x[1], reverse=True
    )[:10]:
        print(f"  - {name} ({count} rows)")

    return results


def step2_inspect_name_tables(data: List[Dict], name_tables: List[tuple]) -> Dict:
    """Step 2: Inspecionar tabelas de nome"""
    print(f"\n{'='*60}")
    print("STEP 2: INSPECAO DE TABELAS DE NOME")
    print(f"{'='*60}\n")

    findings = {}

    if not name_tables:
        print("No name-related tables found")
        return findings

    for table_name, row_count in name_tables:
        table_data = next((t for t in data if t.get("tablename") == table_name), None)
        if not table_data or not table_data.get("rows"):
            continue

        # Analisar primeira row
        first_row = table_data["rows"][0]
        columns = list(first_row.keys())

        print(f"Table: {table_name}")
        print(f"   Rows: {row_count}")
        print(f"   Columns: {', '.join(columns[:10])}")

        # Buscar padrões de ID + String
        has_id = any("id" in col.lower() for col in columns)
        has_string = any(
            isinstance(first_row[col], str) and len(first_row[col]) > 2
            for col in columns
        )

        if has_id and has_string:
            findings[table_name] = {
                "columns": columns,
                "sample_row": first_row,
                "likely_lookup": True,
            }
            print("   POTENTIAL LOOKUP TABLE!")

        print()

    return findings


def step3_search_name_strings(data: List[Dict]) -> Dict:
    """Step 3: Buscar strings de nome em tabelas de player"""
    print(f"\n{'='*60}")
    print("STEP 3: BUSCA DE NAME STRINGS EM TABELAS PLAYER")
    print(f"{'='*60}\n")

    player_tables = [t for t in data if "player" in t.get("tablename", "").lower()]
    findings = {}

    for table in player_tables:
        table_name = table.get("tablename")
        rows = table.get("rows", [])

        if not rows:
            continue

        first_row = rows[0]

        # Buscar campos que podem ser nomes (strings não-vazias)
        name_fields = []
        for key, value in first_row.items():
            if isinstance(value, str) and len(value) > 2:
                # Ignorar campos técnicos
                if not any(x in key.lower() for x in ["guid", "id", "date", "time"]):
                    name_fields.append(key)

        if name_fields:
            findings[table_name] = {
                "name_fields": name_fields,
                "sample": {k: first_row.get(k) for k in name_fields[:3]},
            }

            print(f"{table_name}")
            print(f"   Name fields: {', '.join(name_fields)}")
            print(f"   Sample: {findings[table_name]['sample']}")
            print()

    return findings


def step4_check_career_tables(data: List[Dict]) -> Dict:
    """Step 4: Checar tabelas career_ específicas"""
    print(f"\n{'='*60}")
    print("STEP 4: ANALISE DE TABELAS CAREER_")
    print(f"{'='*60}\n")

    career_tables = [t for t in data if t.get("tablename", "").startswith("career_")]

    # Focar em tabelas com muitos registros (provável dados reais)
    large_tables = [
        (t.get("tablename"), len(t.get("rows", [])))
        for t in career_tables
        if len(t.get("rows", [])) > 100
    ]

    large_tables.sort(key=lambda x: x[1], reverse=True)

    print("Top career_ tables (>100 rows):")
    findings = {}

    for table_name, row_count in large_tables[:10]:
        table_data = next((t for t in data if t.get("tablename") == table_name), None)
        if table_data and table_data.get("rows"):
            first_row = table_data["rows"][0]

            # Buscar campos de nome
            name_like = [
                k
                for k in first_row.keys()
                if "name" in k.lower() or "player" in k.lower()
            ]

            print(f"  {table_name} ({row_count} rows)")
            if name_like:
                print(f"    -> Name-like fields: {', '.join(name_like)}")
                findings[table_name] = name_like

    return findings


def step5_analyze_overlap(data: List[Dict]) -> Dict:
    """Step 5: Análise de overlap de playerids"""
    print(f"\n{'='*60}")
    print("STEP 5: ANALISE DE OVERLAP DE PLAYERIDS")
    print(f"{'='*60}\n")

    # Extrair playerids da tabela players
    players_table = next((t for t in data if t.get("tablename") == "players"), None)
    if not players_table:
        print("Players table not found")
        return {}

    player_ids = {
        row.get("playerid")
        for row in players_table.get("rows", [])
        if row.get("playerid")
    }
    print(f"Players table has {len(player_ids)} unique playerids\n")

    # Buscar tabelas com playerid field
    overlaps = {}
    for table in data:
        table_name = table.get("tablename")
        rows = table.get("rows", [])

        if not rows or table_name == "players":
            continue

        # Check se tem playerid field
        first_row = rows[0]
        playerid_field = None
        for key in first_row.keys():
            if "playerid" in key.lower():
                playerid_field = key
                break

        if playerid_field:
            table_player_ids = {
                row.get(playerid_field) for row in rows if row.get(playerid_field)
            }
            overlap = player_ids & table_player_ids
            overlap_pct = (len(overlap) / len(player_ids)) * 100 if player_ids else 0

            if overlap_pct > 50:  # Overlap significativo
                overlaps[table_name] = {
                    "overlap_count": len(overlap),
                    "overlap_pct": overlap_pct,
                    "total_rows": len(rows),
                }

                print(f"v {table_name}")
                print(
                    f"  Overlap: {len(overlap)}/{len(player_ids)} ({overlap_pct:.1f}%)"
                )
                print(f"  Total rows: {len(rows)}")
                print()

    return overlaps


def generate_report(all_findings: Dict) -> str:
    """Gera relatório markdown final"""

    report = f"""
# RELATORIO DE INVESTIGACAO: NOMES DOS JOGADORES

## Resumo da Analise

**Total de tabelas analisadas:** {all_findings['step1']['total_tables']}
**Tabelas relacionadas a nomes:** {len(all_findings['step1']['name_related'])}
**Tabelas relacionadas a players:** {len(all_findings['step1']['player_related'])}

---

## CENARIO IDENTIFICADO

"""

    # Decision tree
    if all_findings["step2"]:  # Encontrou lookup tables
        report += """
### CENARIO A: Lookup Table Encontrada

**Status:** Tabela de mapeamento ID -> String identificada

**Tabelas encontradas:**
"""
        for table_name, info in all_findings["step2"].items():
            report += f"\n- `{table_name}` ({len(info['columns'])} colunas)\n"
            report += f"  - Colunas: {', '.join(info['columns'][:5])}\n"
            report += f"  - Sample: {info['sample_row']}\n"

        report += """
**Proximos passos:**
1. Implementar JOIN entre `players` e lookup table
2. Mapear firstnameid/lastnameid -> strings
3. Atualizar Player model com computed property
4. Re-importar dados

**Tempo estimado:** 15 minutos
"""

    elif all_findings["step3"]:  # Encontrou strings em outras tabelas
        report += """
### CENARIO B: Nomes em Tabela Alternativa

**Status:** Nomes encontrados como strings em outras tabelas player

**Tabelas com nomes:**
"""
        for table_name, info in all_findings["step3"].items():
            report += f"\n- `{table_name}`\n"
            report += f"  - Name fields: {', '.join(info['name_fields'])}\n"
            report += f"  - Sample: {info['sample']}\n"

        report += """
**Proximos passos:**
1. Trocar source table no import
2. Usar tabela com nomes diretamente
3. Atualizar PlayerInfo model
4. Re-importar dados

**Tempo estimado:** 10 minutos
"""

    else:  # Nenhum encontrado
        report += """
### CENARIO C: Nomes Nao Encontrados no JSON

**Status:** Nomes reais nao estao no parser output

**Possiveis causas:**
- Nomes estao apenas nos XMLs metadata do parser
- Parser nao extraiu tabelas de nomes
- FC26 usa sistema diferente do FIFA 21

**Opcoes:**
1. **Aceitar fallback:** Usar "Player #ID" temporariamente
2. **Investigar XMLs:** Buscar nomes nos arquivos `parser/xml/21/`
3. **Melhorar parser:** Adicionar extracao de lookup tables

**Tempo estimado:** 
- Opcao 1: 5 minutos (immediate)
- Opcao 2-3: 30+ minutos (investigacao)
"""

    report += """
---

## Dados Coletados

### Step 1: Tabelas Escaneadas
"""
    for name, count in all_findings["step1"]["all_tables"][:20]:
        report += f"- `{name}` ({count} rows)\n"

    if all_findings["step4"]:
        report += "\n### Step 4: Career Tables Relevantes\n"
        for table_name, fields in all_findings["step4"].items():
            report += f"- `{table_name}`: {', '.join(fields)}\n"

    if all_findings["step5"]:
        report += "\n### Step 5: Overlap Analysis\n"
        for table_name, info in all_findings["step5"].items():
            report += f"- `{table_name}`: {info['overlap_pct']:.1f}% overlap ({info['overlap_count']} players)\n"

    report += """
---

## Conclusao

Execute os proximos passos recomendados acima para resolver o bloqueador de nomes.
"""

    return report


def main():
    """Main execution"""
    print(f"\n")
    print("=" * 60)
    print("  FC26 CAREER ANALYZER - INVESTIGACAO DE NOMES")
    print("=" * 60)
    print(f"\n")

    try:
        # Load data
        data = load_parser_output()

        # Execute investigation steps
        all_findings = {}

        all_findings["step1"] = step1_scan_tables(data)
        all_findings["step2"] = step2_inspect_name_tables(
            data, all_findings["step1"]["name_related"]
        )
        all_findings["step3"] = step3_search_name_strings(data)
        all_findings["step4"] = step4_check_career_tables(data)
        all_findings["step5"] = step5_analyze_overlap(data)

        # Generate report
        report = generate_report(all_findings)

        # Save report
        report_path = Path("docs/investigation_report.md")
        report_path.parent.mkdir(exist_ok=True)
        report_path.write_text(report, encoding="utf-8")

        print(f"\n")
        print("=" * 60)
        print("  INVESTIGACAO CONCLUIDA")
        print("=" * 60)
        print(f"")
        print(f"\nRelatorio salvo em: docs/investigation_report.md\n")

        # Print quick summary
        if all_findings["step2"]:
            print(f"CENARIO A: Lookup table encontrada!")
        elif all_findings["step3"]:
            print(f"CENARIO B: Nomes em tabela alternativa!")
        else:
            print(f"CENARIO C: Nomes nao encontrados")

        print(f"\nLeia o relatorio completo para proximos passos\n")

    except Exception as e:
        print(f"\nERROR: {e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
