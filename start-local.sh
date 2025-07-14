#!/bin/bash

# Script para ejecutar el sistema completo en local

echo "=== Iniciando Sistema de Reservas de Hotel (Local) ==="

# Función para verificar si un puerto está en uso
check_port() {
    local port=$1
    if lsof -ti:$port > /dev/null 2>&1; then
        return 0  # Puerto en uso
    else
        return 1  # Puerto libre
    fi
}

# Verificar MongoDB
echo "Verificando MongoDB..."
if ! pgrep mongod > /dev/null; then
    echo "❌ MongoDB no está ejecutándose"
    echo "Iniciando MongoDB..."
    
    # Intentar iniciar MongoDB
    if command -v systemctl > /dev/null; then
        sudo systemctl start mongodb
    elif command -v brew > /dev/null; then
        brew services start mongodb-community
    else
        echo "Inicia MongoDB manualmente"
        exit 1
    fi
    
    # Esperar a que MongoDB inicie
    sleep 3
fi

if pgrep mongod > /dev/null; then
    echo "✅ MongoDB está ejecutándose"
else
    echo "❌ No se pudo iniciar MongoDB"
    exit 1
fi

# Verificar puertos
if check_port 8001; then
    echo "❌ Puerto 8001 está en uso"
    echo "Mata el proceso en puerto 8001 y vuelve a intentar"
    exit 1
fi

if check_port 3000; then
    echo "❌ Puerto 3000 está en uso"
    echo "Mata el proceso en puerto 3000 y vuelve a intentar"
    exit 1
fi

# Configurar variables de entorno
cp backend/.env.local backend/.env
cp frontend/.env.local frontend/.env

echo "✅ Variables de entorno configuradas"

# Crear función para manejar la terminación
cleanup() {
    echo ""
    echo "🛑 Deteniendo servicios..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Registrar manejador de señales
trap cleanup SIGINT SIGTERM

# Iniciar backend
echo "🚀 Iniciando backend en puerto 8001..."
cd backend
python run_local.py &
BACKEND_PID=$!

# Esperar a que el backend inicie
sleep 5

# Iniciar frontend
echo "🚀 Iniciando frontend en puerto 3000..."
cd ../frontend
yarn start &
FRONTEND_PID=$!

# Mostrar información
echo ""
echo "=== Sistema de Reservas de Hotel Iniciado ==="
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8001"
echo "📖 Documentación API: http://localhost:8001/docs"
echo ""
echo "Presiona Ctrl+C para detener el sistema"

# Mantener el script corriendo
wait