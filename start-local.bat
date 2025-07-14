@echo off
echo === Sistema de Reservas de Hotel - Windows ===

echo Verificando MongoDB...
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo MongoDB está ejecutándose
) else (
    echo MongoDB no está ejecutándose
    echo Inicia MongoDB manualmente antes de continuar
    pause
    exit /b 1
)

echo Configurando variables de entorno...
copy backend\.env.local backend\.env
copy frontend\.env.local frontend\.env

echo Iniciando backend...
cd backend
start "Backend" python run_local.py

echo Esperando a que el backend inicie...
timeout /t 5 /nobreak

echo Iniciando frontend...
cd ..\frontend
start "Frontend" yarn start

echo.
echo === Sistema Iniciado ===
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8001
echo Documentación: http://localhost:8001/docs
echo.
echo Presiona cualquier tecla para continuar...
pause