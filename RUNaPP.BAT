@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ==========================================
REM Vacay Marketplace MVP Launcher
REM No fixed port (Streamlit chooses automatically)
REM ==========================================

REM اجعل مسار التشغيل هو مسار هذا الملف
cd /d "%~dp0"

echo ==========================================
echo   Vacay Marketplace MVP
echo   Project Path:
echo   %cd%
echo ==========================================
echo.

REM تأكد أن app.py موجود
if not exist "app.py" (
    echo [ERROR] app.py غير موجود في هذا المجلد
    echo.
    pause
    exit /b 1
)

REM تأكد أن Python متاح
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python غير مثبت أو غير مضاف للـ PATH
    echo.
    pause
    exit /b 1
)

REM تأكد أن Streamlit مثبت
python -m streamlit --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Streamlit غير مثبت - جاري التثبيت...
    python -m pip install --upgrade streamlit
    if errorlevel 1 (
        echo [ERROR] فشل تثبيت Streamlit
        pause
        exit /b 1
    )
)

echo.
echo [INFO] تشغيل التطبيق...
echo [INFO] لو المتصفح ما فتحش تلقائيًا، انسخ Local URL من النافذة.
echo.

REM ملاحظة: headless=false يساعد Streamlit يفتح المتصفح تلقائيًا (إن أمكن)
python -m streamlit run app.py --server.headless=false

echo.
echo [INFO] تم إغلاق التطبيق
pause
endlocal
