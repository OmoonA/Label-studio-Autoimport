@echo off
echo ============================
echo 📦 Autoexport 실행 시작!
echo ============================
python autoexport.py

if %ERRORLEVEL% NEQ 0 (
    echo ❌ autoexport.py 실행 중 오류 발생!
    pause
    exit /b %ERRORLEVEL%
)

echo ============================
echo 📦 End_export 실행 시작!
echo ============================
python end_export.py

if %ERRORLEVEL% NEQ 0 (
    echo ❌ end_export.py 실행 중 오류 발생!
    pause
    exit /b %ERRORLEVEL%
)

echo ============================
echo 🎉 모든 작업 완료!
echo ============================
pause
