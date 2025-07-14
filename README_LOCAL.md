# Sistema de Reservas de Hotel - Configuración Local

Este documento explica cómo configurar y ejecutar el sistema de reservas de hotel en tu computadora local.

## 📋 Prerrequisitos

### 1. Python 3.8+
```bash
# Verificar versión de Python
python --version

# Si no tienes Python, instálalo desde:
# https://www.python.org/downloads/
```

### 2. Node.js 16+
```bash
# Verificar versión de Node.js
node --version

# Si no tienes Node.js, instálalo desde:
# https://nodejs.org/
```

### 3. Yarn
```bash
# Instalar Yarn
npm install -g yarn

# Verificar instalación
yarn --version
```

### 4. MongoDB
#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

#### macOS:
```bash
brew install mongodb-community
brew services start mongodb-community
```

#### Windows:
Descarga desde: https://www.mongodb.com/try/download/community

## 🚀 Configuración e Instalación

### Método 1: Configuración Automática (Recomendado)
```bash
# Ejecutar script de configuración
./setup-local.sh
```

### Método 2: Configuración Manual

#### Paso 1: Configurar Backend
```bash
cd backend

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.local .env
```

#### Paso 2: Configurar Frontend
```bash
cd frontend

# Instalar dependencias
yarn install

# Configurar variables de entorno
cp .env.local .env
```

## 🏃‍♂️ Ejecutar el Sistema

### Método 1: Ejecutar Backend con Script
```bash
cd backend
python run_local.py
```

### Método 2: Ejecutar Backend Manualmente
```bash
cd backend
python server.py
```

### Ejecutar Frontend
```bash
# En otra terminal
cd frontend
yarn start
```

## 🌐 Acceder al Sistema

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **Documentación API**: http://localhost:8001/docs

## 🛠️ Estructura del Proyecto

```
hotel-reservation-system/
├── backend/
│   ├── server.py          # Servidor FastAPI
│   ├── requirements.txt   # Dependencias Python
│   ├── .env.local         # Variables de entorno locales
│   └── run_local.py       # Script de ejecución local
├── frontend/
│   ├── src/
│   │   ├── App.js         # Componente principal
│   │   └── App.css        # Estilos
│   ├── package.json       # Dependencias Node.js
│   └── .env.local         # Variables de entorno locales
└── setup-local.sh         # Script de configuración automática
```

## 🗄️ Base de Datos

El sistema utiliza MongoDB con la siguiente estructura:

### Colecciones:
- `workers`: Trabajadores del hotel (autenticación)
- `clients`: Clientes registrados
- `rooms`: Habitaciones del hotel
- `reservations`: Reservas realizadas

### Datos por Defecto:
Al registrar un trabajador, se crean automáticamente 3 habitaciones:
- Habitación 101 - Simple - $50/noche
- Habitación 201 - Doble - $80/noche  
- Habitación 301 - Suite - $150/noche

## 🔧 Configuración Avanzada

### Variables de Entorno Backend (.env)
```
MONGO_URL=mongodb://localhost:27017
JWT_SECRET=hotel-secret-key-local-2025
```

### Variables de Entorno Frontend (.env)
```
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=3000
```

## 🎯 Funcionalidades del Sistema

### 👤 Trabajadores
- ✅ Registro de trabajadores
- ✅ Inicio de sesión con JWT
- ✅ Gestión por hotel

### 👥 Clientes
- ✅ Registro de clientes
- ✅ Información completa (nombre, email, teléfono, ID)
- ✅ Lista de clientes por hotel

### 🏨 Habitaciones
- ✅ Gestión de habitaciones
- ✅ Seguimiento de disponibilidad
- ✅ Precios por tipo

### 📅 Reservas
- ✅ Crear reservas
- ✅ Cálculo automático de precios
- ✅ Gestión de disponibilidad
- ✅ Cancelación de reservas

### 📊 Dashboard
- ✅ Estadísticas en tiempo real
- ✅ Resumen de reservas
- ✅ Métricas del hotel

## 🔍 Solución de Problemas

### Error de MongoDB
```bash
# Verificar que MongoDB esté corriendo
sudo systemctl status mongodb

# Reiniciar MongoDB
sudo systemctl restart mongodb
```

### Error de Dependencias
```bash
# Reinstalar dependencias del backend
cd backend
pip install -r requirements.txt

# Reinstalar dependencias del frontend
cd frontend
yarn install
```

### Error de Puertos
- Backend: Asegúrate de que el puerto 8001 esté libre
- Frontend: Asegúrate de que el puerto 3000 esté libre

## 🚀 Comandos Útiles

```bash
# Verificar estado de MongoDB
sudo systemctl status mongodb

# Ver logs del backend
tail -f backend/server.log

# Limpiar caché del frontend
yarn cache clean

# Construir para producción
yarn build
```

## 📞 Soporte

Si tienes problemas con la configuración local:

1. Verifica que todos los prerrequisitos estén instalados
2. Asegúrate de que MongoDB esté ejecutándose
3. Revisa los logs de error en la consola
4. Verifica que los puertos 3000 y 8001 estén libres

## 🎉 ¡Listo para Usar!

Una vez configurado, puedes:

1. Registrar trabajadores del hotel
2. Iniciar sesión con sus credenciales
3. Registrar clientes
4. Crear reservas
5. Gestionar el hotel desde el dashboard

¡Disfruta usando el sistema de reservas de hotel!