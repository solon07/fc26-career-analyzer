@echo off
echo ============================================
echo FC26 Career Analyzer - Quick Validation
echo ============================================
echo.

echo [1/4] Running pytest...
python -m pytest tests/test_llm_integration.py -v --cov=src --cov-report=term
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Pytest failed!
    pause
    exit /b 1
)
echo.

echo [2/4] Testing SQL query...
fc26-analyzer query "quantos jogadores?"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: SQL query failed!
    pause
    exit /b 1
)
echo.

echo [3/4] Testing Gemini query...
fc26-analyzer query "análise do elenco"
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Gemini query failed (check API key)
)
echo.

echo [4/4] Checking documentation...
if not exist "README.md" (
    echo ERROR: README.md not found!
    exit /b 1
)
if not exist "docs\SPRINT2_COMPLETE.md" (
    echo ERROR: SPRINT2_COMPLETE.md not found!
    exit /b 1
)
echo.

echo ============================================
echo VALIDATION COMPLETE!
echo ============================================
echo Check docs/VALIDATION_REPORT.md for details
pause
