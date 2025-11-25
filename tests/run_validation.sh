#!/bin/bash

echo "============================================"
echo "FC26 Career Analyzer - Quick Validation"
echo "============================================"
echo ""

echo "[1/4] Running pytest..."
python -m pytest tests/test_llm_integration.py -v --cov=src --cov-report=term
if [ $? -ne 0 ]; then
    echo "ERROR: Pytest failed!"
    exit 1
fi
echo ""

echo "[2/4] Testing SQL query..."
fc26-analyzer query "quantos jogadores?"
if [ $? -ne 0 ]; then
    echo "ERROR: SQL query failed!"
    exit 1
fi
echo ""

echo "[3/4] Testing Gemini query..."
fc26-analyzer query "análise do elenco"
if [ $? -ne 0 ]; then
    echo "WARNING: Gemini query failed (check API key)"
fi
echo ""

echo "[4/4] Checking documentation..."
if [ ! -f "README.md" ]; then
    echo "ERROR: README.md not found!"
    exit 1
fi
if [ ! -f "docs/SPRINT2_COMPLETE.md" ]; then
    echo "ERROR: SPRINT2_COMPLETE.md not found!"
    exit 1
fi
echo ""

echo "============================================"
echo "VALIDATION COMPLETE!"
echo "============================================"
echo "Check docs/VALIDATION_REPORT.md for details"
