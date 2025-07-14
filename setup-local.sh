#!/bin/bash

# Configuración Local para Sistema de Reservas de Hotel

echo "=== Configuración Local del Sistema de Reservas de Hotel ==="

# Verificar si MongoDB está ejecutándose
echo "Verificando MongoDB..."
if pgrep mongod > /dev/null; then
    echo "✅ MongoDB está ejecutándose"
else
    echo "❌ MongoDB no está ejecutándose"
    echo "Para instalar MongoDB en Ubuntu/Debian:"
    echo "sudo apt update"
    echo "sudo apt install mongodb"
    echo "sudo systemctl start mongodb"
    echo "sudo systemctl enable mongodb"
    echo ""
    echo "Para instalar MongoDB en macOS:"
    echo "brew install mongodb-community"
    echo "brew services start mongodb-community"
    echo ""
    echo "Para instalar MongoDB en Windows:"
    echo "Descarga desde: https://www.mongodb.com/try/download/community"
    echo ""
    exit 1
fi

# Configurar variables de entorno
echo "Configurando variables de entorno locales..."
cp backend/.env.local backend/.env
cp frontend/.env.local frontend/.env

echo "✅ Variables de entorno configuradas para ejecución local"

# Instalar dependencias del backend
echo "Instalando dependencias del backend..."
cd backend
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Dependencias del backend instaladas"
else
    echo "❌ No se encontró requirements.txt"
    exit 1
fi

# Instalar dependencias del frontend
echo "Instalando dependencias del frontend..."
cd ../frontend
if [ -f "package.json" ]; then
    yarn install
    echo "✅ Dependencias del frontend instaladas"
else
    echo "❌ No se encontró package.json"
    exit 1
fi

echo ""
echo "=== Configuración Completada ==="
echo "Para ejecutar el sistema:"
echo ""
echo "1. Iniciar el backend:"
echo "   cd backend"
echo "   python server.py"
echo ""
echo "2. En otra terminal, iniciar el frontend:"
echo "   cd frontend"
echo "   yarn start"
echo ""
echo "3. Abrir en navegador:"
echo "   http://localhost:3000"
echo ""
echo "El backend estará disponible en: http://localhost:8001"
echo "El frontend estará disponible en: http://localhost:3000"